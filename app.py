%%writefile app.py
import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load model
model = joblib.load("lightgbm_model.pkl")

# Score mapping
def probability_to_score(prob, min_score=300, max_score=800):
    return (1 - prob) * (max_score - min_score) + min_score

def decision_from_score(score):
    if score < 500:
        return "Reject"
    elif score < 650:
        return "Review"
    else:
        return "Approve"

st.title("Esubu Sacco Credit Scoring System")

# Input form
st.subheader("Enter Applicant Information")
age = st.slider("Age", 18, 70, 35)
income = st.number_input("Monthly Income (KES)", value=30000)
dependents = st.slider("Dependents", 0, 10, 2)
past_defaults = st.selectbox("Past Loan Defaults", ["Yes", "No"])

# Simulate input vector (replace with real feature logic)
features = pd.DataFrame([{
    "Age": age,
    "Monthly_Income_KES": income,
    "Dependents": dependents,
    "Past_Loan_Default": 1 if past_defaults == "Yes" else 0
}])

# Predict
if st.button("Predict Credit Score"):
    prob = model.predict_proba(features)[0][1]
    score = probability_to_score(prob)
    decision = decision_from_score(score)

    st.success(f"Credit Score: {score:.0f}")
    st.info(f"System Decision: {decision}")
