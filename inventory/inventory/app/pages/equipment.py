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
    """Display the equipment management page"""
    st.title("Equipment Management")
    
    # Create tabs for different equipment views
    tab1, tab2, tab3 = st.tabs([
        "All Equipment", 
        "Add Equipment",
        "Checkout/Return"
    ])
    
    with tab1:
        show_equipment_list()
    
    with tab2:
        if st.session_state.user_role == "admin":
            add_equipment_form()
        else:
            st.warning("You don't have permission to add equipment. Please contact an administrator.")
    
    with tab3:
        equipment_checkout_return()

def show_equipment_list():
    """Display a list of all equipment"""
    equipment_df = get_equipment()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=list(EQUIPMENT_STATUS.values()),
            default=[]
        )
    
    with col2:
        if not equipment_df.empty and "category" in equipment_df.columns:
            categories = equipment_df["category"].dropna().unique().tolist()
            category_filter = st.multiselect(
                "Filter by Category",
                options=categories,
                default=[]
            )
        else:
            category_filter = []
    
    with col3:
        search_term = st.text_input("Search Equipment", "")
    
    # Apply filters
    filtered_df = equipment_df.copy()
    
    if status_filter:
        filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df["category"].isin(category_filter)]
    
    if search_term:
        search_mask = (
            filtered_df["name"].str.contains(search_term, case=False, na=False) |
            filtered_df["description"].str.contains(search_term, case=False, na=False) |
            filtered_df["sku"].str.contains(search_term, case=False, na=False) |
            filtered_df["manufacturer"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Display the filtered equipment
    if not filtered_df.empty:
        # First, initialize session state for selected row if not exists
        if "selected_equipment_row" not in st.session_state:
            st.session_state.selected_equipment_row = None
        
        # Create a specialized dataframe for display
        display_df = filtered_df.copy()
        
        # Add a selection column that will contain checkboxes
        display_df = display_df.reset_index(drop=True)  # Reset index for clean display
        
        # Create a checkbox column
        display_df["Select"] = [
            "✓" if sku == st.session_state.selected_equipment_row else "" 
            for sku in display_df["sku"]
        ]
        
        # Choose columns to display and their order
        display_cols = ["Select", "sku", "name", "category", "status", "checked_out_by"]
        
        # Create clickable data frame
        st.write("Select an item from the equipment list:")
        clicked = st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
        
        # Create a list of buttons below the table for easier selection
        st.write("Or click an item below:")
        
        # Create 4 columns for the buttons
        cols = st.columns(4)
        
        # Add a button for each equipment item
        for i, (idx, row) in enumerate(filtered_df.iterrows()):
            sku = row["sku"]
            col_idx = i % 4
            
            # Determine button style based on selection
            button_type = "primary" if sku == st.session_state.selected_equipment_row else "secondary"
            
            # Add the button to the appropriate column
            if cols[col_idx].button(sku, key=f"btn_{sku}", type=button_type):
                st.session_state.selected_equipment_row = sku
                st.rerun()
        
        # Show view details button if a row is selected
        if st.session_state.selected_equipment_row:
            sku = st.session_state.selected_equipment_row
            st.write(f"Selected: {sku} - {filtered_df[filtered_df['sku'] == sku]['name'].values[0]}")
            
            if st.button("View Details", type="primary"):
                # Store selected SKU in session state
                st.session_state.selected_equipment_sku = sku
                # Set flag to show equipment details page
                st.session_state.show_equipment_details = True
                st.rerun()
    else:
        st.info("No equipment found matching the current filters.")

def show_equipment_details():
    """Display details for a selected piece of equipment"""
    if "selected_equipment_sku" in st.session_state:
        sku = st.session_state.selected_equipment_sku
        equipment_df = get_equipment()
        
        equipment = equipment_df[equipment_df["sku"] == sku]
        
        if not equipment.empty:
            equipment = equipment.iloc[0]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display equipment image if available
                if pd.notna(equipment["image_path"]) and os.path.exists(equipment["image_path"]):
                    image = Image.open(equipment["image_path"])
                    st.image(image, width=300)
                else:
                    st.image("https://via.placeholder.com/300x200?text=No+Image", width=300)
                
                # Display QR code
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
                st.subheader(equipment["name"])
                
                # Equipment details
                details_cols = ["sku", "description", "category", "manufacturer", 
                                "model", "serial_number", "purchase_date", 
                                "purchase_price", "status"]
                
                for col in details_cols:
                    if pd.notna(equipment[col]):
                        st.write(f"**{col.replace('_', ' ').title()}**: {equipment[col]}")
                
                # Checkout status
                if equipment["status"] == EQUIPMENT_STATUS["checked_out"]:
                    st.write("---")
                    st.write(f"**Checked Out By**: {equipment['checked_out_by']}")
                    st.write(f"**Checkout Date**: {equipment['checkout_date']}")
                    st.write(f"**Due Date**: {equipment['due_date']}")
                
                # Edit button for admins
                if st.session_state.user_role == "admin":
                    if st.button("Edit Equipment"):
                        st.session_state.edit_equipment_sku = sku
                        st.rerun()
            
            # Display checkout history
            st.subheader("Checkout History")
            history_df = get_checkout_history()
            item_history = history_df[history_df["sku"] == sku].sort_values(by="checkout_date", ascending=False)
            
            if not item_history.empty:
                st.dataframe(item_history[["user", "checkout_date", "due_date", "return_date", "notes"]], use_container_width=True)
            else:
                st.info("No checkout history for this item.")
            
            # Equipment edit form
            if "edit_equipment_sku" in st.session_state and st.session_state.edit_equipment_sku == sku:
                with st.form(key="edit_equipment_form"):
                    st.subheader("Edit Equipment")
                    
                    name = st.text_input("Name", value=equipment["name"])
                    description = st.text_area("Description", value=equipment["description"] if pd.notna(equipment["description"]) else "")
                    category = st.text_input("Category", value=equipment["category"] if pd.notna(equipment["category"]) else "")
                    manufacturer = st.text_input("Manufacturer", value=equipment["manufacturer"] if pd.notna(equipment["manufacturer"]) else "")
                    model = st.text_input("Model", value=equipment["model"] if pd.notna(equipment["model"]) else "")
                    serial_number = st.text_input("Serial Number", value=equipment["serial_number"] if pd.notna(equipment["serial_number"]) else "")
                    purchase_date = st.date_input("Purchase Date", value=pd.to_datetime(equipment["purchase_date"]) if pd.notna(equipment["purchase_date"]) else datetime.datetime.now())
                    purchase_price = st.number_input("Purchase Price", value=float(equipment["purchase_price"]) if pd.notna(equipment["purchase_price"]) else 0.0, min_value=0.0)
                    location = st.text_input("Location", value=equipment["location"] if pd.notna(equipment["location"]) else "")
                    
                    # Status can only be changed if item is not checked out
                    if equipment["status"] != EQUIPMENT_STATUS["checked_out"]:
                        status = st.selectbox("Status", options=list(EQUIPMENT_STATUS.values()), index=list(EQUIPMENT_STATUS.values()).index(equipment["status"]))
                    else:
                        status = equipment["status"]
                        st.info(f"Status is locked to '{status}' because the item is currently checked out.")
                    
                    # Image upload
                    uploaded_file = st.file_uploader("Upload a new image", type=["jpg", "jpeg", "png"])
                    
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
                        
                        # Clear the edit flag
                        del st.session_state.edit_equipment_sku
                        
                        st.success("Equipment updated successfully!")
                        st.rerun()
        else:
            st.info("Select an equipment item from the 'All Equipment' tab to view details.")
    else:
        st.info("Select an equipment item from the 'All Equipment' tab to view details.")

def add_equipment_form():
    """Form for adding new equipment"""
    with st.form(key="add_equipment_form"):
        st.subheader("Add New Equipment")
        
        # Generate a new SKU
        new_sku = generate_sku()
        st.write(f"New SKU: {new_sku}")
        
        name = st.text_input("Name", placeholder="Enter equipment name")
        description = st.text_area("Description", placeholder="Enter equipment description")
        category = st.text_input("Category", placeholder="Enter equipment category")
        manufacturer = st.text_input("Manufacturer", placeholder="Enter manufacturer")
        model = st.text_input("Model", placeholder="Enter model number")
        serial_number = st.text_input("Serial Number", placeholder="Enter serial number")
        purchase_date = st.date_input("Purchase Date", value=datetime.datetime.now())
        purchase_price = st.number_input("Purchase Price", min_value=0.0, step=0.01)
        status = st.selectbox("Status", options=list(EQUIPMENT_STATUS.values()))
        location = st.text_input("Location", placeholder="Enter storage location")
        
        # Image upload
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button(label="Add Equipment")
        
        if submit_button:
            # Process the form data
            if name:
                # Process uploaded image if provided
                image_path = None
                if uploaded_file is not None:
                    # Create a unique filename
                    image_filename = f"{new_sku}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    image_path = os.path.join(IMAGES_DIR, image_filename)
                    
                    # Open the uploaded image
                    image = Image.open(uploaded_file)
                    
                    # Save the image
                    image.save(image_path)
                
                # Add the new equipment to the DataFrame
                equipment_df = get_equipment()
                
                new_row = {
                    "sku": new_sku,
                    "name": name,
                    "description": description,
                    "category": category,
                    "manufacturer": manufacturer,
                    "model": model,
                    "serial_number": serial_number,
                    "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                    "purchase_price": purchase_price,
                    "status": status,
                    "checked_out_by": None,
                    "checkout_date": None,
                    "due_date": None,
                    "location": location,
                    "image_path": image_path,
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat()
                }
                
                # Append the new row
                equipment_df = pd.concat([equipment_df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Save the updated DataFrame
                save_equipment(equipment_df)
                
                # Generate QR code for the new equipment
                generate_qr_code(new_sku)
                
                st.success(f"Equipment '{name}' added successfully with SKU {new_sku}!")
                st.info("QR code has been generated for this equipment.")
                
                # Store SKU and navigate to details
                st.session_state.selected_equipment_sku = new_sku
                st.session_state.show_equipment_details = True
                st.rerun()
            else:
                st.error("Equipment name is required.")

def equipment_checkout_return():
    """Form for checking out or returning equipment"""
    equipment_df = get_equipment()
    
    # Only show if there's equipment to checkout
    if equipment_df.empty:
        st.info("No equipment available in the inventory.")
        return
    
    tab1, tab2 = st.tabs(["Checkout Equipment", "Return Equipment"])
    
    with tab1:
        st.subheader("Checkout Equipment")
        
        # QR scanner option
        use_qr = st.checkbox("Use QR Scanner")
        
        if use_qr:
            st.write("Scan the QR code on the equipment.")
            # This would be replaced with actual QR scanning
            st.write("QR scanner placeholder - in real implementation, use camera input")
            sku = st.text_input("Or enter SKU manually")
        else:
            # Filter to only show equipment that's in stock
            available_equipment = equipment_df[equipment_df["status"] == EQUIPMENT_STATUS["in_stock"]]
            
            if available_equipment.empty:
                st.warning("No equipment currently available for checkout.")
                return
            
            sku = st.selectbox(
                "Select Equipment",
                options=available_equipment["sku"].tolist(),
                format_func=lambda x: f"{x} - {available_equipment[available_equipment['sku'] == x]['name'].values[0]}"
            )
        
        if sku:
            # Get equipment details
            equipment = equipment_df[equipment_df["sku"] == sku]
            
            if not equipment.empty:
                equipment = equipment.iloc[0]
                
                # Only allow checkout if equipment is in stock
                if equipment["status"] == EQUIPMENT_STATUS["in_stock"]:
                    st.write(f"**Equipment**: {equipment['name']}")
                    st.write(f"**SKU**: {sku}")
                    
                    # Get user list for checkout
                    users_df = get_users()
                    
                    # Current user is the default
                    default_user_idx = users_df.index[users_df["username"] == st.session_state.username].tolist()[0] if st.session_state.username in users_df["username"].values else 0
                    
                    if st.session_state.user_role == "admin":
                        # Admins can check out equipment for any user
                        checkout_user = st.selectbox(
                            "Checkout For",
                            options=users_df["username"].tolist(),
                            index=default_user_idx
                        )
                    else:
                        # Regular users can only check out for themselves
                        checkout_user = st.session_state.username
                        st.write(f"**Checkout For**: {checkout_user}")
                    
                    # Set checkout duration
                    checkout_days = st.number_input("Checkout Duration (days)", min_value=1, max_value=180, value=DEFAULT_CHECKOUT_DAYS)
                    
                    checkout_date = datetime.datetime.now()
                    due_date = checkout_date + datetime.timedelta(days=checkout_days)
                    
                    st.write(f"**Checkout Date**: {checkout_date.strftime('%Y-%m-%d')}")
                    st.write(f"**Due Date**: {due_date.strftime('%Y-%m-%d')}")
                    
                    notes = st.text_area("Notes", placeholder="Optional notes for this checkout")
                    
                    if st.button("Checkout Equipment"):
                        # Update equipment status
                        equipment_df.loc[equipment_df["sku"] == sku, "status"] = EQUIPMENT_STATUS["checked_out"]
                        equipment_df.loc[equipment_df["sku"] == sku, "checked_out_by"] = checkout_user
                        equipment_df.loc[equipment_df["sku"] == sku, "checkout_date"] = checkout_date.strftime("%Y-%m-%d")
                        equipment_df.loc[equipment_df["sku"] == sku, "due_date"] = due_date.strftime("%Y-%m-%d")
                        equipment_df.loc[equipment_df["sku"] == sku, "updated_at"] = datetime.datetime.now().isoformat()
                        
                        # Save the updated equipment data
                        save_equipment(equipment_df)
                        
                        # Add to checkout history
                        history_df = get_checkout_history()
                        
                        new_history = {
                            "sku": sku,
                            "equipment_name": equipment["name"],
                            "user": checkout_user,
                            "checkout_date": checkout_date.strftime("%Y-%m-%d"),
                            "due_date": due_date.strftime("%Y-%m-%d"),
                            "return_date": None,
                            "notes": notes
                        }
                        
                        # Append the new history record
                        history_df = pd.concat([history_df, pd.DataFrame([new_history])], ignore_index=True)
                        
                        # Save the updated history
                        save_checkout_history(history_df)
                        
                        st.success(f"Equipment {equipment['name']} checked out successfully!")
                        st.rerun()
                else:
                    st.error(f"This equipment is currently {equipment['status']} and cannot be checked out.")
    
    with tab2:
        st.subheader("Return Equipment")
        
        # Filter to only show checked out equipment
        checked_out_equipment = equipment_df[equipment_df["status"] == EQUIPMENT_STATUS["checked_out"]]
        
        if checked_out_equipment.empty:
            st.info("No equipment is currently checked out.")
            return
        
        # If admin, show all checked out equipment, otherwise show only user's equipment
        if st.session_state.user_role == "admin":
            filtered_equipment = checked_out_equipment
        else:
            filtered_equipment = checked_out_equipment[checked_out_equipment["checked_out_by"] == st.session_state.username]
            
            if filtered_equipment.empty:
                st.info("You don't have any equipment checked out.")
                return
        
        return_sku = st.selectbox(
            "Select Equipment to Return",
            options=filtered_equipment["sku"].tolist(),
            format_func=lambda x: f"{x} - {filtered_equipment[filtered_equipment['sku'] == x]['name'].values[0]} (checked out by {filtered_equipment[filtered_equipment['sku'] == x]['checked_out_by'].values[0]})"
        )
        
        if return_sku:
            # Get equipment details
            equipment = filtered_equipment[filtered_equipment["sku"] == return_sku].iloc[0]
            
            st.write(f"**Equipment**: {equipment['name']}")
            st.write(f"**SKU**: {return_sku}")
            st.write(f"**Checked Out By**: {equipment['checked_out_by']}")
            st.write(f"**Checkout Date**: {equipment['checkout_date']}")
            st.write(f"**Due Date**: {equipment['due_date']}")
            
            return_condition = st.selectbox(
                "Condition Upon Return",
                options=["Good", "Needs Maintenance", "Damaged"]
            )
            
            return_notes = st.text_area("Return Notes", placeholder="Enter any notes about the condition")
            
            if st.button("Return Equipment"):
                # Update equipment status based on condition
                if return_condition == "Good":
                    new_status = EQUIPMENT_STATUS["in_stock"]
                elif return_condition == "Needs Maintenance":
                    new_status = EQUIPMENT_STATUS["maintenance"]
                else:  # Damaged
                    new_status = EQUIPMENT_STATUS["in_stock"]  # Still in stock but with damage noted
                
                # Update equipment status
                equipment_df.loc[equipment_df["sku"] == return_sku, "status"] = new_status
                equipment_df.loc[equipment_df["sku"] == return_sku, "checked_out_by"] = None
                equipment_df.loc[equipment_df["sku"] == return_sku, "checkout_date"] = None
                equipment_df.loc[equipment_df["sku"] == return_sku, "due_date"] = None
                equipment_df.loc[equipment_df["sku"] == return_sku, "updated_at"] = datetime.datetime.now().isoformat()
                
                # Save the updated equipment data
                save_equipment(equipment_df)
                
                # Update checkout history
                history_df = get_checkout_history()
                
                # Find the most recent checkout for this equipment without a return date
                checkout_idx = history_df[(history_df["sku"] == return_sku) & (history_df["return_date"].isna())].index.max()
                
                if pd.notna(checkout_idx):
                    # Update the return date and notes
                    history_df.loc[checkout_idx, "return_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    # Append return notes to existing notes
                    existing_notes = history_df.loc[checkout_idx, "notes"]
                    if pd.isna(existing_notes):
                        existing_notes = ""
                    
                    updated_notes = f"{existing_notes}\nReturn Condition: {return_condition}\nReturn Notes: {return_notes}".strip()
                    history_df.loc[checkout_idx, "notes"] = updated_notes
                    
                    # Save the updated history
                    save_checkout_history(history_df)
                
                st.success(f"Equipment {equipment['name']} returned successfully!")
                
                # If equipment needs maintenance, show an alert
                if return_condition in ["Needs Maintenance", "Damaged"]:
                    st.warning(f"This equipment has been marked as {return_condition}. Maintenance may be required.")
                
                st.rerun()