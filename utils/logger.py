import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import traceback
import json

class Logger:
    """Centralized logging system for the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.log_dir = "logs"
        self._create_log_directory()
        self._setup_loggers()
    
    def _create_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # Application Logger
        self.app_logger = logging.getLogger('app')
        self.app_logger.setLevel(logging.DEBUG)
        app_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.app_logger.addHandler(app_handler)
        
        # Error Logger
        self.error_logger = logging.getLogger('error')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'error.log'),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.error_logger.addHandler(error_handler)
        
        # Database Logger
        self.db_logger = logging.getLogger('database')
        self.db_logger.setLevel(logging.INFO)
        db_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'database.log'),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        db_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.db_logger.addHandler(db_handler)
        
        # User Activity Logger
        self.user_logger = logging.getLogger('user')
        self.user_logger.setLevel(logging.INFO)
        user_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'user_activity.log'),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        user_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.user_logger.addHandler(user_handler)
        
        # Performance Logger
        self.perf_logger = logging.getLogger('performance')
        self.perf_logger.setLevel(logging.INFO)
        perf_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'performance.log'),
            maxBytes=5*1024*1024,
            backupCount=3
        )
        perf_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.perf_logger.addHandler(perf_handler)
        
        # Security Logger
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.WARNING)
        security_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'security.log'),
            maxBytes=10*1024*1024,
            backupCount=5
        )
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.security_logger.addHandler(security_handler)
    
    # Application Logs
    def app_info(self, message):
        """Log application info"""
        self.app_logger.info(message)
        print(f"[INFO] {message}")
    
    def app_debug(self, message):
        """Log application debug"""
        self.app_logger.debug(message)
        print(f"[DEBUG] {message}")
    
    def app_warning(self, message):
        """Log application warning"""
        self.app_logger.warning(message)
        print(f"[WARNING] {message}")
    
    def app_error(self, message, exc_info=False):
        """Log application error"""
        self.app_logger.error(message, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)
        print(f"[ERROR] {message}")
    
    # Database Logs
    def db_query(self, query, params=None):
        """Log database queries"""
        log_msg = f"QUERY: {query}"
        if params:
            log_msg += f" | PARAMS: {params}"
        self.db_logger.debug(log_msg)
    
    def db_operation(self, operation, table, record_id=None):
        """Log database operations"""
        log_msg = f"OPERATION: {operation} | TABLE: {table}"
        if record_id:
            log_msg += f" | ID: {record_id}"
        self.db_logger.info(log_msg)
    
    def db_error(self, error, query=None):
        """Log database errors"""
        log_msg = f"DB ERROR: {error}"
        if query:
            log_msg += f" | QUERY: {query}"
        self.db_logger.error(log_msg)
        self.error_logger.error(log_msg)
    
    # User Activity Logs
    def user_login(self, username, success=True):
        """Log user login attempts"""
        status = "SUCCESS" if success else "FAILED"
        self.user_logger.info(f"LOGIN {status} - User: {username}")
        if not success:
            self.security_logger.warning(f"Failed login attempt for user: {username}")
    
    def user_logout(self, username):
        """Log user logout"""
        self.user_logger.info(f"LOGOUT - User: {username}")
    
    def user_action(self, username, action, module, details=None):
        """Log user actions"""
        log_msg = f"ACTION: {action} | MODULE: {module} | USER: {username}"
        if details:
            log_msg += f" | DETAILS: {details}"
        self.user_logger.info(log_msg)
    
    def user_error(self, username, action, error):
        """Log user errors"""
        log_msg = f"USER ERROR - User: {username} | Action: {action} | Error: {error}"
        self.user_logger.error(log_msg)
        self.error_logger.error(log_msg)
    
    # Performance Logs
    def perf_start(self, operation):
        """Start performance tracking"""
        self.perf_logger.info(f"START - {operation}")
    
    def perf_end(self, operation, duration_ms):
        """End performance tracking"""
        self.perf_logger.info(f"END - {operation} | Duration: {duration_ms}ms")
    
    def perf_measurement(self, operation, value, unit="ms"):
        """Log performance measurement"""
        self.perf_logger.info(f"MEASURE - {operation}: {value}{unit}")
    
    # Security Logs
    def security_alert(self, alert_type, details):
        """Log security alerts"""
        log_msg = f"ALERT: {alert_type} | DETAILS: {details}"
        self.security_logger.warning(log_msg)
    
    def security_breach(self, breach_type, details):
        """Log security breaches"""
        log_msg = f"BREACH: {breach_type} | DETAILS: {details}"
        self.security_logger.error(log_msg)
        self.error_logger.error(f"SECURITY BREACH: {log_msg}")
    
    def permission_denied(self, username, action, required_permission):
        """Log permission denied events"""
        log_msg = f"PERMISSION DENIED - User: {username} | Action: {action} | Required: {required_permission}"
        self.security_logger.warning(log_msg)
    
    # Exception Handling
    def log_exception(self, exc, context=""):
        """Log exceptions with traceback"""
        error_msg = f"EXCEPTION: {str(exc)}"
        if context:
            error_msg = f"{context} - {error_msg}"
        self.app_error(error_msg)
        self.error_logger.error(traceback.format_exc())
    
    # System Logs
    def system_start(self):
        """Log system startup"""
        self.app_info("=" * 60)
        self.app_info("SYSTEM STARTUP")
        self.app_info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.app_info("=" * 60)
    
    def system_shutdown(self):
        """Log system shutdown"""
        self.app_info("=" * 60)
        self.app_info("SYSTEM SHUTDOWN")
        self.app_info(f"Shutdown Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.app_info("=" * 60)
    
    def module_load(self, module_name):
        """Log module loading"""
        self.app_debug(f"Module loaded: {module_name}")
    
    def module_error(self, module_name, error):
        """Log module errors"""
        self.app_error(f"Module: {module_name} - Error: {error}")
    
    # Data Export/Import Logs
    def data_export(self, export_type, record_count, file_path):
        """Log data exports"""
        log_msg = f"EXPORT: {export_type} | Records: {record_count} | File: {file_path}"
        self.user_logger.info(log_msg)
    
    def data_import(self, import_type, record_count, file_path):
        """Log data imports"""
        log_msg = f"IMPORT: {import_type} | Records: {record_count} | File: {file_path}"
        self.user_logger.info(log_msg)
    
    # Email Logs
    def email_sent(self, to_email, subject, success=True):
        """Log email sending"""
        status = "SUCCESS" if success else "FAILED"
        log_msg = f"EMAIL {status} - To: {to_email} | Subject: {subject}"
        self.user_logger.info(log_msg)
        if not success:
            self.error_logger.error(log_msg)
    
    # Backup Logs
    def backup_created(self, backup_path, size_bytes):
        """Log backup creation"""
        size_mb = size_bytes / (1024 * 1024)
        log_msg = f"BACKUP CREATED - Path: {backup_path} | Size: {size_mb:.2f}MB"
        self.user_logger.info(log_msg)
    
    def backup_restored(self, backup_path):
        """Log backup restoration"""
        log_msg = f"BACKUP RESTORED - Path: {backup_path}"
        self.user_logger.warning(log_msg)
        self.security_logger.warning(log_msg)
    
    # Invoice Logs
    def invoice_created(self, invoice_number, customer_name, amount):
        """Log invoice creation"""
        log_msg = f"INVOICE CREATED - Number: {invoice_number} | Customer: {customer_name} | Amount: ₹{amount:.2f}"
        self.user_logger.info(log_msg)
    
    def invoice_paid(self, invoice_number, amount, payment_method):
        """Log invoice payment"""
        log_msg = f"INVOICE PAID - Number: {invoice_number} | Amount: ₹{amount:.2f} | Method: {payment_method}"
        self.user_logger.info(log_msg)
    
    # Report Generation Logs
    def report_generated(self, report_type, file_path):
        """Log report generation"""
        log_msg = f"REPORT GENERATED - Type: {report_type} | File: {file_path}"
        self.user_logger.info(log_msg)

# Global logger instance
logger = Logger()