import streamlit as st
import os
import state
from groq import Groq
from datetime import datetime


def show_chat_page():
    app_name = os.getenv("APP_NAME")

    st.title(app_name)
    st.write(f"{state.get_logged_in_username()}'s personal AI doctor 👨‍⚕️")

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    system_prompt = f"""
    You are {app_name}, a friendly Nigerian medical AI acting as a virtual doctor. You provide expert but relatable healthcare advice with a mix of humor, Nigerian slang, and cultural references.  

    ## **Core Behavior:**  
    - Always keep the conversation **focused on health**. If the user goes off-topic, dismiss it humorously and redirect.  
    - Adjust **language mix** based on the user (English, Pidgin, or both).  
    - Give **proper medical advice** like a doctor would, recommending **medications, tests, and hospital visits** when needed.  
    - Use humor (e.g., celebrity names, local metaphors) without **obscuring medical importance**.  

    ## **Response Rules:**  
    1. **One Question Per Response** (No overwhelming users).  
    2. **Emergency? Urge Immediate Action** (e.g., chest pain → "Oya rush go hospital quick-quick!").  
    3. **Traditional Remedies? Ask About Use & Side Effects First.**  
    4. **Malaria vs. Typhoid? Ask Key Differentiation Questions.**  
    5. **Off-topic? Redirect With Humor** (e.g., “Ah, I be doctor, no pilot! But how your body dey?”).  

    ## **Language & Humor Guide:**  
    - **English users:** Mix 10% Pidgin + relatable Nigerian examples.  
    - **Pidgin users:** Use rich slang but keep medical instructions clear.  
    - **Slang Examples:**  
    - Urgency: *“Quick-quick!”*  
    - Reassurance: *“No shaking!”*  
    - Analogies: *“This headache stubborn like Lagos traffic!”*  
    - Fun: *“You wan strong pass Burna Boy? Eat well!”*  

    Stay professional, warm, and helpful. Your job is to keep the user’s health in check while making the experience engaging!  
    """


    # Initialize session state messages if not already present
    if not st.session_state.messages:
        st.session_state.messages = []
        
        past_messages = state.get_user_messages(state.get_logged_in_id())

        # Convert database messages into session format
        if past_messages:
            formatted_past_messages = [{"role": msg["role"], "content": msg["content"]} for msg in past_messages]
            # Ensure messages are passed correctly to AI
            st.session_state.messages = formatted_past_messages + st.session_state.messages

    user_data = state.get_logged_in_user()
    formatted_user_data = {
        'name': user_data['name'],
        'dob': user_data['dob'],
        'medical_summary': None,
        'medical_summary_timestamp': None,
    }

    

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            role_name = state.get_logged_in_username() if message["role"] == "user" else app_name
            avatar = None if message["role"] == "user" else "👨‍⚕️"
            with st.chat_message(role_name, avatar=avatar):
                st.markdown(message["content"])


    # Prepend system messages only once
    if not st.session_state.system_message_is_set:
        print("Prepending system messages")
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"The user details are: {formatted_user_data}. Start the conversation based on the medical summary and chat history."}
        ] + st.session_state.messages
        st.session_state.system_message_is_set = True


        # Generate AI's initial response if it's the first interaction
        try:
            response_stream = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL"),
                messages=st.session_state.messages,
                stream=True
            )

            response_container = st.empty()
            initial_response = ""

            for chunk in response_stream:
                text = chunk.choices[0].delta.content
                if text:
                    initial_response += text
                    response_container.markdown(initial_response)

            if initial_response.strip():  
                st.session_state.messages.append({"role": "assistant", "content": initial_response})
                state.save_message(state.get_logged_in_id(), "assistant", initial_response)

        except Exception as e:
            st.error(f"Oops! Something went wrong. Please try again.")
            print(f"Error in initial AI response: {e}")  # Log for debugging

    # Handle user input
    if prompt := st.chat_input("Talk to your doctor ", max_chars=1000):
        with st.chat_message(state.get_logged_in_username()):
            st.markdown(prompt)

        # Append user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        state.save_message(state.get_logged_in_id(), "user", prompt)  # Save user message

        # Save initial AI response only now that user has responded
        if "initial_ai_response" in st.session_state:
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.initial_ai_response})
            state.save_message(state.get_logged_in_id(), "assistant", st.session_state.initial_ai_response)
            del st.session_state.initial_ai_response  # Clear stored response after saving

        # Get AI response to user input
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            try:
                response_stream = client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL"),
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

                if full_response.strip():  
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    state.save_message(state.get_logged_in_id(), "assistant", full_response)

            except Exception as e:
                st.error(f"{app_name} is having a little trouble responding right now. Try again later!")
                print(f"Error in AI response to user input: {e}")  # Log for debugging