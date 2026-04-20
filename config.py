import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'invoice_business.db')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    BCRYPT_ROUNDS = 12
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    
    # Application
    APP_NAME = "Professional Invoice System"
    APP_VERSION = "2.0.0"
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Company')
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Create directories
    for dir_path in [BACKUP_DIR, LOG_DIR]:
        os.makedirs(dir_path, exist_ok=True)