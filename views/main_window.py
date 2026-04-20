from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QLabel, QFrame, QPushButton, 
                             QMessageBox)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views.dashboard import DashboardWidget
from views.customers import CustomersWidget
from views.products import ProductsWidget
from views.invoices import InvoicesWidget
from views.expenses import ExpensesWidget
from views.reports import ReportsWidget
from views.settings import SettingsWidget
from services.auth_service import AuthService

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.auth_service = AuthService()
        self.auth_service.current_user = user
        self.setWindowTitle(f"Professional Invoice System - {user['full_name']}")
        self.setGeometry(100, 100, 1300, 750)
        self.setup_ui()
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo/Title
        logo_label = QLabel("📊 Invoice Pro")
        logo_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            margin-bottom: 20px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        
        # User info
        user_frame = QFrame()
        user_frame.setObjectName("user_frame")
        user_frame.setStyleSheet("""
            QFrame#user_frame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
        """)
        user_layout = QVBoxLayout(user_frame)
        
        user_name = QLabel(f"👤 {self.user['full_name']}")
        user_name.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        user_role = QLabel(f"Role: {self.user['role'].upper()}")
        user_role.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        sidebar_layout.addWidget(user_frame)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("👥 Customers", "customers"),
            ("📦 Products", "products"),
            ("📄 Invoices", "invoices"),
            ("💰 Expenses", "expenses"),
            ("📈 Reports", "reports"),
            ("⚙️ Settings", "settings"),
        ]
        
        self.pages = {}
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        print("Creating pages...")
        self.pages['dashboard'] = DashboardWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['dashboard'])
        
        self.pages['customers'] = CustomersWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['customers'])
        
        self.pages['products'] = ProductsWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['products'])
        
        self.pages['invoices'] = InvoicesWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['invoices'])
        
        self.pages['expenses'] = ExpensesWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['expenses'])
        
        self.pages['reports'] = ReportsWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['reports'])
        
        self.pages['settings'] = SettingsWidget(self.auth_service)
        self.stacked_widget.addWidget(self.pages['settings'])
        
        # Add navigation buttons
        for text, name in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("nav_button")
            btn.setMinimumHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton#nav_button {
                    background-color: transparent;
                    color: white;
                    border: none;
                    text-align: left;
                    padding: 10px 15px;
                    font-size: 14px;
                    border-radius: 8px;
                }
                QPushButton#nav_button:hover {
                    background-color: #34495e;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setMinimumHeight(45)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton#logout_btn {
                background-color: #e74c3c;
                color: white;
                border: none;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                border-radius: 8px;
                margin-top: 20px;
            }
            QPushButton#logout_btn:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Set default page
        self.switch_page('dashboard')
    
    def switch_page(self, page_name):
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            if hasattr(self.pages[page_name], 'refresh'):
                self.pages[page_name].refresh()
    
    def logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.close()
            from views.login_dialog import LoginDialog
            self.login_dialog = LoginDialog()
            self.login_dialog.login_successful.connect(self.restart_app)
            self.login_dialog.show()
    
    def restart_app(self, user):
        self.close()
        new_window = MainWindow(user)
        new_window.show()