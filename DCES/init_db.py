import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# Database file path
DB_FILE = 'coupons.db'

# Remove existing database if it exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Removed existing {DB_FILE}")

# Connect to the database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
print(f"Connected to {DB_FILE}")

# Create User table
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create Category table
cursor.execute('''
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

# Create Coupon table
cursor.execute('''
CREATE TABLE coupon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    discount_value TEXT NOT NULL,
    store TEXT NOT NULL,
    expiry_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT 0,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (category_id) REFERENCES category (id)
)
''')

# Create Rating table
cursor.execute('''
CREATE TABLE rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    coupon_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (coupon_id) REFERENCES coupon (id) ON DELETE CASCADE
)
''')

print("All tables created successfully")

# Insert default categories
categories = ["Retail", "Food and Beverage", "Travel", "Electronics", "Entertainment", "Health", "Beauty", "Home"]
for category in categories:
    cursor.execute('INSERT INTO category (name) VALUES (?)', (category,))

print(f"Added {len(categories)} default categories")

# Insert admin user
admin_password = generate_password_hash('admin123')
cursor.execute('''
INSERT INTO user (username, email, password, is_admin)
VALUES (?, ?, ?, ?)
''', ('admin', 'admin@example.com', admin_password, True))

print("Added admin user (admin@example.com / admin123)")

# Insert a regular user
user_password = generate_password_hash('user123')
cursor.execute('''
INSERT INTO user (username, email, password, is_admin)
VALUES (?, ?, ?, ?)
''', ('user', 'user@example.com', user_password, False))

print("Added regular user (user@example.com / user123)")

# Get category IDs for the sample coupons
cursor.execute("SELECT id FROM category WHERE name = 'Retail'")
retail_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM category WHERE name = 'Food and Beverage'")
food_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM category WHERE name = 'Electronics'")
electronics_id = cursor.fetchone()[0]

# Get user IDs
cursor.execute("SELECT id FROM user WHERE username = 'admin'")
admin_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM user WHERE username = 'user'")
user_id = cursor.fetchone()[0]

# Insert sample coupons
sample_coupons = [
    (
        'Amazon 20% Off', 
        'Get 20% off on your first purchase', 
        'AMAZON20', 
        '20%', 
        'Amazon', 
        (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        1,  # is_verified
        admin_id,
        retail_id
    ),
    (
        'Starbucks BOGO', 
        'Buy one coffee get one free', 
        'COFFEE4U', 
        'Buy One Get One', 
        'Starbucks', 
        (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
        1,  # is_verified
        user_id,
        food_id
    ),
    (
        'Best Buy $50 Off', 
        '$50 off purchases over $200', 
        'BBSAVE50', 
        '$50', 
        'Best Buy', 
        (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
        0,  # not verified
        admin_id,
        electronics_id
    )
]

for coupon in sample_coupons:
    cursor.execute('''
    INSERT INTO coupon (title, description, code, discount_value, store, expiry_date, is_verified, user_id, category_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', coupon)

print(f"Added {len(sample_coupons)} sample coupons")

# Insert sample ratings
sample_ratings = [
    (5, "Great discount, worked perfectly!", user_id, 1),  # Rating for Amazon coupon
    (4, "Good deal, easy to redeem", admin_id, 2),  # Rating for Starbucks coupon
    (3, "It works but limited selection", user_id, 3)   # Rating for Best Buy coupon
]

for rating in sample_ratings:
    cursor.execute('''
    INSERT INTO rating (score, comment, user_id, coupon_id)
    VALUES (?, ?, ?, ?)
    ''', rating)

print(f"Added {len(sample_ratings)} sample ratings")

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Database {DB_FILE} has been successfully created and populated with sample data!")