import streamlit as st
import pandas as pd
import hashlib
import datetime
import smtplib
import sqlite3
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..utils.database import get_users, save_users, get_db_connection, hash_password
from ..utils.constants import DELL_BLUE, DELL_DARK, DELL_DARK_SECONDARY, ROLES
from ..utils.cookies.cookies import set_cookie, get_cookie, delete_cookie

# Cookie constants
AUTH_COOKIE_NAME = "inventory_auth"
AUTH_COOKIE_EXPIRY = 7  # days

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""
    if "login_error" not in st.session_state:
        st.session_state.login_error = ""
    
    # Attempt to get auth data from session state first
    if not st.session_state.authenticated:
        if "auth_data" in st.session_state and st.session_state.auth_data:
            try:
                # Parse auth data
                auth_data = json.loads(st.session_state.auth_data)
                
                if auth_data and "username" in auth_data and "role" in auth_data:
                    # Restore session
                    st.session_state.authenticated = True
                    st.session_state.username = auth_data["username"]
                    st.session_state.user_role = auth_data["role"]
                    return True
            except:
                # Invalid auth data, ignore it
                pass
    
    return st.session_state.authenticated

def set_auth_data(username, role):
    """Set authentication data in session state"""
    auth_data = {
        "username": username,
        "role": role
    }
    
    # Store auth data in session state
    st.session_state.auth_data = json.dumps(auth_data)
    
    # Also try to set in a cookie for persistence across refreshes
    try:
        set_cookie(
            AUTH_COOKIE_NAME,
            st.session_state.auth_data,
            expires_at=datetime.datetime.now() + datetime.timedelta(days=AUTH_COOKIE_EXPIRY)
        )
    except:
        # If setting cookie fails, still continue with session state auth
        pass

def delete_auth_data():
    """Delete the authentication data"""
    if "auth_data" in st.session_state:
        del st.session_state.auth_data
    
    try:
        delete_cookie(AUTH_COOKIE_NAME)
    except:
        # Ignore errors when deleting cookies
        pass

def check_authentication():
    """Check if the user is authenticated"""
    init_session_state()
    return st.session_state.authenticated

def authenticate(username, password):
    """Authenticate a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find the user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        stored_password = user['password']
        hashed_password = hash_password(password)
        
        if stored_password == hashed_password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = user['role']
            st.session_state.login_error = ""
            
            # Set authentication data
            set_auth_data(username, user['role'])
            
            conn.close()
            return True
    
    conn.close()
    st.session_state.login_error = "Invalid username or password"
    return False

def login():
    """Display login form"""
    # Initialize session state and check for existing cookie auth
    is_authenticated = init_session_state()
    
    # Skip login screen if already authenticated
    if is_authenticated:
        return
    
    st.title("Lab Equipment Inventory")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        # Define callback function for form submission
        def do_login():
            username = st.session_state.username_input
            password = st.session_state.password_input
            authenticate(username, password)
        
        # Create form
        with st.form(key="login_form"):
            st.text_input("Username", key="username_input")
            st.text_input("Password", type="password", key="password_input")
            
            # Remember me option (visual only for now - we always remember)
            remember_me = st.checkbox("Remember me for 7 days", value=True, key="remember_me")
            
            col_btn, _, _ = st.columns([1, 2, 1])
            
            with col_btn:
                submit_button = st.form_submit_button(label="Login", on_click=do_login)
        
        # Forgot password button outside the form
        if st.button("Forgot Password?"):
            st.session_state.show_password_reset = True
        
        if st.session_state.login_error:
            st.error(st.session_state.login_error)
        
        if "show_password_reset" in st.session_state and st.session_state.show_password_reset:
            st.subheader("Reset Password")
            
            with st.form(key="reset_password_form"):
                reset_email = st.text_input("Enter your email", key="reset_email")
                
                def do_reset():
                    email = st.session_state.reset_email
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                    user = cursor.fetchone()
                    
                    conn.close()
                    
                    if user:
                        # In a real app, you would send an email with a reset link
                        st.session_state.reset_success = True
                        st.session_state.show_password_reset = False
                    else:
                        st.session_state.reset_error = "Email not found"
                
                reset_submit = st.form_submit_button("Send Reset Link", on_click=do_reset)
            
            # Show success/error messages outside the form
            if "reset_success" in st.session_state and st.session_state.reset_success:
                st.success("Password reset link sent to your email!")
                st.session_state.reset_success = False
            
            if "reset_error" in st.session_state and st.session_state.reset_error:
                st.error(st.session_state.reset_error)
                st.session_state.reset_error = ""

def change_password(username, current_password, new_password):
    """Change a user's password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify current password
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user or user['password'] != hash_password(current_password):
        conn.close()
        return False
    
    # Update password
    hashed_new_password = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_new_password, username))
    conn.commit()
    conn.close()
    return True

def send_email(to_email, subject, body):
    """Send an email (mock function - in production connect to SMTP server)"""
    # This is a mock function - in production, connect to an SMTP server
    st.success(f"Email would be sent to {to_email}")
    st.info(f"Subject: {subject}")
    st.info(f"Body: {body}")
    
    # Real implementation would be like:
    """
    sender_email = "your-email@example.com"
    password = "your-email-password"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, message.as_string())
    """