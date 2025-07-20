import bcrypt
import logging
import sqlite3
from datetime import datetime
from config import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utilities for password hashing and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

class DatabaseUtils:
    """Database utilities with enhanced error handling and logging"""
    
    @staticmethod
    def get_connection():
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @staticmethod
    def execute_query(query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False):
        """Execute database query with proper error handling"""
        try:
            with DatabaseUtils.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise

def log_user_action(username: str, action: str, details: str = ""):
    """Log user actions for audit trail"""
    timestamp = datetime.now().isoformat()
    logger.info(f"USER_ACTION - {timestamp} - {username} - {action} - {details}")

def validate_input(data: dict, required_fields: list) -> tuple:
    """Validate input data and return (is_valid, missing_fields)"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    return len(missing_fields) == 0, missing_fields
