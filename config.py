import os
from pathlib import Path

# Database configuration
DB_FILE = os.getenv('DB_FILE', 'users.db')
DB_PATH = Path(DB_FILE)

# Security configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))

# Default admin credentials (change in production)
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')

# Model paths
MODEL_PATH = os.getenv('MODEL_PATH', 'credit_scoring_stacked_model.pkl')
PIPELINE_PATH = os.getenv('PIPELINE_PATH', 'preprocessing_pipeline.pkl')

# Application settings
APP_TITLE = os.getenv('APP_TITLE', '🏦 Esubu AI Credit Scoring System')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
