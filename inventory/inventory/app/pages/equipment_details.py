import streamlit as st
import pandas as pd
import os
import datetime
from PIL import Image
import io

from ...utils.database import (
    get_equipment, 
    save_equipment, 
    get_checkout_history, 
    save_checkout_history, 
    generate_sku,
    get_users,
    IMAGES_DIR
)
from ...utils.constants import EQUIPMENT_STATUS, DEFAULT_CHECKOUT_DAYS, DELL_BLUE
from ...utils.qr_code import generate_qr_code
from ..auth import send_email

def show():
    """Display the equipment details page"""
    st.title("Equipment Details")
    
    # Check if an equipment SKU is provided in query parameters or session state
    if "selected_equipment_sku" in st.session_state:
        sku = st.session_state.selected_equipment_sku
        display_equipment_details(sku)
    else:
        # Show equipment selection if no SKU is provided
        st.info("Please select equipment from the Equipment Management page to view details.")
        
        # Option to manually enter SKU
        with st.form(key="sku_input_form"):
            manual_sku = st.text_input("Or enter SKU manually")
            submit = st.form_submit_button("View Details")
            
            if submit and manual_sku:
                st.session_state.selected_equipment_sku = manual_sku
                st.rerun()

def display_equipment_details(sku):
    """Display detailed information and edit form for a piece of equipment"""
    equipment_df = get_equipment()
    
    # Find the equipment with the given SKU
    equipment = equipment_df[equipment_df["sku"] == sku]
    
    if equipment.empty:
        st.error(f"No equipment found with SKU: {sku}")
        if st.button("Clear Selection"):
            if "selected_equipment_sku" in st.session_state:
                del st.session_state.selected_equipment_sku
            st.rerun()
        return
    
    # Get the equipment details
    equipment = equipment.iloc[0]
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Details", "Edit Equipment", "Checkout History"])
    
    # Tab 1: Equipment Details
    with tab1:
        display_equipment_info(equipment)
    
    # Tab 2: Edit Equipment (admin only)
    with tab2:
        if st.session_state.user_role == "admin":
            edit_equipment_form(equipment, equipment_df)
        else:
            st.warning("You don't have permission to edit equipment. Please contact an administrator.")
    
    # Tab 3: Checkout History
    with tab3:
        display_checkout_history(sku)
    
    # Button to go back to equipment list
    if st.button("Back to Equipment Management"):
        # Clear the details view flags but keep the selection
        st.session_state.show_equipment_details = False
        st.rerun()

