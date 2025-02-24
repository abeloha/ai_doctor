import streamlit as st
import os
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
    if "system_message_is_set" not in st.session_state:
        st.session_state.system_message_is_set = False

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
            avatar = None if message["role"] == "user" else "👨‍⚕️"
            with st.chat_message(role_name, avatar=avatar):
                st.markdown(message["content"])

def get_ai_response(client, model):
    """Fetch AI response from Groq API."""
    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
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
    if prompt := st.chat_input("Talk to your doctor", max_chars=1000):
        with st.chat_message(state.get_logged_in_username()):
            st.markdown(prompt)

        # Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        state.save_message(state.get_logged_in_id(), "user", prompt)

        # Get AI response
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            response = get_ai_response(client, model)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.save_message(state.get_logged_in_id(), "assistant", response)

        # **Trim messages to last 10 entries**
        st.session_state.messages = st.session_state.messages[-10:]

def show_chat_page():
    """Main function to render the chat page."""
    app_name = os.getenv("APP_NAME")
    model = os.getenv("GROQ_MODEL")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    st.title(app_name)
    st.write(f"{state.get_logged_in_username()}'s personal AI doctor 👨‍⚕️")

    initialize_session()
    load_past_messages()
    
    system_prompt = f"""
    You are {app_name}, a Nigerian AI doctor. You provide health advice with humor and cultural references.

    ## **Guidelines:**
    - Focus only on health. Redirect off-topic chats humorously.
    - Adjust **language** (English/Pidgin) based on user.
    - Recommend **medications, tests, or hospital visits** as needed.
    - Use humor but keep medical info clear.

    ## **Response Rules:**
    1. One question per response.
    2. Emergency? Urge immediate hospital visit.
    3. Clarify traditional remedies before recommending.
    4. If off-topic? Redirect humorously.

    ## **Language & Humor:**
    - Mix Pidgin & English based on user preference.
    - Example slang:
    - Urgency: *"Quick-quick!"*
    - Reassurance: *"No shaking!"*
    - Analogies: *"This headache stubborn like Lagos traffic!"*
    """

    if not st.session_state.system_message_is_set:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
        ] + st.session_state.messages

        st.session_state.messages.append({"role": "system", "content": f"The user details are: {state.get_logged_in_user()}. Start the conversation based on history."})
        st.session_state.system_message_is_set = True

        # AI's first response
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            response = get_ai_response(client, model)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.save_message(state.get_logged_in_id(), "assistant", response)

    display_messages(app_name)
    handle_user_input(client, model)