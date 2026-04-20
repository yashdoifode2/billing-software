from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QLabel, QFrame, QPushButton, 
                             QMessageBox, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QIcon
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

class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setFocusPolicy(Qt.NoFocus)
        
    def enterEvent(self, event):
        self.setStyleSheet(self.styleSheet() + """
            QPushButton {
                background-color: rgba(52, 73, 94, 0.8);
                padding-left: 20px;
            }
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("""
            QPushButton {
                background-color: rgba(52, 73, 94, 0.8);
                padding-left: 20px;
            }
        """, ""))
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.auth_service = AuthService()
        self.auth_service.current_user = user
        self.current_page = "dashboard"
        self.setup_window()
        self.setup_ui()
        self.apply_modern_style()
        
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle(f"InvoicePro Enterprise - {self.user['full_name']}")
        self.setGeometry(100, 100, 1400, 850)
        
        # Set window icon (you can add your own icon file)
        # self.setWindowIcon(QIcon("resources/icon.png"))
        
        # Enable modern window effects
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Set minimum window size
        self.setMinimumSize(1200, 700)
        
    def setup_ui(self):
        """Setup the main UI structure"""
        # Central widget with gradient background
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        
        # Main layout with spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        
        # Create content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        self.content_area.setStyleSheet("""
            QWidget#content_area {
                background-color: #f8f9fa;
            }
        """)
        
        # Create pages
        self.create_pages()
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)
        
        # Set default page
        self.switch_page('dashboard')
        
    def create_sidebar(self):
        """Create modern sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a252f, stop:1 #2c3e50);
                border-right: none;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Header section with logo
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.setStyleSheet("""
            QWidget#header_widget {
                background-color: rgba(0, 0, 0, 0.2);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 30, 20, 20)
        
        # Logo
        logo_label = QLabel("INVOICEPRO")
        logo_label.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Enterprise Edition")
        subtitle_label.setStyleSheet("""
            color: #bdc3c7;
            font-size: 11px;
            letter-spacing: 1px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(subtitle_label)
        sidebar_layout.addWidget(header_widget)
        
        # User profile section
        profile_widget = self.create_profile_widget()
        sidebar_layout.addWidget(profile_widget)
        
        # Navigation menu
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(5)
        
        # Navigation items with icons and descriptions
        nav_items = [
            ("📊", "Dashboard", "dashboard", "Overview & Statistics"),
            ("👥", "Customers", "customers", "Manage Client Base"),
            ("📦", "Products", "products", "Inventory Management"),
            ("📄", "Invoices", "invoices", "Billing & Payments"),
            ("💰", "Expenses", "expenses", "Track Spending"),
            ("📈", "Reports", "reports", "Analytics & Reports"),
            ("⚙️", "Settings", "settings", "System Configuration"),
        ]
        
        self.nav_buttons = {}
        for icon, text, page_name, tooltip in nav_items:
            btn = self.create_nav_button(icon, text, page_name, tooltip)
            nav_layout.addWidget(btn)
            self.nav_buttons[page_name] = btn
        
        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_widget)
        
        # Footer section with logout
        footer_widget = self.create_footer()
        sidebar_layout.addWidget(footer_widget)
        
        return sidebar
    
    def create_profile_widget(self):
        """Create modern user profile widget"""
        profile_widget = QFrame()
        profile_widget.setObjectName("profile_widget")
        profile_widget.setStyleSheet("""
            QFrame#profile_widget {
                background-color: rgba(0, 0, 0, 0.2);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(profile_widget)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(8)
        
        # Avatar circle (using text for now)
        avatar_label = QLabel(self.user['full_name'][0].upper())
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 35px;
                padding: 15px;
                min-width: 70px;
                min-height: 70px;
                max-width: 70px;
                max-height: 70px;
            }
        """)
        layout.addWidget(avatar_label, 0, Qt.AlignCenter)
        
        # User name
        name_label = QLabel(self.user['full_name'])
        name_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # User role with badge
        role_label = QLabel(self.user['role'].upper())
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 12px;
                max-width: 100px;
            }
        """)
        layout.addWidget(role_label, 0, Qt.AlignCenter)
        
        # Email
        if 'email' in self.user:
            email_label = QLabel(self.user['email'])
            email_label.setStyleSheet("color: #bdc3c7; font-size: 11px;")
            email_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(email_label)
        
        return profile_widget
    
    def create_nav_button(self, icon, text, page_name, tooltip):
        """Create modern navigation button"""
        btn = QPushButton(f"  {icon}  {text}")
        btn.setObjectName(f"nav_btn_{page_name}")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(50)
        btn.setFocusPolicy(Qt.NoFocus)
        
        # Set font
        font = QFont()
        font.setPointSize(10)
        btn.setFont(font)
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: rgba(52, 73, 94, 0.6);
                color: white;
                padding-left: 25px;
            }
            QPushButton[active="true"] {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        
        btn.clicked.connect(lambda checked, n=page_name: self.switch_page(n))
        return btn
    
    def create_footer(self):
        """Create footer widget with logout and info"""
        footer_widget = QWidget()
        footer_widget.setObjectName("footer_widget")
        footer_widget.setStyleSheet("""
            QWidget#footer_widget {
                background-color: rgba(0, 0, 0, 0.2);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(footer_widget)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Logout button
        logout_btn = QPushButton("🚪  Sign Out")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setMinimumHeight(45)
        logout_btn.setFocusPolicy(Qt.NoFocus)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        # Version info
        version_label = QLabel("Version 2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding-top: 10px;")
        layout.addWidget(version_label)
        
        return footer_widget
    
    def create_pages(self):
        """Create and initialize all page widgets"""
        self.pages = {}
        
        # Define page configurations
        page_configs = [
            ('dashboard', DashboardWidget, "Dashboard"),
            ('customers', CustomersWidget, "Customer Management"),
            ('products', ProductsWidget, "Product Management"),
            ('invoices', InvoicesWidget, "Invoice Management"),
            ('expenses', ExpensesWidget, "Expense Tracking"),
            ('reports', ReportsWidget, "Reports & Analytics"),
            ('settings', SettingsWidget, "System Settings"),
        ]
        
        for page_name, page_class, title in page_configs:
            try:
                print(f"Loading {title}...")
                page_widget = page_class(self.auth_service)
                page_widget.setObjectName(f"page_{page_name}")
                self.content_area.addWidget(page_widget)
                self.pages[page_name] = page_widget
            except Exception as e:
                print(f"Error loading {title}: {str(e)}")
                # Create error page
                error_widget = self.create_error_page(title, str(e))
                self.content_area.addWidget(error_widget)
                self.pages[page_name] = error_widget
    
    def create_error_page(self, page_name, error_message):
        """Create error page for failed widget loads"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        error_label = QLabel(f"⚠️ Error Loading {page_name}")
        error_label.setStyleSheet("font-size: 18px; color: #e74c3c;")
        error_label.setAlignment(Qt.AlignCenter)
        
        detail_label = QLabel(f"Details: {error_message}")
        detail_label.setStyleSheet("color: #7f8c8d;")
        detail_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(error_label)
        layout.addWidget(detail_label)
        layout.addStretch()
        
        return widget
    
    def switch_page(self, page_name):
        """Switch between pages with animation and visual feedback"""
        if page_name in self.pages:
            # Update active button styling
            for name, button in self.nav_buttons.items():
                if name == page_name:
                    button.setProperty("active", True)
                    button.setStyleSheet(button.styleSheet())
                else:
                    button.setProperty("active", False)
                    button.setStyleSheet(button.styleSheet())
            
            # Switch page
            self.content_area.setCurrentWidget(self.pages[page_name])
            self.current_page = page_name
            
            # Refresh page if it has refresh method
            if hasattr(self.pages[page_name], 'refresh'):
                try:
                    self.pages[page_name].refresh()
                except Exception as e:
                    print(f"Error refreshing {page_name}: {str(e)}")
            
            # Update window title
            page_titles = {
                'dashboard': 'Dashboard',
                'customers': 'Customer Management',
                'products': 'Product Management',
                'invoices': 'Invoice Management',
                'expenses': 'Expense Tracking',
                'reports': 'Reports & Analytics',
                'settings': 'System Settings'
            }
            title = page_titles.get(page_name, page_name.capitalize())
            self.setWindowTitle(f"InvoicePro Enterprise - {title} - {self.user['full_name']}")
    
    def apply_modern_style(self):
        """Apply modern global stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                font-size: 11px;
                padding: 5px;
                border-radius: 3px;
            }
        """)
    
    def logout(self):
        """Handle user logout with confirmation"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Logout")
        msg_box.setText("Are you sure you want to sign out?")
        msg_box.setInformativeText("You will need to login again to access the system.")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Yes, Sign Out")
        msg_box.button(QMessageBox.No).setText("Cancel")
        
        # Style the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QPushButton {
                min-width: 100px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton[text="Yes, Sign Out"] {
                background-color: #e74c3c;
                color: white;
            }
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            try:
                self.auth_service.logout()
                self.close()
                
                # Show login dialog
                from views.login_dialog import LoginDialog
                self.login_dialog = LoginDialog()
                self.login_dialog.login_successful.connect(self.restart_app)
                self.login_dialog.show()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to logout: {str(e)}")
    
    def restart_app(self, user):
        """Restart the application with new user"""
        try:
            self.close()
            new_window = MainWindow(user)
            new_window.show()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to restart application: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(self, 'Confirm Exit', 
                                    'Are you sure you want to exit the application?',
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Perform cleanup if needed
            try:
                # Save any unsaved data
                if hasattr(self.pages.get(self.current_page), 'save_state'):
                    self.pages[self.current_page].save_state()
            except Exception:
                pass
            event.accept()
        else:
            event.ignore()