import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# ----------- Initialize Session State -----------
if 'authorized' not in st.session_state:
    st.session_state.authorized = False
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'fernet_key' not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}

# ----------- Initialize Encryption -----------
fernet = Fernet(st.session_state.fernet_key)

# ----------- Sample Login Credentials -----------
login_credentials = {"admin": "admin123"}

# ----------- Helper Functions -----------
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_text(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(cipher):
    return fernet.decrypt(cipher.encode()).decode()

# ----------- Login Page -----------
def login_page():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_credentials.get(username) == password:
            st.session_state.authorized = True
            st.session_state.failed_attempts = 0
            st.success("Logged in successfully!")
        else:
            st.session_state.failed_attempts += 1
            st.error("Invalid credentials")
            if st.session_state.failed_attempts >= 3:
                st.warning("Too many failed attempts. Please restart the app.")

# ----------- Insert Data Page -----------
def insert_data_page():
    st.title("📦 Insert Secure Data")
    key = st.text_input("Enter a unique key for this data")
    text = st.text_area("Enter your secret data")
    passkey = st.text_input("Enter a passkey", type="password")

    if st.button("Store Securely"):
        if not key or not text or not passkey:
            st.warning("All fields are required.")
        elif key in st.session_state.stored_data:
            st.warning("This key already exists. Choose a new one.")
        else:
            encrypted_text = encrypt_text(text)
            hashed_passkey = hash_passkey(passkey)
            st.session_state.stored_data[key] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            st.success("Your data has been securely stored!")

# ----------- Retrieve Data Page -----------
def retrieve_data_page():
    if not st.session_state.authorized:
        login_page()
        return

    st.title("🔓 Retrieve Secure Data")
    key = st.text_input("Enter your unique data key")
    passkey = st.text_input("Enter your passkey", type="password")

    if st.button("Retrieve"):
        if not key or not passkey:
            st.warning("Both key and passkey are required.")
        elif key in st.session_state.stored_data:
            stored_passkey = st.session_state.stored_data[key]["passkey"]
            if hash_passkey(passkey) == stored_passkey:
                decrypted_text = decrypt_text(st.session_state.stored_data[key]["encrypted_text"])
                st.success("Data decrypted successfully!")
                st.code(decrypted_text)
                st.session_state.failed_attempts = 0
            else:
                st.session_state.failed_attempts += 1
                attempts_left = 3 - st.session_state.failed_attempts
                st.error(f"Incorrect passkey. Attempts left: {attempts_left}")
                if st.session_state.failed_attempts >= 3:
                    st.session_state.authorized = False
                    st.warning("Too many failed attempts. Logged out.")
        else:
            st.warning("No data found for this key.")

# ----------- Main App -----------
def main():
    st.sidebar.title("🔐 Secure Storage System")
    if st.session_state.get('authorized', False):
        if st.sidebar.button("Logout"):
            st.session_state.authorized = False
            st.success("Logged out successfully.")

    choice = st.sidebar.radio("Navigate", ["Home", "Insert Data", "Retrieve Data"])

    if choice == "Home":
        st.title("🔒 Welcome to the Secure Data Encryption System")
        st.write("Choose an option from the sidebar to get started.")
    elif choice == "Insert Data":
        insert_data_page()
    elif choice == "Retrieve Data":
        retrieve_data_page()

if __name__ == "__main__":
    main()
