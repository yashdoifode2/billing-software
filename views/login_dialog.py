from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService

class LoginDialog(QDialog):
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_service = AuthService()
        self.setup_ui()
        self.setWindowTitle("Login - Professional Invoice System")
        self.setModal(True)
        self.setFixedSize(450, 400)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Professional Invoice System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.username_input.returnPressed.connect(self.login)
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        layout.addWidget(self.login_btn)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Info label
        info_label = QLabel("Demo Credentials:\nUsername: admin\nPassword: Admin@123")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 20px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Please enter username and password")
            return
        
        user = self.auth_service.authenticate(username, password)
        if user:
            self.login_successful.emit(user)
            self.accept()
        else:
            self.status_label.setText("Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()