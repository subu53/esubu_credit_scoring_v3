import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
import cloudpickle
import pickle
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
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

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
    try:
        return joblib.load("credit_scoring_stacked_model.pkl")
    except FileNotFoundError:
        st.error("Model file not found. Please ensure 'credit_scoring_stacked_model.pkl' is in the app directory.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

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
    if model is None:
        return None
        
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

# ------------------ UI FUNCTIONS ------------------
def login_page():
    st.title("🏦 Credit Scoring System Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login")
        
        if login_submitted:
            if username and password:
                role = login_user(username, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

def loan_application():
    st.title("💰 Loan Application")
    st.write("Please fill in the following details for your loan application:")

    with st.form("loan_application_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.selectbox("Age Group", ['18-24', '25-34', '35-44', '45+'])
            gender = st.selectbox("Gender", ['Male', 'Female'])
            region = st.selectbox("Region", ['Urban', 'Suburban', 'Rural'])
            income = st.number_input("Monthly Income (KES)", min_value=1000, value=50000)
            employment = st.selectbox("Employment Status", ['Unemployed', 'Self-employed', 'Part-time', 'Full-time'])
            grade = st.selectbox("KCSE Grade", ['E', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A'])
        
        with col2:
            adaptability = st.selectbox("Learning Adaptability", ['Low', 'Moderate', 'High'])
            support_services = st.radio("Do you use support services?", ['Yes', 'No'])
            psychosocial = st.selectbox("Psychosocial Support", ['Low', 'Moderate', 'High'])
            repayment = st.selectbox("Repayment History", ['good', 'average', 'poor'])
            collateral = st.checkbox("Has Collateral")
            missing_docs = st.checkbox("Missing Documents")

        submitted = st.form_submit_button("Submit Application")
        
        if submitted:
            model = load_model()
            if model is None:
                st.error("Unable to process application. Model not available.")
                return
                
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

            # Encode categorical variables
            for col in input_data.select_dtypes(include='object').columns:
                le = LabelEncoder()
                input_data[col] = le.fit_transform(input_data[col])

            results = run_decision_engine(model, input_data)
            
            if results:
                st.markdown("---")
                st.subheader("📋 Decision Result")
                st.markdown(results['message'])
                st.info(f"**Probability of Approval:** {results['probability']*100:.2f}%")

                # Officer override option
                if st.session_state.role == "officer" and results['decision'] == 'Review':
                    st.warning("⚠️ This application requires manual review. You can override the system's decision below.")
                    override = st.selectbox("Override Decision", ['No Action', 'Approve', 'Reject'])
                    if override != 'No Action':
                        if st.button("Confirm Override"):
                            st.success(f"✅ Decision overridden to: {override}")

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    
    tab1, tab2 = st.tabs(["👥 User Management", "💼 Loan Application"])
    
    with tab1:
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["admin", "officer"])
            add_submitted = st.form_submit_button("Add User")
            
            if add_submitted:
                if new_username and new_password:
                    if add_user(new_username, new_password, role):
                        st.success(f"✅ User '{new_username}' added successfully!")
                    else:
                        st.error("❌ Username already exists!")
                else:
                    st.warning("Please fill in all fields")

        st.markdown("---")
        st.subheader("Current Users")
        users = get_all_users()
        
        if users:
            for i, (user, user_role) in enumerate(users):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{user}** ({user_role})")
                with col2:
                    st.write("🔒 Admin" if user_role == "admin" else "👤 Officer")
                with col3:
                    if user != "admin":  # Prevent deleting the default admin
                        if st.button("🗑️ Delete", key=f"delete_{user}_{i}"):
                            delete_user(user)
                            st.success(f"User '{user}' deleted!")
                            st.rerun()
                st.markdown("---")
        else:
            st.info("No users found")
    
    with tab2:
        loan_application()

# ------------------ MAIN ------------------
def main():
    # Initialize database
    create_user_table()
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

    # Main app logic
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar with user info and logout
        with st.sidebar:
            st.success(f"✅ Logged in as **{st.session_state.username}**")
            st.info(f"Role: **{st.session_state.role.title()}**")
            st.markdown("---")
            if st.button("🚪 Logout", type="primary"):
                logout()

        # Main content based on role
        if st.session_state.role == "admin":
            admin_dashboard()
        elif st.session_state.role == "officer":
            loan_application()

if __name__ == "__main__":
    main()
