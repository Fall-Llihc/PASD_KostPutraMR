import streamlit as st
import sqlite3
import hashlib
import datetime

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 username TEXT PRIMARY KEY,
                 password TEXT)''')
    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                 username TEXT,
                 action TEXT,
                 timestamp TEXT,
                 metadata TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    if data and data[0] == password:
        return True
    return False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- HISTORY ----------
def add_history(username, action, metadata=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO history (username, action, timestamp, metadata) VALUES (?, ?, ?, ?)",
              (username, action, timestamp, metadata))
    conn.commit()
    conn.close()

def get_history(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT action, timestamp, metadata FROM history WHERE username = ?", (username,))
    data = c.fetchall()
    conn.close()
    return data


def login():
    menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])
    if menu == "Sign Up":
        st.subheader("Create Account")
        with st.form(key="sign_up", enter_to_submit=False):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            submit = st.form_submit_button('Sign Up')
        if submit:
            if not new_user or not new_pass:
                st.warning('Please fill both fields.')
            else:
                try:
                    add_user(new_user, hash_password(new_pass))
                    st.success("Account created. Go to Login.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")
    elif menu == "Login":
        st.subheader("Login")
        with st.form(key="login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button('Login')
        if submit:
            if authenticate_user(username, hash_password(password)):
                st.success(f"Welcome, {username}!")
                st.session_state["user"] = username
                st.session_state.authenticated = True
                return True
            else:
                st.error("Invalid credentials.")
    return False


def logout():
    st.session_state.authenticated = False


