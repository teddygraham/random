import streamlit as st
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inventory.app.auth import login, check_authentication
from inventory.app.pages import equipment, users, reports, qr_scanner, equipment_details
from inventory.utils.constants import APP_TITLE, DELL_BLUE, DELL_DARK, DELL_DARK_SECONDARY

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Apply Dell corporate styling with dark mode
    st.markdown(
        f"""
        <style>
        .reportview-container .main .block-container{{
            max-width: 1200px;
        }}
        .stApp {{
            background-color: {DELL_DARK};
            color: white;
        }}
        .stButton>button {{
            background-color: {DELL_BLUE};
            color: white;
        }}
        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: {DELL_DARK_SECONDARY};
            color: white;
        }}
        /* Card/container styling */
        div.stTabs [data-baseweb="tab-panel"] {{
            background-color: {DELL_DARK_SECONDARY};
            padding: 15px;
            border-radius: 5px;
        }}
        div.stTabs [data-baseweb="tab-list"] {{
            background-color: {DELL_DARK};
        }}
        div.stTabs [data-baseweb="tab-border"] {{
            background-color: {DELL_BLUE};
        }}
        div.stTabs [data-baseweb="tab"] {{
            color: white;
        }}
        div.stTabs [data-baseweb="tab-highlight"] {{
            background-color: {DELL_BLUE};
        }}
        div[data-testid="stForm"] {{
            background-color: {DELL_DARK_SECONDARY};
            padding: 15px;
            border-radius: 5px;
        }}
        /* Text inputs */
        div[data-baseweb="input"] {{
            background-color: {DELL_DARK};
        }}
        div[data-baseweb="input"] input {{
            color: white !important;
        }}
        /* Select inputs */
        div[data-baseweb="select"] {{
            background-color: {DELL_DARK};
        }}
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {{
            color: white;
        }}
        /* DataFrames */
        .stDataFrame {{
            background-color: {DELL_DARK_SECONDARY};
        }}
        .dataframe {{
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not check_authentication():
        login()
    else:
        # Display main navigation in sidebar
        st.sidebar.title("Lab Inventory")
        # Main navigation options without Equipment Details page
        selection = st.sidebar.radio(
            "Go to",
            [
                "Equipment",
                "Users",
                "Reports",
                "QR Scanner",
            ]
        )
        
        # Display user info and logout option in the sidebar
        st.sidebar.markdown("---")
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
        st.sidebar.write(f"Role: {st.session_state.user_role}")
        if st.sidebar.button("Logout"):
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            
            # Clear auth data
            from inventory.app.auth import delete_auth_data
            try:
                delete_auth_data()
            except Exception:
                pass  # Ignore errors on logout
            
            st.rerun()
        
        # Check if we should display equipment details instead of regular routing
        if "selected_equipment_sku" in st.session_state and st.session_state.get("show_equipment_details", False):
            # Show equipment details page
            equipment_details.show()
            # Reset the flag after showing
            st.session_state.show_equipment_details = False
        else:
            # Route to the appropriate page based on sidebar selection
            if selection == "Equipment":
                equipment.show()
            elif selection == "Users":
                users.show()
            elif selection == "Reports":
                reports.show()
            elif selection == "QR Scanner":
                qr_scanner.show()

if __name__ == "__main__":
    main()