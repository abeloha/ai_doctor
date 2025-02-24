import streamlit as st
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MySQL database credentials from .env
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Connect to MySQL database
def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone VARCHAR(15) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(50) NOT NULL,
            dob DATE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    return conn

# Hash password securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Ensure session state variables are initialized
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None  # Store user data to avoid repeated queries
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_message_is_set" not in st.session_state:
        st.session_state.system_message_is_set = False

initialize_session_state()

# Check if user is logged in
def is_logged_in():
    return st.session_state.logged_in

# Authenticate user from the MySQL database
def authenticate_user(phone, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    hashed_pw = hash_password(password)

    cursor.execute("SELECT id, phone, name, dob FROM users WHERE phone = %s AND password = %s", (phone, hashed_pw))
    user = cursor.fetchone()
    conn.close()

    if user:
        st.session_state.logged_in = True
        st.session_state.user_data = user  # Store user data in session
        return True
    return False

# Register a new user in MySQL
def register_user(phone, password, name, dob):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
    if cursor.fetchone():
        conn.close()
        return False  # User already exists

    hashed_pw = hash_password(password)
    cursor.execute("INSERT INTO users (phone, password, name, dob) VALUES (%s, %s, %s, %s)", 
                   (phone, hashed_pw, name, dob))
    conn.commit()
    
    # login the new user
    authenticate_user(phone, password)

# Get logged-in user data from session (no repeated DB queries)
def get_logged_in_user():
    if st.session_state.logged_in and st.session_state.user_data:
        return st.session_state.user_data
    return None


def get_logged_in_username():
    if st.session_state.logged_in and st.session_state.user_data:
        return st.session_state.user_data["name"]
    return None

def get_logged_in_id():
    if st.session_state.logged_in and st.session_state.user_data:
        return st.session_state.user_data["id"]
    return None

def get_logged_in_first_name():
    if st.session_state.logged_in and st.session_state.user_data:
        return st.session_state.user_data["name"].split()[0]  # Get first word of the name
    return None

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_data = None



def save_message(user_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)", 
                   (user_id, role, content))
    
    conn.commit()
    conn.close()


def get_user_messages(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT role, content, timestamp FROM messages WHERE user_id = %s ORDER BY timestamp ASC", (user_id,))
    messages = cursor.fetchall()
    
    conn.close()

    return messages