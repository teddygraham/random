import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import datetime
import base64

from ...utils.database import get_equipment, get_checkout_history, get_users
from ...utils.constants import EQUIPMENT_STATUS

def show():
    """Display the reports page"""
    st.title("Reports")
    
    # Create tabs for different reports
    tab1, tab2, tab3, tab4 = st.tabs([
        "Equipment Status", 
        "Checkout History", 
        "User Activity",
        "Overdue Items"
    ])
    
    with tab1:
        equipment_status_report()
    
    with tab2:
        checkout_history_report()
    
    with tab3:
        user_activity_report()
    
    with tab4:
        overdue_items_report()

def equipment_status_report():
    """Report on equipment status"""
    st.subheader("Equipment Status Report")
    
    equipment_df = get_equipment()
    
    if equipment_df.empty:
        st.info("No equipment data available.")
        return
    
    # Count equipment by status
    status_counts = equipment_df["status"].value_counts()
    
    # Create a pie chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    st.pyplot(fig)
    
    # Display a table of equipment counts by category
    st.subheader("Equipment by Category")
    
    if "category" in equipment_df.columns:
        category_counts = equipment_df["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        st.dataframe(category_counts, use_container_width=True)
    else:
        st.info("No category data available.")
    
    # Display a table of equipment by status
    st.subheader("Equipment by Status")
    
    status_table = pd.DataFrame({
        "Status": status_counts.index,
        "Count": status_counts.values
    })
    
    st.dataframe(status_table, use_container_width=True)
    
    # Download CSV
    csv = equipment_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="equipment_report.csv">Download Equipment Data (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)

def checkout_history_report():
    """Report on checkout history"""
    st.subheader("Checkout History Report")
    
    history_df = get_checkout_history()
    
    if history_df.empty:
        st.info("No checkout history available.")
        return
    
    # Date filters
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.datetime.now() - datetime.timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.datetime.now()
        )
    
    # Convert dates to string format for comparison
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Filter history by date range
    filtered_history = history_df[
        (history_df["checkout_date"] >= start_date_str) & 
        (history_df["checkout_date"] <= end_date_str)
    ]
    
    if filtered_history.empty:
        st.info(f"No checkout history found between {start_date_str} and {end_date_str}.")
        return
    
    # Display checkout history
    st.dataframe(filtered_history, use_container_width=True)
    
    # Calculate average checkout duration
    filtered_history_with_return = filtered_history[filtered_history["return_date"].notna()]
    
    if not filtered_history_with_return.empty:
        # Calculate checkout duration in days
        checkout_durations = []
        
        for _, row in filtered_history_with_return.iterrows():
            checkout_date = datetime.datetime.strptime(row["checkout_date"], "%Y-%m-%d")
            return_date = datetime.datetime.strptime(row["return_date"], "%Y-%m-%d")
            duration = (return_date - checkout_date).days
            checkout_durations.append(duration)
        
        avg_duration = sum(checkout_durations) / len(checkout_durations)
        
        st.info(f"Average checkout duration: {avg_duration:.1f} days")
    
    # Download CSV
    csv = filtered_history.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="checkout_history_report.csv">Download Checkout History (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)

def user_activity_report():
    """Report on user activity"""
    st.subheader("User Activity Report")
    
    history_df = get_checkout_history()
    users_df = get_users()
    
    if history_df.empty:
        st.info("No checkout history available.")
        return
    
    # Count checkouts by user
    user_counts = history_df["user"].value_counts().reset_index()
    user_counts.columns = ["Username", "Checkouts"]
    
    # Merge with user data to get user names
    if not users_df.empty and "name" in users_df.columns:
        user_counts = user_counts.merge(
            users_df[["username", "name", "department"]],
            left_on="Username",
            right_on="username",
            how="left"
        )
        user_counts.drop("username", axis=1, inplace=True)
    
    # Display user activity
    st.dataframe(user_counts, use_container_width=True)
    
    # Create a bar chart of top users
    top_n = min(10, len(user_counts))
    top_users = user_counts.sort_values("Checkouts", ascending=False).head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(
        top_users["Username"], 
        top_users["Checkouts"],
        color="skyblue"
    )
    ax.set_xlabel("Username")
    ax.set_ylabel("Number of Checkouts")
    ax.set_title("Top Users by Number of Checkouts")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Download CSV
    csv = user_counts.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="user_activity_report.csv">Download User Activity (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)

def overdue_items_report():
    """Report on overdue items"""
    st.subheader("Overdue Items Report")
    
    equipment_df = get_equipment()
    
    if equipment_df.empty:
        st.info("No equipment data available.")
        return
    
    # Get checked out equipment
    checked_out = equipment_df[equipment_df["status"] == EQUIPMENT_STATUS["checked_out"]]
    
    if checked_out.empty:
        st.info("No equipment is currently checked out.")
        return
    
    # Today's date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get overdue items
    overdue_items = checked_out[checked_out["due_date"] < today]
    
    if overdue_items.empty:
        st.success("There are no overdue items.")
        return
    
    # Display overdue items
    st.warning(f"There are {len(overdue_items)} overdue items.")
    
    # Add days overdue column
    overdue_items_display = overdue_items.copy()
    overdue_items_display["days_overdue"] = overdue_items_display["due_date"].apply(
        lambda x: (datetime.datetime.now() - datetime.datetime.strptime(x, "%Y-%m-%d")).days
    )
    
    # Display columns for the report
    display_cols = ["sku", "name", "checked_out_by", "checkout_date", "due_date", "days_overdue"]
    st.dataframe(overdue_items_display[display_cols], use_container_width=True)
    
    # Group by user
    user_overdue = overdue_items.groupby("checked_out_by").size().reset_index()
    user_overdue.columns = ["Username", "Overdue Items"]
    
    st.subheader("Overdue Items by User")
    st.dataframe(user_overdue, use_container_width=True)
    
    # Download CSV
    csv = overdue_items_display.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="overdue_items_report.csv">Download Overdue Items Report (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)