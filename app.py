import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
from typing import Tuple, Union

# Configure Streamlit for production
st.set_page_config(
    page_title="Esubu Credit Scoring",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load model with error handling
@st.cache_resource
def load_model():
    """Load the trained model with caching for better performance."""
    model_path = "lightgbm_model.pkl"
    if not os.path.exists(model_path):
        st.error(f"❌ Model file '{model_path}' not found!")
        return None
    
    try:
        model = joblib.load(model_path)
        st.success("✅ Model loaded successfully!")
        return model
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None

model = load_model()

# Score mapping functions
def probability_to_score(prob: float, min_score: int = 300, max_score: int = 800) -> float:
    """Convert probability to credit score."""
    return (1 - prob) * (max_score - min_score) + min_score

def decision_from_score(score: float) -> Tuple[str, str]:
    """Determine decision and color based on score."""
    if score < 500:
        return "Reject", "🔴"
    elif score < 650:
        return "Review", "🟡"
    else:
        return "Approve", "🟢"

# Main app interface
st.title("💳 Esubu Sacco Credit Scoring System")
st.markdown("---")

# Check if model is loaded
if model is None:
    st.error("❌ Cannot proceed - Model not loaded properly!")
    st.stop()

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Enter Applicant Information")
    
    # Input form with better validation
    age = st.slider("Age", 18, 70, 35, help="Applicant's age in years")
    income = st.number_input(
        "Monthly Income (KES)", 
        min_value=0, 
        max_value=1000000, 
        value=30000,
        step=1000,
        help="Monthly income in Kenyan Shillings"
    )
    dependents = st.slider(
        "Number of Dependents", 
        0, 10, 2,
        help="Number of people financially dependent on the applicant"
    )
    past_defaults = st.selectbox(
        "Past Loan Defaults", 
        ["No", "Yes"],
        help="Has the applicant defaulted on previous loans?"
    )

with col2:
    st.subheader("📊 Application Summary")
    st.metric("Age", f"{age} years")
    st.metric("Monthly Income", f"KES {income:,}")
    st.metric("Dependents", dependents)
    st.metric("Past Defaults", past_defaults)

st.markdown("---")

# Prediction section
if st.button("🔍 Predict Credit Score", type="primary", use_container_width=True):
    try:
        # Create feature vector
        features = pd.DataFrame([{
            "Age": age,
            "Monthly_Income_KES": income,
            "Dependents": dependents,
            "Past_Loan_Default": 1 if past_defaults == "Yes" else 0
        }])
        
        # Make prediction
        prob = model.predict_proba(features)[0][1]
        score = probability_to_score(prob)
        decision, emoji = decision_from_score(score)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Credit Score",
                value=f"{score:.0f}",
                delta=f"{score-500:.0f} from threshold"
            )
        
        with col2:
            st.metric(
                label="Default Risk",
                value=f"{prob*100:.1f}%"
            )
            
        with col3:
            st.metric(
                label="Decision",
                value=f"{emoji} {decision}"
            )
        
        # Risk assessment
        if decision == "Approve":
            st.success(f"✅ **APPROVED** - Low risk applicant with score {score:.0f}")
        elif decision == "Review":
            st.warning(f"⚠️ **REVIEW REQUIRED** - Moderate risk with score {score:.0f}")
        else:
            st.error(f"❌ **REJECTED** - High risk applicant with score {score:.0f}")
            
    except Exception as e:
        st.error(f"❌ Prediction error: {str(e)}")
        st.info("Please check your inputs and try again.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>🏦 Esubu Sacco Credit Scoring System | Powered by Machine Learning</p>
    </div>
    """, 
    unsafe_allow_html=True
)
