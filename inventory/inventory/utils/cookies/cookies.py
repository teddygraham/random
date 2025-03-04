import streamlit as st
import json
import base64
import datetime
import time

def set_cookie(name, value, expires_at=None, key=None):
    """
    Set a cookie using Streamlit's query parameters.
    This is a workaround since Streamlit doesn't natively support cookies.
    
    Args:
        name (str): The name of the cookie
        value (str): The value to store
        expires_at (datetime): When the cookie should expire
        key (str): Unique key for the component
    """
    if key is None:
        key = f"cookie_{name}"
        
    if expires_at is None:
        # Default: expire in 30 days
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        
    expiry_timestamp = int(time.mktime(expires_at.timetuple()))
    
    # Create cookie data with value and expiry
    cookie_data = {
        "value": value,
        "expires": expiry_timestamp
    }
    
    # Store in session state
    if "cookies" not in st.session_state:
        st.session_state.cookies = {}
        
    st.session_state.cookies[name] = cookie_data
    
    # Store in local storage using st.markdown hack
    js_code = f"""
    <script>
    try {{
        const cookieData = {json.dumps(cookie_data)};
        localStorage.setItem('st_cookie_{name}', JSON.stringify(cookieData));
        console.log('Cookie {name} set in localStorage');
    }} catch (error) {{
        console.error('Error setting cookie:', error);
    }}
    </script>
    """
    
    st.markdown(js_code, unsafe_allow_html=True)
    
def get_cookie(name, default=None):
    """
    Get a cookie value.
    First checks session state, then tries to retrieve from localStorage.
    
    Args:
        name (str): The name of the cookie
        default: The default value if cookie doesn't exist
        
    Returns:
        The cookie value or default if not found
    """
    # Check if we have it in session state
    if "cookies" in st.session_state and name in st.session_state.cookies:
        cookie_data = st.session_state.cookies[name]
        
        # Check expiry
        if cookie_data["expires"] > int(time.time()):
            return cookie_data["value"]
        else:
            # Expired - remove it
            del st.session_state.cookies[name]
    
    # Try to retrieve from local storage using JavaScript
    retrieve_js = f"""
    <script>
    try {{
        const cookieStr = localStorage.getItem('st_cookie_{name}');
        if (cookieStr) {{
            const cookieData = JSON.parse(cookieStr);
            
            // Check if expired
            if (cookieData.expires > {int(time.time())}) {{
                // Valid cookie - store it in a hidden element for retrieval
                const hiddenDiv = document.getElementById('cookie_value_{name}');
                if (hiddenDiv) {{
                    hiddenDiv.innerText = cookieData.value;
                    // Also update the "cookie_retrieved" element
                    const retrievedDiv = document.getElementById('cookie_retrieved_{name}');
                    if (retrievedDiv) {{
                        retrievedDiv.innerText = 'true';
                    }}
                }}
            }} else {{
                // Expired cookie - remove it
                localStorage.removeItem('st_cookie_{name}');
            }}
        }}
    }} catch (error) {{
        console.error('Error getting cookie:', error);
    }}
    </script>
    
    <div id="cookie_value_{name}" style="display: none;"></div>
    <div id="cookie_retrieved_{name}" style="display: none;">false</div>
    """
    
    # We'll use this once per Streamlit session to try to retrieve cookies
    if f"cookie_retrieve_attempt_{name}" not in st.session_state:
        st.markdown(retrieve_js, unsafe_allow_html=True)
        st.session_state[f"cookie_retrieve_attempt_{name}"] = True
    
    return default
    
def delete_cookie(name):
    """
    Delete a cookie.
    
    Args:
        name (str): The name of the cookie to delete
    """
    # Remove from session state if it exists
    if "cookies" in st.session_state and name in st.session_state.cookies:
        del st.session_state.cookies[name]
    
    # Remove from localStorage
    delete_js = f"""
    <script>
    try {{
        localStorage.removeItem('st_cookie_{name}');
        console.log('Cookie {name} removed from localStorage');
    }} catch (error) {{
        console.error('Error removing cookie:', error);
    }}
    </script>
    """
    
    st.markdown(delete_js, unsafe_allow_html=True)