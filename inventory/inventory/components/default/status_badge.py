import streamlit as st
from ...utils.constants import EQUIPMENT_STATUS, DELL_DARK_SECONDARY

def status_badge(status):
    """
    Display a status badge with appropriate color based on equipment status.
    
    Args:
        status (str): The equipment status
    """
    # Define badge colors based on status - using brighter colors for dark mode
    badge_colors = {
        EQUIPMENT_STATUS["in_stock"]: "#00CC66",      # Bright green
        EQUIPMENT_STATUS["checked_out"]: "#FF9900",   # Bright orange
        EQUIPMENT_STATUS["maintenance"]: "#3399FF",   # Bright blue
        EQUIPMENT_STATUS["lost"]: "#FF3333"           # Bright red
    }
    
    # Default color if status not found
    color = badge_colors.get(status, "#999999")
    
    # Render the badge
    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: 0.2em 0.6em;
            border-radius: 0.25em;
            font-size: 0.9em;
            font-weight: bold;
            color: white;
            background-color: {color};
            text-align: center;
        ">
            {status}
        </div>
        """,
        unsafe_allow_html=True
    )