def display_equipment_info(equipment):
    """Display detailed information for a piece of equipment"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display equipment image if available
        if pd.notna(equipment["image_path"]) and os.path.exists(equipment["image_path"]):
            image = Image.open(equipment["image_path"])
            st.image(image, width=300)
        else:
            st.image("https://via.placeholder.com/300x200?text=No+Image", width=300)
        
        # Display QR code
        sku = equipment["sku"]
        qr_path = os.path.join(IMAGES_DIR, f"qr_{sku}.png")
        if os.path.exists(qr_path):
            st.image(qr_path, width=200, caption=f"QR Code for {sku}")
        else:
            qr_path = generate_qr_code(sku)
            st.image(qr_path, width=200, caption=f"QR Code for {sku}")
        
        # Download QR code
        with open(qr_path, "rb") as file:
            qr_bytes = file.read()
            st.download_button(
                label="Download QR Code",
                data=qr_bytes,
                file_name=f"qr_{sku}.png",
                mime="image/png"
            )
    
    with col2:
        # Title with equipment name and SKU
        st.header(equipment["name"])
        st.subheader(f"SKU: {equipment['sku']}")
        
        # Equipment status with colored badge
        status = equipment["status"]
        status_color = {
            EQUIPMENT_STATUS["in_stock"]: "green",
            EQUIPMENT_STATUS["checked_out"]: "red",
            EQUIPMENT_STATUS["maintenance"]: "orange",
            EQUIPMENT_STATUS["lost"]: "gray"
        }.get(status, "blue")
        
        st.markdown(f"""
        <div style="background-color: {status_color}; color: white; padding: 5px 10px; 
        border-radius: 5px; display: inline-block; margin-bottom: 15px;">
        Status: {status}
        </div>
        """, unsafe_allow_html=True)
        
        # Equipment details in a clean format
        st.subheader("Specifications")
        details_cols = [
            ("Description", "description"),
            ("Category", "category"),
            ("Manufacturer", "manufacturer"),
            ("Model", "model"),
            ("Serial Number", "serial_number"),
            ("Purchase Date", "purchase_date"),
            ("Purchase Price", "purchase_price"),
            ("Location", "location")
        ]
        
        for label, col in details_cols:
            if pd.notna(equipment[col]):
                value = equipment[col]
                # Format price with currency symbol
                if col == "purchase_price":
                    value = f"${float(value):.2f}"
                st.markdown(f"**{label}:** {value}")
        
        # Checkout information if checked out
        if equipment["status"] == EQUIPMENT_STATUS["checked_out"]:
            st.subheader("Current Checkout")
            st.markdown(f"**Checked Out By:** {equipment['checked_out_by']}")
            st.markdown(f"**Checkout Date:** {equipment['checkout_date']}")
            st.markdown(f"**Due Date:** {equipment['due_date']}")
            
            # Calculate days overdue or remaining
            if pd.notna(equipment['due_date']):
                due_date = pd.to_datetime(equipment['due_date'])
                today = pd.to_datetime(datetime.datetime.now().date())
                days_diff = (due_date - today).days
                
                if days_diff < 0:
                    st.markdown(f"<div style='color: red; font-weight: bold;'>Overdue by {abs(days_diff)} days</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: green;'>{days_diff} days remaining</div>", unsafe_allow_html=True)

def edit_equipment_form(equipment, equipment_df):
    """Form for editing equipment details"""
    sku = equipment["sku"]
    
    with st.form(key="edit_equipment_form"):
        st.subheader("Edit Equipment Details")
        
        name = st.text_input("Name", value=equipment["name"])
        description = st.text_area("Description", value=equipment["description"] if pd.notna(equipment["description"]) else "")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.text_input("Category", value=equipment["category"] if pd.notna(equipment["category"]) else "")
            manufacturer = st.text_input("Manufacturer", value=equipment["manufacturer"] if pd.notna(equipment["manufacturer"]) else "")
            model = st.text_input("Model", value=equipment["model"] if pd.notna(equipment["model"]) else "")
        
        with col2:
            serial_number = st.text_input("Serial Number", value=equipment["serial_number"] if pd.notna(equipment["serial_number"]) else "")
            purchase_date = st.date_input("Purchase Date", value=pd.to_datetime(equipment["purchase_date"]) if pd.notna(equipment["purchase_date"]) else datetime.datetime.now())
            purchase_price = st.number_input("Purchase Price", value=float(equipment["purchase_price"]) if pd.notna(equipment["purchase_price"]) else 0.0, min_value=0.0, format="%.2f")
        
        location = st.text_input("Location", value=equipment["location"] if pd.notna(equipment["location"]) else "")
        
        # Status can only be changed if item is not checked out
        if equipment["status"] != EQUIPMENT_STATUS["checked_out"]:
            status = st.selectbox("Status", options=list(EQUIPMENT_STATUS.values()), index=list(EQUIPMENT_STATUS.values()).index(equipment["status"]))
        else:
            status = equipment["status"]
            st.info(f"Status is locked to '{status}' because the item is currently checked out.")
        
        # Image upload with preview
        st.subheader("Equipment Image")
        
        # Show current image if available
        if pd.notna(equipment["image_path"]) and os.path.exists(equipment["image_path"]):
            st.image(Image.open(equipment["image_path"]), width=200, caption="Current Image")
        
        uploaded_file = st.file_uploader("Upload a new image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Preview the new image
            st.image(Image.open(uploaded_file), width=200, caption="New Image Preview")
        
        submit_button = st.form_submit_button(label="Update Equipment")
        
        if submit_button:
            # Process uploaded image if provided
            if uploaded_file is not None:
                # Create a unique filename
                image_filename = f"{sku}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                image_path = os.path.join(IMAGES_DIR, image_filename)
                
                # Open the uploaded image
                image = Image.open(uploaded_file)
                
                # Save the image
                image.save(image_path)
            else:
                # Keep existing image
                image_path = equipment["image_path"] if pd.notna(equipment["image_path"]) else None
            
            # Update the equipment in the DataFrame
            equipment_df.loc[equipment_df["sku"] == sku, "name"] = name
            equipment_df.loc[equipment_df["sku"] == sku, "description"] = description
            equipment_df.loc[equipment_df["sku"] == sku, "category"] = category
            equipment_df.loc[equipment_df["sku"] == sku, "manufacturer"] = manufacturer
            equipment_df.loc[equipment_df["sku"] == sku, "model"] = model
            equipment_df.loc[equipment_df["sku"] == sku, "serial_number"] = serial_number
            equipment_df.loc[equipment_df["sku"] == sku, "purchase_date"] = purchase_date.strftime("%Y-%m-%d")
            equipment_df.loc[equipment_df["sku"] == sku, "purchase_price"] = purchase_price
            equipment_df.loc[equipment_df["sku"] == sku, "status"] = status
            equipment_df.loc[equipment_df["sku"] == sku, "location"] = location
            equipment_df.loc[equipment_df["sku"] == sku, "image_path"] = image_path
            equipment_df.loc[equipment_df["sku"] == sku, "updated_at"] = datetime.datetime.now().isoformat()
            
            # Save the updated DataFrame
            save_equipment(equipment_df)
            
            st.success("Equipment updated successfully!")
            st.session_state.show_success = True

def display_checkout_history(sku):
    """Display checkout history for a piece of equipment"""
    st.subheader("Checkout History")
    
    history_df = get_checkout_history()
    item_history = history_df[history_df["sku"] == sku].sort_values(by="checkout_date", ascending=False)
    
    if not item_history.empty:
        # Add a Status column
        item_history["status"] = item_history.apply(
            lambda x: "Returned" if pd.notna(x["return_date"]) else (
                "Overdue" if pd.to_datetime(x["due_date"]) < datetime.datetime.now().date() else "Checked Out"
            ),
            axis=1
        )
        
        # Display as a more readable table with colored status
        for _, row in item_history.iterrows():
            status = row["status"]
            status_color = {
                "Returned": "green",
                "Checked Out": "blue",
                "Overdue": "red"
            }.get(status, "gray")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**User:** {row['user']}")
                if pd.notna(row['notes']):
                    st.markdown(f"**Notes:** {row['notes']}")
            
            with col2:
                st.markdown(f"**Checkout:** {row['checkout_date']}")
                st.markdown(f"**Due Date:** {row['due_date']}")
                if pd.notna(row['return_date']):
                    st.markdown(f"**Returned:** {row['return_date']}")
            
            with col3:
                st.markdown(f"""
                <div style="background-color: {status_color}; color: white; padding: 5px 10px; 
                border-radius: 5px; text-align: center; margin-top: 5px;">
                {status}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("No checkout history for this item.")