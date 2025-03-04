import streamlit as st
import pandas as pd

def data_table(df, columns=None, use_container_width=True, height=None, selection=None, key=None):
    """
    Enhanced data table with sorting and optional column selection.
    
    Args:
        df (pd.DataFrame): The DataFrame to display
        columns (list): Columns to display (default: all)
        use_container_width (bool): Whether to expand to container width
        height (int): Optional height specification
        selection (str): Selection mode ('single' or 'multi')
        key (str): Key for the component
    
    Returns:
        list: Selected rows if selection is enabled
    """
    if df.empty:
        st.info("No data to display.")
        return None
    
    # Use specified columns or all columns
    display_df = df[columns] if columns else df
    
    # Generate key if not provided
    if key is None:
        key = f"data_table_{id(df)}"
    
    # Set up table options
    table_args = {
        "data": display_df,
        "use_container_width": use_container_width,
        "key": key
    }
    
    # Add height if specified
    if height:
        table_args["height"] = height
    
    # Handle selection modes
    if selection == "single":
        return st.data_editor(
            **table_args,
            disabled=True,
            num_rows="fixed",
            selection_mode="single"
        )
    elif selection == "multi":
        return st.data_editor(
            **table_args,
            disabled=True,
            num_rows="fixed",
            selection_mode="multi"
        )
    else:
        # Standard display with no selection
        return st.dataframe(**table_args)