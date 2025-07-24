from typing import Optional, Union
from dataclasses import dataclass
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, precision_score

def load_model(model_path: str) -> object:
    """
    Load a machine learning model from the specified file path.
    
    Args:
        model_path (str): Path to the model file
        
    Returns:
        object: Loaded model object
        
    Raises:
        FileNotFoundError: If the model file doesn't exist
        RuntimeError: If there's an error loading the model
    """
    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"Model file not found at path: {model_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess input data by removing missing values and extracting features.
    
    Args:
        data (pd.DataFrame): Input dataframe containing raw data
        
    Returns:
        pd.DataFrame: Preprocessed features dataframe
        
    Raises:
        TypeError: If input is not a pandas DataFrame
        ValueError: If dataframe operations fail
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame")
    
    try:
        dataframe = data.copy()
        dataframe = dataframe.dropna()
        features = dataframe.drop('target', axis=1) if 'target' in dataframe.columns else dataframe
        return features
    except Exception as e:
        raise ValueError(f"Error preprocessing data: {str(e)}")

class CreditScorer:
    """
    A credit scoring model wrapper for making predictions on loan applications.
    
    This class loads a pre-trained machine learning model and provides
    methods to predict credit risk based on applicant features.
    """
    
    def __init__(self, model_path: str, threshold: float = 0.5):
        """
        Initialize the CreditScorer with a model and prediction threshold.
        
        Args:
            model_path (str): Path to the trained model file
            threshold (float): Decision threshold for binary classification (default: 0.5)
        """
        self.model = load_model(model_path)
        self.threshold = threshold
    
    def predict(self, features: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Make credit risk predictions on input features.
        
        Args:
            features: Input features for prediction
            
        Returns:
            np.ndarray: Binary predictions (True/False)
            
        Raises:
            ValueError: If model doesn't have predict_proba method
            TypeError: If features are not in expected format
            RuntimeError: If prediction fails
        """
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model must have 'predict_proba' method for probability predictions")
            
        if not isinstance(features, (pd.DataFrame, np.ndarray)):
            raise TypeError("Features must be a pandas DataFrame or numpy array")
            
        try:
            probabilities = self.model.predict_proba(features)[:, 1]
            return probabilities > self.threshold
        except Exception as e:
            raise RuntimeError(f"Error during prediction: {str(e)}")

# Note: Unsafe pickle loading function has been removed for security reasons
# Use joblib.load() or other safe serialization methods instead

@dataclass
class ScoringWeights:
    """Configuration class for credit scoring weights and thresholds."""
    
    # Age scoring
    age_young_penalty: int = -10
    age_senior_penalty: int = -5
    age_optimal_bonus: int = 5
    age_young_threshold: int = 25
    age_senior_threshold: int = 65
    
    # Income scoring
    income_low_penalty: int = -20
    income_high_bonus: int = 20
    income_medium_bonus: int = 10
    income_low_threshold: int = 30000
    income_high_threshold: int = 100000
    
    # Credit history scoring
    credit_good_bonus: int = 25
    credit_fair_bonus: int = 10
    credit_poor_penalty: int = -15
    
    # Employment scoring
    employment_employed_bonus: int = 15
    employment_self_employed_bonus: int = 10
    employment_unemployed_penalty: int = -20
    
    # Debt ratio scoring
    debt_high_penalty: int = -25
    debt_low_bonus: int = 15
    debt_medium_bonus: int = 5
    debt_high_threshold: float = 0.4
    debt_low_threshold: float = 0.2
    
    # Score limits
    base_score: int = 50
    min_score: int = 0
    max_score: int = 100


def score_age(age: int, weights: ScoringWeights = ScoringWeights()) -> int:
    """
    Calculate credit score component based on applicant's age.
    
    Args:
        age (int): Applicant's age in years
        weights (ScoringWeights): Scoring configuration
        
    Returns:
        int: Age-based score component
        
    Raises:
        ValueError: If age is not a positive integer
    """
    if not isinstance(age, int) or age <= 0:
        raise ValueError("Age must be a positive integer")
        
    if age < weights.age_young_threshold:
        return weights.age_young_penalty
    elif age > weights.age_senior_threshold:
        return weights.age_senior_penalty
    else:
        return weights.age_optimal_bonus


def score_income(income: Union[int, float], weights: ScoringWeights = ScoringWeights()) -> int:
    """
    Calculate credit score component based on applicant's income.
    
    Args:
        income (Union[int, float]): Applicant's annual income
        weights (ScoringWeights): Scoring configuration
        
    Returns:
        int: Income-based score component
        
    Raises:
        ValueError: If income is negative
    """
    if not isinstance(income, (int, float)) or income < 0:
        raise ValueError("Income must be a non-negative number")
        
    if income < weights.income_low_threshold:
        return weights.income_low_penalty
    elif income > weights.income_high_threshold:
        return weights.income_high_bonus
    else:
        return weights.income_medium_bonus


def score_credit_history(credit_history: str, weights: ScoringWeights = ScoringWeights()) -> int:
    """
    Calculate credit score component based on credit history.
    
    Args:
        credit_history (str): Credit history category ('good', 'fair', or other)
        weights (ScoringWeights): Scoring configuration
        
    Returns:
        int: Credit history-based score component
        
    Raises:
        ValueError: If credit_history is not a string
    """
    if not isinstance(credit_history, str):
        raise ValueError("Credit history must be a string")
        
    credit_history = credit_history.lower().strip()
    
    if credit_history == 'good':
        return weights.credit_good_bonus
    elif credit_history == 'fair':
        return weights.credit_fair_bonus
    else:
        return weights.credit_poor_penalty


def score_employment(employment_status: str, weights: ScoringWeights = ScoringWeights()) -> int:
    """
    Calculate credit score component based on employment status.
    
    Args:
        employment_status (str): Employment status ('employed', 'self-employed', or other)
        weights (ScoringWeights): Scoring configuration
        
    Returns:
        int: Employment-based score component
        
    Raises:
        ValueError: If employment_status is not a string
    """
    if not isinstance(employment_status, str):
        raise ValueError("Employment status must be a string")
        
    employment_status = employment_status.lower().strip()
    
    if employment_status == 'employed':
        return weights.employment_employed_bonus
    elif employment_status == 'self-employed':
        return weights.employment_self_employed_bonus
    else:
        return weights.employment_unemployed_penalty


def score_debt_ratio(debt_ratio: float, weights: ScoringWeights = ScoringWeights()) -> int:
    """
    Calculate credit score component based on debt-to-income ratio.
    
    Args:
        debt_ratio (float): Debt-to-income ratio (0.0 to 1.0)
        weights (ScoringWeights): Scoring configuration
        
    Returns:
        int: Debt ratio-based score component
        
    Raises:
        ValueError: If debt_ratio is not between 0 and 1
    """
    if not isinstance(debt_ratio, (int, float)) or not (0 <= debt_ratio <= 1):
        raise ValueError("Debt ratio must be a number between 0 and 1")
        
    if debt_ratio > weights.debt_high_threshold:
        return weights.debt_high_penalty
    elif debt_ratio < weights.debt_low_threshold:
        return weights.debt_low_bonus
    else:
        return weights.debt_medium_bonus


def calculate_credit_score(
    age: int,
    income: Union[int, float],
    credit_history: str,
    employment_status: str,
    debt_ratio: float,
    loan_amount: Union[int, float],
    collateral: bool,
    previous_defaults: int,
    weights: ScoringWeights = ScoringWeights()
) -> int:
    """
    Calculate comprehensive credit score based on multiple applicant factors.
    
    This function combines various scoring components to produce a final
    credit score between 0 and 100. Higher scores indicate lower credit risk.
    
    Args:
        age (int): Applicant's age in years
        income (Union[int, float]): Annual income
        credit_history (str): Credit history category ('good', 'fair', 'poor')
        employment_status (str): Employment status ('employed', 'self-employed', 'unemployed')
        debt_ratio (float): Debt-to-income ratio (0.0 to 1.0)
        loan_amount (Union[int, float]): Requested loan amount
        collateral (bool): Whether collateral is provided
        previous_defaults (int): Number of previous loan defaults
        weights (ScoringWeights): Scoring configuration parameters
        
    Returns:
        int: Final credit score (0-100)
        
    Raises:
        ValueError: If any input parameters are invalid
    """
    if not isinstance(loan_amount, (int, float)) or loan_amount < 0:
        raise ValueError("Loan amount must be a non-negative number")
    if not isinstance(collateral, bool):
        raise ValueError("Collateral must be a boolean value")
    if not isinstance(previous_defaults, int) or previous_defaults < 0:
        raise ValueError("Previous defaults must be a non-negative integer")
    
    # Calculate individual score components
    score = weights.base_score
    score += score_age(age, weights)
    score += score_income(income, weights)
    score += score_credit_history(credit_history, weights)
    score += score_employment(employment_status, weights)
    score += score_debt_ratio(debt_ratio, weights)
    
    # Additional scoring factors
    if collateral:
        score += 10  # Collateral bonus
    
    # Penalty for previous defaults
    score -= previous_defaults * 5
    
    # Loan amount impact (higher amounts = higher risk)
    if loan_amount > 100000:
        score -= 10
    elif loan_amount > 50000:
        score -= 5
    
    # Clamp score to valid range
    final_score = max(weights.min_score, min(weights.max_score, score))
    return final_score

def calculate_probability_score(
    probability: float,
    min_score: int = 300,
    max_score: int = 800
) -> float:
    """
    Transform a probability score (0-1) to a credit score range.
    
    This function converts a model's probability output to a more interpretable
    credit score. Higher probabilities of default result in lower credit scores.
    
    Args:
        probability (float): Default probability from model (0.0 to 1.0)
        min_score (int): Minimum possible credit score (default: 300)
        max_score (int): Maximum possible credit score (default: 800)
        
    Returns:
        float: Transformed credit score within the specified range
        
    Raises:
        ValueError: If probability is not between 0 and 1, or if score range is invalid
    """
    if not isinstance(probability, (int, float)) or not (0 <= probability <= 1):
        raise ValueError("Probability must be a number between 0 and 1")
    
    if not isinstance(min_score, int) or not isinstance(max_score, int):
        raise ValueError("Score limits must be integers")
        
    if min_score >= max_score:
        raise ValueError("Maximum score must be greater than minimum score")
    
    # Transform probability to credit score (inverse relationship)
    score = (1 - probability) * (max_score - min_score) + min_score
    return score
