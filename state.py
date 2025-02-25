import streamlit as st
import mysql.connector
import hashlib

# Get MySQL database credentials from .env
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"]
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
            gender ENUM('Male', 'Female') NULL,
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
    if "welcome_message_is_sent" not in st.session_state:
        st.session_state.welcome_message_is_sent = False
    if "unsaved_ai_message" not in st.session_state:
        st.session_state.unsaved_ai_message = None

initialize_session_state()

# Check if user is logged in
def is_logged_in():
    return st.session_state.logged_in

# Authenticate user from the MySQL database
def check_phone_exists(phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, phone, name, dob, gender FROM users WHERE phone = %s", (phone,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return True

    return False

def authenticate_user(phone, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    hashed_pw = hash_password(password)

    cursor.execute("SELECT id, phone, name, dob, gender FROM users WHERE phone = %s AND password = %s", (phone, hashed_pw))
    user = cursor.fetchone()
    conn.close()

    if user:
        st.session_state.logged_in = True
        st.session_state.user_data = user  # Store user data in session
        return True
    return False

# Register a new user in MySQL
def register_user(phone, password, name, dob, gender):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
    if cursor.fetchone():
        conn.close()
        return False  # User already exists

    hashed_pw = hash_password(password)
    cursor.execute("INSERT INTO users (phone, password, name, dob, gender) VALUES (%s, %s, %s, %s, %s)", 
                   (phone, hashed_pw, name, dob, gender))
    conn.commit()
    
    # login the new user
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, phone, name, dob, gender FROM users WHERE phone = %s", (phone,))
    user = cursor.fetchone()
    conn.close()

    if user:
        st.session_state.logged_in = True
        st.session_state.user_data = user  # Store user data in session
        return True

    return False

# Get logged-in user data from session (no repeated DB queries)
def get_logged_in_user():
    if st.session_state.logged_in and st.session_state.user_data:
        return st.session_state.user_data
    return None

def get_logged_in_user_basic_info():
    user_data = get_logged_in_user()
    if user_data:
        return {
            "name": user_data["name"],
            "dob": user_data["dob"],
            "gender": user_data["gender"],
            "medical summary": "",
        }
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


def get_user_latest_messages(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT role, content, timestamp FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT 10", (user_id,))
    messages = cursor.fetchall()
    
    conn.close()

    return messages


def get_system_prompt():

    app_name = st.secrets["APP_NAME"]
    return f"""
    You are {app_name}, a Nigerian AI doctor. You provide health advice with humor and cultural references.
    ## **Guidelines:**
    - Focus only on health. Redirect off-topic humorously.
    - Do not answer questions that are not related to health.
    - Adjust language based on user.
    - Recommend **medications, tests, or hospital visits** as needed.
    - Use humor but keep medical info clear.
    ## **Response Rules:**
    1. One question per response.
    2. Emergency? Urge immediate hospital visit.
    3. Clarify traditional remedies before recommending.
    4. If off-topic? Redirect humorously.
    5. Keep response very short.
    ## **Language & Humor:**
    - Mix English with a bit Pidgin.
    - If user reply in English 3 times in a row, then stop Pidgin.
    - Example slang:
    - Urgency: *"Quick-quick!"*
    - Reassurance: *"No shaking!"*
    - Analogies: *"This headache stubborn like Lagos traffic!"*
    """