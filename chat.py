import streamlit as st
import os
import state
from groq import Groq

def show_chat_page():
    app_name = os.getenv("APP_NAME")
    
    st.title(app_name)
    st.write(f"{state.get_logged_in_username()}'s personal AI doctor 👨‍⚕️")

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    system_prompt = """
    You are AyoMed, a friendly Nigerian medical AI acting as a virtual doctor. You provide expert but relatable healthcare advice with a mix of humor, Nigerian slang, and cultural references.  

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

    # Initializing the system prompt for the chatbot
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "assistant",
            "content": f"Hi {state.get_logged_in_first_name()}, how how are you today?"
        }]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            role_name = message["role"]
            avatar = None
            if (message["role"] == "user"):
                role_name = state.get_logged_in_username()
            else:
                avatar="👨‍⚕️"
                role_name = app_name
            with st.chat_message(role_name, avatar=avatar):
                st.markdown(message["content"])

    # Handle user input and Groq response
    if prompt := st.chat_input("Your response", max_chars=1000):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message(state.get_logged_in_username()):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="👨‍⚕️"):
            response_stream = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL"),
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True  # Enable streaming
            )

            response_container = st.empty()  # Placeholder for the streamed text
            full_response = ""

            for chunk in response_stream:
                text = chunk.choices[0].delta.content  # Extract streamed content
                if text:
                    full_response += text
                    response_container.markdown(full_response)  # Update the display

            st.session_state.messages.append({"role": "assistant", "content": full_response})

