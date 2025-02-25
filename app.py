import streamlit as st
from auth import show_auth_page
from chat import show_chat_page
import state


# Set up the page
# Set page title and description
st.set_page_config(
    page_title=st.secrets["APP_NAME"],
    page_icon="🩺",  
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Set metadata (workaround)
st.markdown(
    f"""
    <meta name="description" content="{st.secrets['APP_DESCRIPTION']}">
    <meta name="keywords" content="AI Doctor, Health Companion, Medical AI, Nigeria">
    """,
    unsafe_allow_html=True
)



# Initialize session state variables
state.initialize_session_state()


# Check if the user is logged in
if state.is_logged_in():
    print("Logged in")
    show_chat_page()
else:
    print("Not Logged in")
    show_auth_page()