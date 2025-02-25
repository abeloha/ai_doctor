import streamlit as st

import state
from groq import Groq
from datetime import datetime, timedelta


def time_ago(timestamp):
    past_time = timestamp
    now = datetime.now()
    diff = now - past_time

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        return f"{diff.seconds // 60} min ago"
    elif diff < timedelta(days=1):
        return f"{diff.seconds // 3600} hours ago"
    elif diff < timedelta(days=7):
        return f"{diff.days} days ago"
    else:
        return past_time.strftime('%d %b')

def initialize_session():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "welcome_message_is_sent" not in st.session_state:
        st.session_state.welcome_message_is_sent = False

def load_past_messages():
    """Load past messages from the database into session state."""
    past_messages = state.get_user_latest_messages(state.get_logged_in_id())
    
    if past_messages:
        formatted_past_messages = [
            {"role": msg["role"], "content": f"{msg['content']}  \n({time_ago(msg['timestamp'])})"}
            for msg in past_messages
        ]

        # Only keep the last 10 messages to prevent hitting token limits
        st.session_state.messages = formatted_past_messages[-10:] + st.session_state.messages

def display_messages(app_name):
    """Display chat messages from session state."""
    for message in st.session_state.messages:
        if message["role"] != "system":
            role_name = state.get_logged_in_username() if message["role"] == "user" else app_name
            avatar = None if message["role"] == "user" else "🩺"
            # "👨‍⚕️"
            with st.chat_message(role_name, avatar=avatar):
                st.markdown(message["content"])

# use additional_instructions to customize the AI's behavior. This is added at the bottom of the message
def get_ai_response(client, model, additional_instructions:str = ""):

    # **Trim messages to last 15 entries**
    history = st.session_state.messages[-15:]

    # Add instructions to the message
    system_prompt = state.get_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"The user details are: {state.get_logged_in_user_basic_info()}."},
    ] + history

    if (additional_instructions):
         messages.append(
            {"role": "system", "content": additional_instructions}
        )

    """Fetch AI response from Groq API."""
    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )

        response_container = st.empty()
        full_response = ""

        for chunk in response_stream:
            text = chunk.choices[0].delta.content
            if text:
                full_response += text
                response_container.markdown(full_response)

        return full_response.strip()
    except Exception as e:
        st.error("Oops! Something went wrong. Please try again.")
        print(f"Error in AI response: {e}")
        return None

def handle_user_input(client, model):
    """Handle user input and get AI response."""
    if prompt := st.chat_input("Talk to your doctor", max_chars=500):

        # Save the AI first message now that user has started the conversation
        if state.unsaved_ai_message:
            state.save_message(state.get_logged_in_id(), "assistant", state.unsaved_ai_message)
            state.unsaved_ai_message = None

        with st.chat_message(state.get_logged_in_username()):
            st.markdown(prompt)

        # Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        state.save_message(state.get_logged_in_id(), "user", prompt)

        # Get AI response
        with st.chat_message("assistant", avatar="🩺"):
            response = get_ai_response(client, model)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.save_message(state.get_logged_in_id(), "assistant", response)

def show_chat_page():
    """Main function to render the chat page."""
    app_name = st.secrets["APP_NAME"]
    model = st.secrets["GROQ_MODEL"]
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    st.title(app_name)
    st.write(f"{state.get_logged_in_username()}'s personal AI doctor 👨‍⚕️")

    if not st.session_state.welcome_message_is_sent:
        initialize_session()
        load_past_messages()
        st.session_state.welcome_message_is_sent = True

        # AI's first response
        with st.chat_message("assistant", avatar="🩺"):
            response = get_ai_response(client, model, additional_instructions="Start the conversation.")
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.unsaved_ai_message = response

    display_messages(app_name)
    handle_user_input(client, model)