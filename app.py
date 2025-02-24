import streamlit as st
from auth import show_auth_page
from chat import show_chat_page
import state


# Set up the page
st.set_page_config(page_title="Chat App", page_icon="💬")

# Initialize session state variables
state.initialize_session_state()


# Check if the user is logged in
if state.is_logged_in():
    print("Logged in")
    show_chat_page()
else:
    print("Not Logged in")
    show_auth_page()