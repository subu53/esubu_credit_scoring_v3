import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
import cloudpickle
from sklearn.preprocessing import LabelEncoder

# ------------------ DATABASE ------------------
DB_FILE = 'users.db'

def create_user_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin', 'officer'))
    )''')
    conn.commit()

    # 🔐 Seed default admin if not exists
    c.execute("SELECT username FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
        conn.commit()

    conn.close()

def add_user(username, password, role):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    data = c.fetchall()
    conn.close()
    return data

def delete_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# ------------------ MODEL ------------------
@st.cache_resource
def load_model():
    return joblib.load("credit_scoring_stacked_model.pkl")

# ------------------ DECISION ENGINE ------------------
def map_probability_to_score(prob, min_score=300, max_score=800):
    return int(min_score + prob * (max_score - min_score))

def decision_logic(prob, income, repayment_history, has_collateral, missing_docs=False):
    credit_score = map_probability_to_score(prob)

    if credit_score >= 700 and repayment_history == 'good':
        decision = 'Approved'
    elif credit_score >= 600 and repayment_history in ['good', 'average'] and has_collateral:
        decision = 'Approved'
    elif 500 <= credit_score < 600 or repayment_history == 'average':
        decision = 'Review'
    else:
        decision = 'Rejected'

    if missing_docs:
        decision = 'Review'

    return credit_score, decision

def estimate_loan_amount(income, credit_score):
    if credit_score >= 750:
        multiplier = 3.0
    elif credit_score >= 700:
        multiplier = 2.5
    elif credit_score >= 650:
        multiplier = 2.0
    elif credit_score >= 600:
        multiplier = 1.5
    else:
        multiplier = 1.0

    return round(income * multiplier, -3)

def generate_message(decision, credit_score, amount=None):
    if decision == 'Approved':
        return f"✅ Congratulations! Your loan has been approved with a credit score of {credit_score}. The approved loan amount is **KES {amount:,.0f}**."
    elif decision == 'Review':
        return f"📋 Your loan application is under review. A loan officer will contact you shortly. (Credit score: {credit_score})"
    else:
        return f"❌ We're sorry, your loan application was not approved at this time. (Credit score: {credit_score})"

def run_decision_engine(model, input_df):
    prob = model.predict_proba(input_df)[0][1]

    income = input_df['monthly_income'].values[0]
    repayment_history = input_df['repayment_history'].values[0]
    has_collateral = input_df['has_collateral'].values[0]
    missing_docs = input_df['missing_documents'].values[0]

    credit_score, decision = decision_logic(prob, income, repayment_history, has_collateral, missing_docs)

    approved_loan_amount = None
    if decision == 'Approved':
        approved_loan_amount = estimate_loan_amount(income, credit_score)

    message = generate_message(decision, credit_score, approved_loan_amount)

    return {
        'credit_score': credit_score,
        'decision': decision,
        'loan_amount': approved_loan_amount,
        'probability': round(prob, 4),
        'message': message
    }

# ------------------ UI ------------------
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = login_user(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

def loan_application():
    st.title("Loan Application")
    st.write("Enter the following details:")

    age = st.selectbox("Age Group", ['18-24', '25-34', '35-44', '45+'])
    gender = st.selectbox("Gender", ['Male', 'Female'])
    region = st.selectbox("Region", ['Urban', 'Suburban', 'Rural'])
    income = st.number_input("Monthly Income (KES)", min_value=1000)
    employment = st.selectbox("Employment Status", ['Unemployed', 'Self-employed', 'Part-time', 'Full-time'])
    grade = st.selectbox("KCSE Grade", ['E', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A'])
    adaptability = st.selectbox("Learning Adaptability", ['Low', 'Moderate', 'High'])
    support_services = st.radio("Do you use support services?", ['Yes', 'No'])
    psychosocial = st.selectbox("Psychosocial Support", ['Low', 'Moderate', 'High'])
    repayment = st.selectbox("Repayment History", ['good', 'average', 'poor'])
    collateral = st.checkbox("Has Collateral")
    missing_docs = st.checkbox("Missing Documents")

    if st.button("Submit Application"):
        input_data = pd.DataFrame([{
            'Age_Group': age,
            'Gender': gender,
            'Region': region,
            'monthly_income': income,
            'Employment_Status': employment,
            'KCSE_Grade': grade,
            'Learning_Adaptability': adaptability,
            'Support_Services_Usage': support_services,
            'Psychosocial_Support': psychosocial,
            'repayment_history': repayment,
            'has_collateral': collateral,
            'missing_documents': missing_docs
        }])

        for col in input_data.select_dtypes(include='object').columns:
            le = LabelEncoder()
            input_data[col] = le.fit_transform(input_data[col])

        results = run_decision_engine(model, input_data)
        st.subheader("Decision Result")
        st.write(results['message'])
        st.write(f"Probability of Approval: {results['probability']*100:.2f}%")

        if st.session_state.role == "officer" and results['decision'] == 'Review':
            st.warning("This application requires manual review. You can override the system's decision below.")
            override = st.selectbox("Override Decision", ['No Action', 'Approve', 'Reject'])
            if override != 'No Action':
                st.success(f"Decision overridden to: {override}")

def admin_dashboard():
    st.title("Admin Dashboard")
    st.subheader("User Management")

    with st.expander("Add New User"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["admin", "officer"])
        if st.button("Add User"):
            add_user(new_username, new_password, role)
            st.success("User added successfully")

    st.subheader("All Users")
    users = get_all_users()
    for user, role in users:
        col1, col2 = st.columns([3,1])
        col1.write(f"{user} ({role})")
        if col2.button("Delete", key=user):
            delete_user(user)
            st.warning(f"Deleted user: {user}")
            st.experimental_rerun()

# ------------------ MAIN ------------------
def main():
    create_user_table()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()

        if st.session_state.role == "officer":
            loan_application()
        elif st.session_state.role == "admin":
            admin_dashboard()
            loan_application()

if __name__ == "__main__":
    main()
