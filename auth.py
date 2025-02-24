import streamlit as st
import state
import os
import datetime

def show_auth_page():
    st.title('Welcome to ' + os.getenv("APP_NAME", "Our App"))
    st.write(os.getenv("APP_DESCRIPTION"))
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
        reg_name = st.text_input("Name", max_chars=40)
        
        today = datetime.date.today()

        # Restrict date selection to past dates only
        min_birth_date = today.replace(year=today.year - 12)
        max_birth_date = today.replace(year=today.year - 100)

        reg_dob = st.date_input("Date of Birth", max_value=min_birth_date, min_value=max_birth_date)

        reg_phone = st.text_input("Phone Number", max_chars=11, key="reg_phone")
        reg_password = st.text_input("Password", type="password", key="reg_password")

        if st.button("Register"):
            if not reg_name or not reg_dob or not reg_phone or not reg_password:
                st.error("All fields are required!")
            else:
                # Age validation: must be at least 12 years old
                min_birth_date = today.replace(year=today.year - 12)

                if reg_dob > min_birth_date:
                    st.error("You must be at least 12 years old to register.")
                elif state.register_user(reg_phone, reg_password, reg_name, reg_dob):
                    st.success("Registration successful! Logging in...")
                    st.rerun()  # Rerun to update UI
                else:
                    st.error("Phone number already registered")