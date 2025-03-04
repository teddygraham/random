# Lab Equipment Inventory System

A comprehensive inventory management system for laboratory equipment, built with Streamlit.

## Features

- **Equipment Management**: Add, edit, view, and remove equipment
- **User Management**: Add, edit, view, and remove users with different roles (admin, user, read-only)
- **Checkout System**: Check out and return equipment with history tracking
- **QR Code Integration**: Generate and scan QR codes for quick equipment checkout/return
- **Reports**: Generate reports on equipment status, checkout history, and more
- **Dell-inspired UI**: Dell corporate styling throughout the application
- **Customizable Components**: Easily replace UI components with custom implementations

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Run the application with:

```
streamlit run app.py
```

The application will be available at http://localhost:8501.

## Default Login

- Username: admin
- Password: admin123

## Project Structure

```
inventory/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── data/                   # Data storage (created automatically)
│   ├── users.csv           # User data
│   ├── equipment.csv       # Equipment data
│   ├── checkout_history.csv # Checkout history records
│   └── images/             # Equipment and QR code images
├── inventory/              # Main package
│   ├── app/                # Application logic
│   │   ├── auth.py         # Authentication module
│   │   └── pages/          # Application pages
│   │       ├── equipment.py # Equipment management page
│   │       ├── users.py     # User management page
│   │       ├── reports.py   # Reports page
│   │       └── qr_scanner.py # QR scanner page
│   ├── utils/              # Utility functions
│   │   ├── database.py     # Database access functions
│   │   ├── qr_code.py      # QR code generation/scanning
│   │   └── constants.py    # Application constants
│   └── components/         # UI components
│       ├── custom/         # Custom component implementations
│       └── default/        # Default component implementations
```

## Customizing Components

You can customize UI components by:

1. Find the component you want to customize in the `inventory/components/default` directory
2. Copy the component file to the `inventory/components/custom` directory
3. Modify the component's implementation as needed
4. The system will automatically load your custom version instead of the default

## Adding Equipment

1. Log in as an admin user
2. Go to the Equipment tab
3. Select the "Add Equipment" sub-tab
4. Fill in the equipment details and click "Add Equipment"
5. A QR code will be automatically generated for the new equipment

## Checking Out Equipment

1. Go to the Equipment tab
2. Select the "Checkout/Return" sub-tab
3. Select the equipment to check out
4. Set the checkout duration and any notes
5. Click "Checkout Equipment"

Alternatively, use the QR Scanner tab to scan the equipment's QR code for quick checkout.

## Security Notes

- This application uses simple password storage for demonstration purposes
- In a production environment, use proper password hashing and secure authentication
- Configure proper database storage (e.g., PostgreSQL, MySQL) for production use

## License

This project is licensed under the MIT License.