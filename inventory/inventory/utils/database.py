import os
import sqlite3
import json
import pandas as pd
import datetime
from pathlib import Path
import hashlib
from .constants import DATA_PATH

# Ensure data directory exists
Path(DATA_PATH).mkdir(exist_ok=True)

# Database file path
DB_FILE = os.path.join(DATA_PATH, "inventory.db")
IMAGES_DIR = os.path.join(DATA_PATH, "images")

# Ensure images directory exists
Path(IMAGES_DIR).mkdir(exist_ok=True)

def get_db_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def hash_password(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_database():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        department TEXT,
        created_at TEXT NOT NULL
    )
    ''')
    
    # Create equipment table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        sku TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        manufacturer TEXT,
        model TEXT,
        serial_number TEXT,
        purchase_date TEXT,
        purchase_price REAL,
        status TEXT NOT NULL,
        checked_out_by TEXT,
        checkout_date TEXT,
        due_date TEXT,
        location TEXT,
        image_path TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (checked_out_by) REFERENCES users (username)
    )
    ''')
    
    # Create checkout history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checkout_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        user TEXT NOT NULL,
        checkout_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        notes TEXT,
        FOREIGN KEY (sku) REFERENCES equipment (sku),
        FOREIGN KEY (user) REFERENCES users (username)
    )
    ''')
    
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_exists = cursor.fetchone()
    
    # Create admin user if it doesn't exist
    if not admin_exists:
        cursor.execute('''
        INSERT INTO users (username, email, password, role, name, department, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', hash_password('admin123'), 'admin', 'Administrator', 'IT', datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# Data access functions
def get_users():
    """Get all users as a pandas DataFrame"""
    conn = get_db_connection()
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return users_df

def get_equipment():
    """Get all equipment as a pandas DataFrame"""
    conn = get_db_connection()
    equipment_df = pd.read_sql_query("SELECT * FROM equipment", conn)
    conn.close()
    return equipment_df

def get_checkout_history():
    """Get all checkout history as a pandas DataFrame"""
    conn = get_db_connection()
    history_df = pd.read_sql_query("SELECT * FROM checkout_history", conn)
    conn.close()
    return history_df

def save_users(users_df):
    """Save users DataFrame to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete existing users (except for those being updated)
    usernames = tuple(users_df['username'].tolist()) if not users_df.empty else ('',)
    if len(usernames) == 1:
        # SQLite requires special handling for one-element tuples
        cursor.execute("DELETE FROM users WHERE username NOT IN (?)", usernames)
    else:
        cursor.execute("DELETE FROM users WHERE username NOT IN {}".format(usernames))
    
    # Insert or update users
    for _, user in users_df.iterrows():
        cursor.execute('''
        INSERT OR REPLACE INTO users (username, email, password, role, name, department, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['username'],
            user['email'],
            user['password'],
            user['role'],
            user['name'],
            user['department'],
            user['created_at']
        ))
    
    conn.commit()
    conn.close()

def save_equipment(equipment_df):
    """Save equipment DataFrame to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete existing equipment (except for those being updated)
    if not equipment_df.empty:
        skus = tuple(equipment_df['sku'].tolist())
        if len(skus) == 1:
            # SQLite requires special handling for one-element tuples
            cursor.execute("DELETE FROM equipment WHERE sku NOT IN (?)", skus)
        else:
            cursor.execute("DELETE FROM equipment WHERE sku NOT IN {}".format(skus))
    else:
        cursor.execute("DELETE FROM equipment")
    
    # Insert or update equipment
    for _, equip in equipment_df.iterrows():
        cursor.execute('''
        INSERT OR REPLACE INTO equipment (
            sku, name, description, category, manufacturer, model, serial_number, 
            purchase_date, purchase_price, status, checked_out_by, checkout_date, 
            due_date, location, image_path, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            equip['sku'],
            equip['name'],
            equip['description'],
            equip['category'],
            equip['manufacturer'],
            equip['model'],
            equip['serial_number'],
            equip['purchase_date'],
            equip['purchase_price'],
            equip['status'],
            equip['checked_out_by'],
            equip['checkout_date'],
            equip['due_date'],
            equip['location'],
            equip['image_path'],
            equip['created_at'],
            equip['updated_at']
        ))
    
    conn.commit()
    conn.close()

def save_checkout_history(history_df):
    """Save checkout history DataFrame to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing history
    cursor.execute("DELETE FROM checkout_history")
    
    # Insert history records
    for _, record in history_df.iterrows():
        cursor.execute('''
        INSERT INTO checkout_history (
            sku, equipment_name, user, checkout_date, due_date, return_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['sku'],
            record['equipment_name'],
            record['user'],
            record['checkout_date'],
            record['due_date'],
            record['return_date'],
            record['notes']
        ))
    
    conn.commit()
    conn.close()

def generate_sku():
    """Generate a unique SKU for new equipment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the maximum SKU value
    cursor.execute("SELECT sku FROM equipment WHERE sku LIKE 'LAB-%' ORDER BY sku DESC LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        last_sku = result[0]
        # Extract numeric part, assuming SKU format is LAB-XXXXX
        next_id = int(last_sku.split('-')[1]) + 1
    else:
        next_id = 1
    
    conn.close()
    
    # Format: LAB-00001, LAB-00002, etc.
    return f"LAB-{next_id:05d}"

# Initialize the database
initialize_database()