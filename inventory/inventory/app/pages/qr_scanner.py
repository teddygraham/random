import streamlit as st
import numpy as np
import pandas as pd
import datetime
from PIL import Image

from ...utils.database import (
    get_equipment, 
    save_equipment, 
    get_checkout_history, 
    save_checkout_history,
    get_users
)
from ...utils.qr_code import scan_qr_code_from_image
from ...utils.constants import EQUIPMENT_STATUS, DEFAULT_CHECKOUT_DAYS

def show():
    """Display the QR scanner page"""
    st.title("QR Scanner")
    
    st.write("Use this page to quickly check out or return equipment using QR codes.")
    
    # Option to use camera or upload image
    scan_option = st.radio(
        "Choose scan method:",
        ["Upload Image", "Use Camera"]
    )
    
    if scan_option == "Upload Image":
        uploaded_file = st.file_uploader("Upload QR code image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Read the image
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Display the image
            st.image(image, caption="Uploaded Image", width=300)
            
            # Process the QR code
            process_qr_code(image_array)
    
    else:  # Use Camera
        st.write("Camera integration would use streamlit-camera-input-live in a real implementation.")
        st.write("For this demo, we'll simulate camera input with an upload.")
        
        camera_file = st.file_uploader("Upload QR code image (camera simulation)", type=["jpg", "jpeg", "png"])
        
        if camera_file is not None:
            # Read the image
            image = Image.open(camera_file)
            image_array = np.array(image)
            
            # Display the image
            st.image(image, caption="Camera Image", width=300)
            
            # Process the QR code
            process_qr_code(image_array)

def process_qr_code(image_array):
    """Process a QR code from an image array"""
    # Scan the QR code
    sku = scan_qr_code_from_image(image_array)
    
    if sku:
        st.success(f"QR Code Detected: {sku}")
        
        equipment_df = get_equipment()
        
        # Check if the SKU exists
        if sku in equipment_df["sku"].values:
            equipment = equipment_df[equipment_df["sku"] == sku].iloc[0]
            
            st.write(f"**Equipment**: {equipment['name']}")
            st.write(f"**SKU**: {sku}")
            st.write(f"**Status**: {equipment['status']}")
            
            # Determine action based on status
            if equipment["status"] == EQUIPMENT_STATUS["checked_out"]:
                st.write("This equipment is currently checked out.")
                
                if st.button("Return Equipment"):
                    return_equipment(sku)
            
            elif equipment["status"] == EQUIPMENT_STATUS["in_stock"]:
                st.write("This equipment is available for checkout.")
                
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
                    checkout_equipment(sku, checkout_user, checkout_days, notes)
            
            else:
                st.warning(f"This equipment is currently {equipment['status']} and cannot be checked out or returned.")
        
        else:
            st.error(f"SKU '{sku}' not found in the inventory.")
    
    else:
        st.error("No QR code detected in the image.")

def checkout_equipment(sku, checkout_user, checkout_days, notes):
    """Check out equipment by SKU"""
    equipment_df = get_equipment()
    
    # Get equipment details
    equipment = equipment_df[equipment_df["sku"] == sku].iloc[0]
    
    # Only allow checkout if equipment is in stock
    if equipment["status"] == EQUIPMENT_STATUS["in_stock"]:
        checkout_date = datetime.datetime.now()
        due_date = checkout_date + datetime.timedelta(days=checkout_days)
        
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

def return_equipment(sku):
    """Return equipment by SKU"""
    equipment_df = get_equipment()
    
    # Get equipment details
    equipment = equipment_df[equipment_df["sku"] == sku].iloc[0]
    
    # Only allow return if equipment is checked out
    if equipment["status"] == EQUIPMENT_STATUS["checked_out"]:
        return_condition = st.selectbox(
            "Condition Upon Return",
            options=["Good", "Needs Maintenance", "Damaged"]
        )
        
        return_notes = st.text_area("Return Notes", placeholder="Enter any notes about the condition")
        
        if st.button("Confirm Return"):
            # Update equipment status based on condition
            if return_condition == "Good":
                new_status = EQUIPMENT_STATUS["in_stock"]
            elif return_condition == "Needs Maintenance":
                new_status = EQUIPMENT_STATUS["maintenance"]
            else:  # Damaged
                new_status = EQUIPMENT_STATUS["in_stock"]  # Still in stock but with damage noted
            
            # Update equipment status
            equipment_df.loc[equipment_df["sku"] == sku, "status"] = new_status
            equipment_df.loc[equipment_df["sku"] == sku, "checked_out_by"] = None
            equipment_df.loc[equipment_df["sku"] == sku, "checkout_date"] = None
            equipment_df.loc[equipment_df["sku"] == sku, "due_date"] = None
            equipment_df.loc[equipment_df["sku"] == sku, "updated_at"] = datetime.datetime.now().isoformat()
            
            # Save the updated equipment data
            save_equipment(equipment_df)
            
            # Update checkout history
            history_df = get_checkout_history()
            
            # Find the most recent checkout for this equipment without a return date
            checkout_idx = history_df[(history_df["sku"] == sku) & (history_df["return_date"].isna())].index.max()
            
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
    else:
        st.error(f"This equipment is currently {equipment['status']} and cannot be returned.")