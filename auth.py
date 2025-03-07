import streamlit as st
import state
import datetime

def show_auth_page():
    st.title('Welcome to ' + st.secrets["APP_NAME"])
    st.write(st.secrets["APP_DESCRIPTION"])
    st.write('\n\n\n\n\n')
    
    tab1, tab2 = st.tabs(["Login", "Create an Account"])
    
    with tab1:
        st.subheader("Login")
        phone = st.text_input("Phone Number", max_chars=11)
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if not phone or not password:
                st.error("Both phone number and password are required!")
            elif state.authenticate_user(phone, password):
                st.success("Login successful!")
                st.rerun()  # Rerun the app to update UI
            else:
                st.error("Invalid phone number or password")

    with tab2:
        st.subheader("Create an Account")
        reg_name = st.text_input("What is your name?", max_chars=40)
        
        today = datetime.date.today()

        # Restrict date selection to past dates only
        min_birth_date = today.replace(year=today.year - 12)
        max_birth_date = today.replace(year=today.year - 100)


        reg_phone = st.text_input("Your Phone number", max_chars=11, key="reg_phone")
        reg_password = st.text_input("Password/Pin", type="password", key="reg_password")

        # Gender selection
        reg_gender = st.radio("Select your gender:", ["Male", "Female"], horizontal=True)
        reg_dob = st.date_input("When were you born?", max_value=min_birth_date, min_value=max_birth_date)

        if st.button("Register"):
            if not reg_name or not reg_dob or not reg_phone or not reg_password or not reg_gender:
                st.error("All fields are required!")
            else:
                # Check phone
                if state.check_phone_exists(reg_phone):
                    st.error("Phone number already registered")
                    return

                # Age validation: must be at least 12 years old
                if reg_dob > min_birth_date:
                    st.error("You must be at least 12 years old to register.")
                elif state.register_user(reg_phone, reg_password, reg_name, reg_dob, reg_gender):
                    st.success("Registration successful! Logging in...")
                    st.rerun()  # Rerun to update UI
                else:
                    st.error("An error occurred while registering. Try again")