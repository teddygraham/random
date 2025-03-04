import os
import importlib.util
import streamlit as st
import streamlit.components.v1 as components
import inspect

# Directory containing custom components
COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom")
DEFAULT_COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default")

def load_component(component_name):
    """
    Load a component, first checking the custom directory, then falling back to the default.
    
    Args:
        component_name (str): Name of the component to load
    
    Returns:
        function: The component function
    """
    # Check for custom implementation
    custom_path = os.path.join(COMPONENTS_DIR, f"{component_name}.py")
    if os.path.exists(custom_path):
        module = load_module_from_path(custom_path, f"custom_{component_name}")
        return getattr(module, component_name)
    
    # Fall back to default implementation
    default_path = os.path.join(DEFAULT_COMPONENTS_DIR, f"{component_name}.py")
    if os.path.exists(default_path):
        module = load_module_from_path(default_path, f"default_{component_name}")
        return getattr(module, component_name)
    
    raise ValueError(f"Component '{component_name}' not found in either custom or default directories.")

def load_module_from_path(path, module_name):
    """
    Load a Python module from a file path.
    
    Args:
        path (str): Path to the module file
        module_name (str): Name to assign to the module
    
    Returns:
        module: The loaded Python module
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def ensure_component_dirs():
    """Ensure the component directories exist"""
    os.makedirs(COMPONENTS_DIR, exist_ok=True)
    os.makedirs(DEFAULT_COMPONENTS_DIR, exist_ok=True)
    
    # Create a README in the custom directory to explain how to use it
    readme_path = os.path.join(COMPONENTS_DIR, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("""# Custom Components

This directory contains custom implementations of UI components for the Lab Equipment Inventory System.

## How to customize a component

1. Find the component you want to customize in the `../default` directory
2. Copy the component file to this directory
3. Modify the component's implementation as needed
4. The system will automatically load your custom version instead of the default

## Available components

- `data_table.py`: Enhanced data table with sorting and filtering
- `status_badge.py`: Status indicator badges with different colors for equipment status
- `checkout_form.py`: Equipment checkout form
- `return_form.py`: Equipment return form
- `qr_display.py`: QR code display component
""")

# Call this function when the module is imported
ensure_component_dirs()