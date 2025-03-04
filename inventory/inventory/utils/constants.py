# Application constants
APP_TITLE = "Lab Equipment Inventory"
DATA_PATH = "data"

# Dell corporate colors with dark mode
DELL_BLUE = "#0076CE"
DELL_GRAY = "#444444"
DELL_LIGHT_GRAY = "#F2F2F2"
DELL_DARK = "#1E1E1E"
DELL_DARK_SECONDARY = "#2D2D2D"

# User roles
ROLES = {
    "admin": "Administrator",
    "user": "Regular User",
    "readonly": "Read-Only User"
}

# Equipment status options
EQUIPMENT_STATUS = {
    "in_stock": "In Stock",
    "checked_out": "Checked Out",
    "maintenance": "Under Maintenance",
    "lost": "Lost/Missing"
}

# Default checkout duration in days
DEFAULT_CHECKOUT_DAYS = 14