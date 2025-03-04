import streamlit as st
import pandas as pd
import datetime

from ...utils.database import get_users, save_users, get_equipment, save_equipment
from ...utils.constants import ROLES
from ..auth import change_password, send_email

def show():
    """Display the users management page"""
    st.title("User Management")
    
    # Only admins can access user management
    if st.session_state.user_role != "admin":
        st.subheader("My Account")
        show_user_profile(st.session_state.username)
        return
    
    # Create tabs for different user views
    tab1, tab2, tab3 = st.tabs(["All Users", "Add User", "User Profile"])
    
    with tab1:
        show_user_list()
    
    with tab2:
        add_user_form()
    
    with tab3:
        if "selected_username" in st.session_state:
            show_user_profile(st.session_state.selected_username)
        else:
            st.info("Select a user from the 'All Users' tab to view their profile.")

def show_user_list():
    """Display a list of all users"""
    users_df = get_users()
    
    # Search filter
    search_term = st.text_input("Search Users", "")
    
    # Apply search filter
    if search_term:
        search_mask = (
            users_df["username"].str.contains(search_term, case=False, na=False) |
            users_df["name"].str.contains(search_term, case=False, na=False) |
            users_df["email"].str.contains(search_term, case=False, na=False) |
            users_df["department"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = users_df[search_mask]
    else:
        filtered_df = users_df
    
    # Display the filtered users
    if not filtered_df.empty:
        # First, initialize session state for selected row if not exists
        if "selected_user_row" not in st.session_state:
            st.session_state.selected_user_row = None
        
        # Create a specialized dataframe for display
        display_df = filtered_df.copy()
        
        # Add a selection column that will contain checkboxes
        display_df = display_df.reset_index(drop=True)  # Reset index for clean display
        
        # Create a checkbox column
        display_df["Select"] = [
            "✓" if username == st.session_state.selected_user_row else "" 
            for username in display_df["username"]
        ]
        
        # Choose columns to display and their order
        display_cols = ["Select", "username", "name", "email", "role", "department"]
        
        # Create clickable data frame
        st.write("Select a user from the list:")
        clicked = st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
        
        # Create a list of buttons below the table for easier selection
        st.write("Or click a user below:")
        
        # Create 4 columns for the buttons
        cols = st.columns(4)
        
        # Add a button for each user
        for i, (idx, row) in enumerate(filtered_df.iterrows()):
            username = row["username"]
            col_idx = i % 4
            
            # Determine button style based on selection
            button_type = "primary" if username == st.session_state.selected_user_row else "secondary"
            
            # Add the button to the appropriate column
            if cols[col_idx].button(username, key=f"btn_{username}", type=button_type):
                st.session_state.selected_user_row = username
                st.rerun()
        
        # Show action buttons if a row is selected
        if st.session_state.selected_user_row:
            username = st.session_state.selected_user_row
            st.write(f"Selected: {username} - {filtered_df[filtered_df['username'] == username]['name'].values[0]}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View Profile", type="primary"):
                    st.session_state.selected_username = username
                    st.rerun()
            
            with col2:
                if st.button("Delete User", type="secondary"):
                    st.session_state.confirm_delete_user = username
        
        # Confirm deletion
        if "confirm_delete_user" in st.session_state:
            username = st.session_state.confirm_delete_user
            st.warning(f"Are you sure you want to delete user '{username}'? This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Delete"):
                    delete_user(username)
                    del st.session_state.confirm_delete_user
                    if "selected_username" in st.session_state and st.session_state.selected_username == username:
                        del st.session_state.selected_username
                    st.rerun()
            
            with col2:
                if st.button("Cancel"):
                    del st.session_state.confirm_delete_user
                    st.rerun()
    else:
        st.info("No users found matching the search criteria.")

def show_user_profile(username):
    """Display profile for a selected user"""
    users_df = get_users()
    user = users_df[users_df["username"] == username]
    
    if not user.empty:
        user = user.iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"User: {user['name']}")
            st.write(f"**Username**: {user['username']}")
            st.write(f"**Email**: {user['email']}")
            st.write(f"**Role**: {user['role']}")
            st.write(f"**Department**: {user['department']}")
            st.write(f"**Account Created**: {user['created_at']}")
        
        with col2:
            # If admin viewing another user's profile
            if st.session_state.user_role == "admin" and username != st.session_state.username:
                if st.button("Edit User"):
                    st.session_state.edit_user = username
            
            # Self profile actions (available to all users for their own profile)
            if username == st.session_state.username:
                if st.button("Change Password"):
                    st.session_state.change_password = True
        
        # Show equipment checked out by user
        st.subheader("Checked Out Equipment")
        
        equipment_df = get_equipment()
        user_equipment = equipment_df[equipment_df["checked_out_by"] == username]
        
        if not user_equipment.empty:
            st.dataframe(user_equipment[["sku", "name", "checkout_date", "due_date"]], use_container_width=True)
            
            # Check for overdue items
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            overdue_items = user_equipment[user_equipment["due_date"] < today]
            
            if not overdue_items.empty:
                st.warning(f"This user has {len(overdue_items)} overdue item(s).")
                
                if st.button("Send Reminder Email"):
                    send_reminder_email(username, overdue_items)
        else:
            st.info("This user has no equipment checked out.")
        
        # Password change form
        if "change_password" in st.session_state and st.session_state.change_password:
            with st.form(key="change_password_form"):
                st.subheader("Change Password")
                
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                submit_button = st.form_submit_button(label="Change Password")
                
                if submit_button:
                    if new_password != confirm_password:
                        st.error("New passwords do not match.")
                    elif not current_password or not new_password:
                        st.error("All fields are required.")
                    else:
                        if change_password(username, current_password, new_password):
                            st.success("Password changed successfully!")
                            st.session_state.change_password = False
                            st.rerun()
                        else:
                            st.error("Current password is incorrect.")
        
        # User edit form
        if "edit_user" in st.session_state and st.session_state.edit_user == username:
            with st.form(key="edit_user_form"):
                st.subheader("Edit User")
                
                name = st.text_input("Name", value=user["name"])
                email = st.text_input("Email", value=user["email"])
                role = st.selectbox("Role", options=list(ROLES.keys()), 
                                    index=list(ROLES.keys()).index(user["role"]),
                                    format_func=lambda x: ROLES[x])
                department = st.text_input("Department", value=user["department"])
                
                # Reset password option
                reset_password = st.checkbox("Reset Password")
                new_password = ""
                if reset_password:
                    new_password = st.text_input("New Password", type="password")
                
                submit_button = st.form_submit_button(label="Update User")
                
                if submit_button:
                    if not email or not name:
                        st.error("Name and email are required.")
                    elif reset_password and not new_password:
                        st.error("New password is required when resetting password.")
                    else:
                        # Update the user in the DataFrame
                        users_df.loc[users_df["username"] == username, "name"] = name
                        users_df.loc[users_df["username"] == username, "email"] = email
                        users_df.loc[users_df["username"] == username, "role"] = role
                        users_df.loc[users_df["username"] == username, "department"] = department
                        
                        if reset_password:
                            users_df.loc[users_df["username"] == username, "password"] = new_password  # In production, use hashed passwords
                        
                        # Save the updated DataFrame
                        save_users(users_df)
                        
                        # Clear the edit flag
                        del st.session_state.edit_user
                        
                        st.success("User updated successfully!")
                        st.rerun()
    else:
        st.error(f"User '{username}' not found.")

def add_user_form():
    """Form for adding a new user"""
    with st.form(key="add_user_form"):
        st.subheader("Add New User")
        
        username = st.text_input("Username", placeholder="Enter username")
        name = st.text_input("Name", placeholder="Enter full name")
        email = st.text_input("Email", placeholder="Enter email address")
        role = st.selectbox("Role", options=list(ROLES.keys()), 
                            format_func=lambda x: ROLES[x])
        department = st.text_input("Department", placeholder="Enter department")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
        
        submit_button = st.form_submit_button(label="Add User")
        
        if submit_button:
            # Validate form inputs
            if not username or not name or not email or not password:
                st.error("All fields are required.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                users_df = get_users()
                
                # Check if username already exists
                if username in users_df["username"].values:
                    st.error(f"Username '{username}' already exists.")
                    return
                
                # Add the new user to the DataFrame
                new_user = {
                    "username": username,
                    "email": email,
                    "password": password,  # In production, use hashed passwords
                    "role": role,
                    "name": name,
                    "department": department,
                    "created_at": datetime.datetime.now().isoformat()
                }
                
                # Append the new user
                users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                
                # Save the updated DataFrame
                save_users(users_df)
                
                st.success(f"User '{username}' added successfully!")

def delete_user(username):
    """Delete a user from the system"""
    users_df = get_users()
    
    # Check for equipment currently checked out by the user
    equipment_df = get_equipment()
    user_equipment = equipment_df[equipment_df["checked_out_by"] == username]
    
    if not user_equipment.empty:
        # Mark all equipment as returned
        equipment_df.loc[equipment_df["checked_out_by"] == username, "status"] = "In Stock"
        equipment_df.loc[equipment_df["checked_out_by"] == username, "checked_out_by"] = None
        equipment_df.loc[equipment_df["checked_out_by"] == username, "checkout_date"] = None
        equipment_df.loc[equipment_df["checked_out_by"] == username, "due_date"] = None
        
        # Save the updated equipment data
        save_equipment(equipment_df)
    
    # Remove the user
    users_df = users_df[users_df["username"] != username]
    
    # Save the updated DataFrame
    save_users(users_df)
    
    st.success(f"User '{username}' deleted successfully!")

def send_reminder_email(username, overdue_items):
    """Send a reminder email to a user with overdue items"""
    users_df = get_users()
    user = users_df[users_df["username"] == username].iloc[0]
    user_email = user["email"]
    
    subject = "Reminder: Overdue Lab Equipment"
    
    body = f"Dear {user['name']},\n\n"
    body += "This is a reminder that you have the following overdue lab equipment:\n\n"
    
    for _, item in overdue_items.iterrows():
        body += f"- {item['name']} (SKU: {item['sku']})\n"
        body += f"  Due Date: {item['due_date']}\n"
    
    body += "\nPlease return these items as soon as possible.\n\n"
    body += "Thank you,\nLab Equipment Management System"
    
    send_email(user_email, subject, body)