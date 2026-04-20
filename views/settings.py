from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox,
                             QTextEdit, QFileDialog, QMessageBox, QComboBox,
                             QCheckBox, QTabWidget, QSpinBox, QScrollArea,
                             QFrame, QGridLayout, QMainWindow, QSizePolicy,
                             QToolBar, QAction, QSplitter, QProgressBar,
                             QStatusBar, QApplication, QStyleFactory, QTabBar)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QColor
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from utils.backup_restore import BackupRestore


class SettingsWindow(QMainWindow):
    """Main window wrapper for settings with full window management"""
    
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("System Settings - Invoice Management System")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        # Set application style
        self.setStyle(QStyleFactory.create('Fusion'))
        
        # Setup UI
        self.setup_menu_bar()
        self.setup_status_bar()
        
        # Central widget
        central_widget = SettingsWidget(auth_service)
        self.setCentralWidget(central_widget)
        
        # Connect signals
        central_widget.settings_saved.connect(self.on_settings_saved)
    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #34495e;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #2c3e50;
            }
            QMenu {
                background-color: #34495e;
                color: white;
                border: 1px solid #2c3e50;
            }
            QMenu::item:selected {
                background-color: #2c3e50;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Settings", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.centralWidget().save_settings())
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut("Ctrl+M")
        minimize_action.triggered.connect(self.showMinimized)
        view_menu.addAction(minimize_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(lambda: self.centralWidget().backup_database())
        tools_menu.addAction(backup_action)
        
        restore_action = QAction("Restore Database", self)
        restore_action.triggered.connect(lambda: self.centralWidget().restore_database())
        tools_menu.addAction(restore_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        self.statusBar.showMessage("Ready", 3000)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.statusBar.showMessage("Exited full screen mode", 2000)
        else:
            self.showFullScreen()
            self.statusBar.showMessage("Entered full screen mode - Press F11 to exit", 2000)
    
    def on_settings_saved(self):
        self.statusBar.showMessage("Settings saved successfully!", 3000)
    
    def show_about(self):
        QMessageBox.about(self, "About Settings",
                         "<h3>Invoice Management System</h3>"
                         "<p>Version 2.0</p>"
                         "<p>Enhanced Settings Management Module</p>"
                         "<p>Features:</p>"
                         "<ul>"
                         "<li>Full window management (minimize/fullscreen)</li>"
                         "<li>Responsive scrollable layouts</li>"
                         "<li>Modern UI design</li>"
                         "<li>Real-time settings validation</li>"
                         "<li>Auto-save backup integration</li>"
                         "</ul>")


class SettingsWidget(QWidget):
    settings_saved = pyqtSignal()
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = SettingsController()
        self.backup_restore = BackupRestore()
        self.logo_data = None
        self.unsaved_changes = False
        self.setup_ui()
        self.load_settings()
        self.setup_auto_save_timer()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and window controls
        header = self.create_header()
        layout.addWidget(header)
        
        # Create main content area with tab widget
        self.tab_widget = ModernTabWidget()
        self.tab_widget.setStyleSheet(self.get_tab_style())
        
        # Create all tabs
        self.create_business_tab()
        self.create_bank_tab()
        self.create_tax_tab()
        self.create_invoice_tab()
        self.create_email_tab()
        self.create_backup_tab()
        
        layout.addWidget(self.tab_widget, stretch=1)
        
        # Bottom button bar with enhanced controls
        button_bar = self.create_button_bar()
        layout.addWidget(button_bar)
    
    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #34495e, stop:1 #2c3e50);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("⚙️ System Configuration")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Window control buttons
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """
        
        self.minimize_btn = QPushButton("━")
        self.minimize_btn.setFixedSize(35, 35)
        self.minimize_btn.setStyleSheet(btn_style)
        self.minimize_btn.clicked.connect(self.minimize_window)
        
        self.fullscreen_btn = QPushButton("□")
        self.fullscreen_btn.setFixedSize(35, 35)
        self.fullscreen_btn.setStyleSheet(btn_style)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.fullscreen_btn)
        
        return header
    
    def create_button_bar(self):
        button_bar = QFrame()
        button_bar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #dee2e6;
            }
        """)
        button_layout = QHBoxLayout(button_bar)
        
        # Save button with icon and progress indicator
        self.save_btn = QPushButton("💾 Save All Settings")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset to Saved")
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.reset_btn.clicked.connect(self.confirm_reset)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("● All settings saved")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 12px;
                padding: 5px 15px;
                background-color: #e8f5e9;
                border-radius: 15px;
            }
        """)
        button_layout.addWidget(self.status_indicator)
        
        return button_bar
    
    def create_business_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Enhanced scroll area
        scroll = ModernScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Logo Section
        logo_group = self.create_logo_section()
        scroll_layout.addWidget(logo_group)
        
        # Business Information
        business_group = self.create_business_info_section()
        scroll_layout.addWidget(business_group)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "🏢 Business Info")
    
    def create_logo_section(self):
        logo_group = QGroupBox("Company Branding")
        logo_group.setStyleSheet(self.get_groupbox_style())
        
        logo_layout = QVBoxLayout(logo_group)
        logo_layout.setSpacing(15)
        
        # Logo preview with improved design
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 15px;
            }
        """)
        preview_container.setFixedSize(220, 220)
        preview_layout = QVBoxLayout(preview_container)
        
        self.logo_preview = QLabel()
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setFixedSize(200, 200)
        self.logo_preview.setStyleSheet("""
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)
        self.logo_preview.setText("📷\n\nNo Logo\n\nUpload an image file")
        preview_layout.addWidget(self.logo_preview, alignment=Qt.AlignCenter)
        
        logo_layout.addWidget(preview_container, alignment=Qt.AlignCenter)
        
        # Button container
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        self.upload_logo_btn = QPushButton("📁 Upload Logo")
        self.upload_logo_btn.setMinimumHeight(40)
        self.upload_logo_btn.setMinimumWidth(130)
        self.upload_logo_btn.setStyleSheet(self.get_button_style("#3498db"))
        self.upload_logo_btn.clicked.connect(self.upload_logo)
        btn_layout.addWidget(self.upload_logo_btn)
        
        self.remove_logo_btn = QPushButton("🗑️ Remove")
        self.remove_logo_btn.setMinimumHeight(40)
        self.remove_logo_btn.setMinimumWidth(130)
        self.remove_logo_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        btn_layout.addWidget(self.remove_logo_btn)
        
        btn_layout.addStretch()
        logo_layout.addWidget(btn_container)
        
        # Info label
        info_label = QLabel("💡 Supported formats: PNG, JPG, JPEG, BMP (Max 2MB)")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(info_label)
        
        return logo_group
    
    def create_business_info_section(self):
        business_group = QGroupBox("Business Information")
        business_group.setStyleSheet(self.get_groupbox_style())
        
        # Use QGridLayout for better organization
        grid_layout = QGridLayout(business_group)
        grid_layout.setSpacing(15)
        grid_layout.setVerticalSpacing(20)
        
        # Create styled line edits
        self.business_name = self.create_styled_lineedit("Enter business name")
        self.business_address = self.create_styled_textedit("Enter business address")
        self.business_phone = self.create_styled_lineedit("Phone number")
        self.business_email = self.create_styled_lineedit("Email address")
        self.business_website = self.create_styled_lineedit("Website URL")
        self.business_gst = self.create_styled_lineedit("GST Number")
        self.business_pan = self.create_styled_lineedit("PAN Number")
        
        # Add to grid
        row = 0
        grid_layout.addWidget(QLabel("Business Name:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_name, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("Address:"), row, 0, Qt.AlignRight | Qt.AlignTop)
        grid_layout.addWidget(self.business_address, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("Phone:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_phone, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("Email:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_email, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("Website:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_website, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("GST Number:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_gst, row, 1)
        
        row += 1
        grid_layout.addWidget(QLabel("PAN Number:"), row, 0, Qt.AlignRight)
        grid_layout.addWidget(self.business_pan, row, 1)
        
        # Set column stretches
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 3)
        
        return business_group
    
    def create_bank_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = ModernScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        bank_group = QGroupBox("Bank Account Configuration")
        bank_group.setStyleSheet(self.get_groupbox_style())
        
        form_layout = QFormLayout(bank_group)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.bank_name = self.create_styled_lineedit("Bank name")
        self.bank_account_name = self.create_styled_lineedit("Account holder name")
        self.bank_account_number = self.create_styled_lineedit("Account number")
        self.bank_ifsc = self.create_styled_lineedit("IFSC code")
        self.bank_branch = self.create_styled_lineedit("Branch name")
        self.bank_upi_id = self.create_styled_lineedit("UPI ID (e.g., business@bank)")
        
        form_layout.addRow("Bank Name:", self.bank_name)
        form_layout.addRow("Account Holder:", self.bank_account_name)
        form_layout.addRow("Account Number:", self.bank_account_number)
        form_layout.addRow("IFSC Code:", self.bank_ifsc)
        form_layout.addRow("Branch:", self.bank_branch)
        form_layout.addRow("UPI ID:", self.bank_upi_id)
        
        scroll_layout.addWidget(bank_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "🏦 Bank Details")
    
    def create_tax_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        tax_group = QGroupBox("Tax Configuration")
        tax_group.setStyleSheet(self.get_groupbox_style())
        
        form_layout = QFormLayout(tax_group)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.default_cgst = self.create_styled_lineedit("9")
        self.default_sgst = self.create_styled_lineedit("9")
        self.default_igst = self.create_styled_lineedit("18")
        
        # Add validation for numeric input
        for field in [self.default_cgst, self.default_sgst, self.default_igst]:
            field.textChanged.connect(self.validate_tax_rates)
        
        form_layout.addRow("CGST Rate (%):", self.default_cgst)
        form_layout.addRow("SGST Rate (%):", self.default_sgst)
        form_layout.addRow("IGST Rate (%):", self.default_igst)
        
        # Info panel
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border-radius: 8px;
                padding: 10px;
                margin-top: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_label = QLabel("ℹ️ Information")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_label2 = QLabel("These rates will be applied as defaults when creating new products. You can modify them per transaction.")
        info_label2.setWordWrap(True)
        info_label2.setStyleSheet("color: #2c3e50; font-size: 11px;")
        info_layout.addWidget(info_label)
        info_layout.addWidget(info_label2)
        
        layout.addWidget(tax_group)
        layout.addWidget(info_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💰 Tax Settings")
    
    def create_invoice_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = ModernScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Invoice Settings
        invoice_group = QGroupBox("Invoice Preferences")
        invoice_group.setStyleSheet(self.get_groupbox_style())
        
        form_layout = QFormLayout(invoice_group)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.currency_symbol = self.create_styled_lineedit("₹")
        self.currency_symbol.setMaximumWidth(100)
        self.invoice_prefix = self.create_styled_lineedit("INV")
        self.invoice_terms = self.create_styled_textedit("Enter terms and conditions for invoices...")
        self.invoice_terms.setMaximumHeight(120)
        
        form_layout.addRow("Currency Symbol:", self.currency_symbol)
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        form_layout.addRow("Terms & Conditions:", self.invoice_terms)
        
        scroll_layout.addWidget(invoice_group)
        
        # UI Settings
        ui_group = QGroupBox("Appearance")
        ui_group.setStyleSheet(self.get_groupbox_style())
        
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(20)
        ui_layout.setLabelAlignment(Qt.AlignRight)
        
        self.ui_theme = QComboBox()
        self.ui_theme.addItems(["Light", "Dark"])
        self.ui_theme.setMinimumHeight(35)
        self.ui_theme.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        
        ui_layout.addRow("Theme:", self.ui_theme)
        
        scroll_layout.addWidget(ui_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "📄 Invoice Settings")
    
    def create_email_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = ModernScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # SMTP Configuration
        smtp_group = QGroupBox("SMTP Configuration")
        smtp_group.setStyleSheet(self.get_groupbox_style())
        
        form_layout = QFormLayout(smtp_group)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.smtp_host = self.create_styled_lineedit("smtp.gmail.com")
        self.smtp_port = self.create_styled_lineedit("587")
        self.smtp_user = self.create_styled_lineedit("your-email@gmail.com")
        self.smtp_password = self.create_styled_lineedit("Your email password or app password")
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_from_email = self.create_styled_lineedit("sender@example.com")
        self.smtp_use_tls = QCheckBox("Enable TLS/SSL Encryption")
        self.smtp_use_tls.setChecked(True)
        self.smtp_use_tls.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        form_layout.addRow("SMTP Host:", self.smtp_host)
        form_layout.addRow("SMTP Port:", self.smtp_port)
        form_layout.addRow("Username:", self.smtp_user)
        form_layout.addRow("Password:", self.smtp_password)
        form_layout.addRow("From Email:", self.smtp_from_email)
        form_layout.addRow("", self.smtp_use_tls)
        
        scroll_layout.addWidget(smtp_group)
        
        # Test Email Section
        test_group = QGroupBox("Test Configuration")
        test_group.setStyleSheet(self.get_groupbox_style())
        
        test_layout = QVBoxLayout(test_group)
        
        test_input_layout = QHBoxLayout()
        self.test_email = self.create_styled_lineedit("Enter email address to send test")
        test_input_layout.addWidget(self.test_email)
        
        self.test_btn = QPushButton("📧 Send Test Email")
        self.test_btn.setMinimumHeight(40)
        self.test_btn.setStyleSheet(self.get_button_style("#3498db"))
        self.test_btn.clicked.connect(self.send_test_email)
        test_input_layout.addWidget(self.test_btn)
        
        test_layout.addLayout(test_input_layout)
        
        scroll_layout.addWidget(test_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "📧 Email Settings")
    
    def create_backup_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = ModernScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Auto Backup Settings
        auto_group = QGroupBox("Automatic Backup")
        auto_group.setStyleSheet(self.get_groupbox_style())
        
        auto_layout = QVBoxLayout(auto_group)
        
        self.auto_backup = QCheckBox("Enable automatic backup")
        self.auto_backup.setStyleSheet("font-weight: bold; font-size: 12px;")
        auto_layout.addWidget(self.auto_backup)
        
        backup_path_layout = QHBoxLayout()
        self.backup_path = self.create_styled_lineedit("Select backup directory")
        backup_path_layout.addWidget(self.backup_path)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setMinimumHeight(35)
        browse_btn.setMinimumWidth(100)
        browse_btn.setStyleSheet(self.get_button_style("#95a5a6"))
        browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(browse_btn)
        
        auto_layout.addLayout(backup_path_layout)
        
        scroll_layout.addWidget(auto_group)
        
        # Manual Operations
        manual_group = QGroupBox("Manual Operations")
        manual_group.setStyleSheet(self.get_groupbox_style())
        
        manual_layout = QVBoxLayout(manual_group)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        backup_now_btn = QPushButton("💾 Create Backup")
        backup_now_btn.setMinimumHeight(50)
        backup_now_btn.setStyleSheet(self.get_button_style("#27ae60"))
        backup_now_btn.clicked.connect(self.backup_database)
        button_layout.addWidget(backup_now_btn)
        
        restore_btn = QPushButton("🔄 Restore from Backup")
        restore_btn.setMinimumHeight(50)
        restore_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        restore_btn.clicked.connect(self.restore_database)
        button_layout.addWidget(restore_btn)
        
        manual_layout.addLayout(button_layout)
        
        # Info text
        info_label = QLabel("⚠️ Note: Restoring a backup will overwrite all current data. Please ensure you have a current backup before restoring.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #e74c3c; font-size: 11px; padding: 10px; background-color: #fdeaea; border-radius: 5px;")
        manual_layout.addWidget(info_label)
        
        scroll_layout.addWidget(manual_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "💾 Backup & Restore")
    
    # Helper methods for consistent styling
    def get_groupbox_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """
    
    def get_tab_style(self):
        return """
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e9ecef;
            }
        """
    
    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def create_styled_lineedit(self, placeholder=""):
        lineedit = QLineEdit()
        lineedit.setPlaceholderText(placeholder)
        lineedit.setMinimumHeight(40)
        lineedit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #95a5a6;
            }
        """)
        lineedit.textChanged.connect(self.mark_unsaved)
        return lineedit
    
    def create_styled_textedit(self, placeholder=""):
        textedit = QTextEdit()
        textedit.setPlaceholderText(placeholder)
        textedit.setMinimumHeight(80)
        textedit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        textedit.textChanged.connect(self.mark_unsaved)
        return textedit
    
    def mark_unsaved(self):
        if not self.unsaved_changes:
            self.unsaved_changes = True
            self.status_indicator.setText("⚠️ Unsaved changes")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    color: #f39c12;
                    font-size: 12px;
                    padding: 5px 15px;
                    background-color: #fff3e0;
                    border-radius: 15px;
                }
            """)
    
    def validate_tax_rates(self):
        """Validate tax rate inputs"""
        sender = self.sender()
        if sender:
            try:
                value = float(sender.text()) if sender.text() else 0
                if value < 0 or value > 100:
                    sender.setStyleSheet("border: 2px solid #e74c3c; border-radius: 6px;")
                else:
                    sender.setStyleSheet("")
            except ValueError:
                if sender.text():
                    sender.setStyleSheet("border: 2px solid #e74c3c; border-radius: 6px;")
                else:
                    sender.setStyleSheet("")
    
    def setup_auto_save_timer(self):
        """Auto-save timer for unsaved changes"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(300000)  # 5 minutes
    
    def auto_save(self):
        """Auto-save if there are unsaved changes"""
        if self.unsaved_changes:
            self.save_settings()
            self.status_indicator.setText("💾 Auto-saved")
            QTimer.singleShot(3000, lambda: self.status_indicator.setText("● All settings saved"))
    
    def minimize_window(self):
        """Minimize the main window"""
        main_window = self.window()
        if main_window:
            main_window.showMinimized()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        main_window = self.window()
        if main_window:
            if main_window.isFullScreen():
                main_window.showNormal()
                self.fullscreen_btn.setText("□")
            else:
                main_window.showFullScreen()
                self.fullscreen_btn.setText("❐")
    
    def confirm_reset(self):
        """Confirm before resetting"""
        reply = QMessageBox.question(self, "Confirm Reset", 
                                    "Are you sure you want to reset to saved settings?\nAny unsaved changes will be lost.",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.load_settings()
            self.unsaved_changes = False
            self.status_indicator.setText("● All settings saved")
    
    def browse_backup_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            self.backup_path.setText(directory)
            self.mark_unsaved()
    
    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Logo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024:
                QMessageBox.warning(self, "File Too Large", "Logo file size should be less than 2MB!")
                return
            
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            
            with open(file_path, 'rb') as f:
                self.logo_data = base64.b64encode(f.read()).decode('utf-8')
            
            QMessageBox.information(self, "Success", "Logo loaded successfully! Click 'Save All Settings' to save.")
            self.mark_unsaved()
    
    def remove_logo(self):
        reply = QMessageBox.question(self, "Remove Logo", 
                                    "Are you sure you want to remove the logo?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logo_data = None
            self.logo_preview.setText("📷\n\nNo Logo\n\nUpload an image file")
            self.logo_preview.setPixmap(QPixmap())
            QMessageBox.information(self, "Success", "Logo removed! Click 'Save All Settings' to save.")
            self.mark_unsaved()
    
    def send_test_email(self):
        email = self.test_email.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Please enter a test email address!")
            return
        
        from services.email_service import EmailService
        email_service = EmailService()
        
        subject = "Test Email from Invoice Management System"
        body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h2>Test Email</h2>
            </div>
            <div style="padding: 20px;">
                <p>Dear User,</p>
                <p>This is a test email from your <b>Invoice Management System</b>.</p>
                <p>If you received this email, your SMTP settings are configured correctly!</p>
                <br>
                <p>Best regards,<br>Invoice System</p>
            </div>
        </body>
        </html>
        """
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Sending...")
        
        success, message = email_service.send_email(email, subject, body)
        
        self.test_btn.setEnabled(True)
        self.test_btn.setText("📧 Send Test Email")
        
        if success:
            QMessageBox.information(self, "Success", f"Test email sent successfully to {email}!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to send email: {message}")
    
    def load_settings(self):
        settings = self.controller.get_settings()
        
        # Business Info
        self.business_name.setText(settings.get('business_name', ''))
        self.business_address.setText(settings.get('business_address', ''))
        self.business_phone.setText(settings.get('business_phone', ''))
        self.business_email.setText(settings.get('business_email', ''))
        self.business_website.setText(settings.get('business_website', ''))
        self.business_gst.setText(settings.get('business_gst', ''))
        self.business_pan.setText(settings.get('business_pan', ''))
        
        # Bank Details
        self.bank_name.setText(settings.get('bank_name', ''))
        self.bank_account_name.setText(settings.get('bank_account_name', ''))
        self.bank_account_number.setText(settings.get('bank_account_number', ''))
        self.bank_ifsc.setText(settings.get('bank_ifsc', ''))
        self.bank_branch.setText(settings.get('bank_branch', ''))
        self.bank_upi_id.setText(settings.get('bank_upi_id', ''))
        
        # Tax Settings
        self.default_cgst.setText(settings.get('default_cgst', '9'))
        self.default_sgst.setText(settings.get('default_sgst', '9'))
        self.default_igst.setText(settings.get('default_igst', '18'))
        
        # Invoice Settings
        self.currency_symbol.setText(settings.get('currency_symbol', '₹'))
        self.invoice_prefix.setText(settings.get('invoice_prefix', 'INV'))
        self.invoice_terms.setText(settings.get('invoice_terms', ''))
        
        # UI Settings
        theme_index = self.ui_theme.findText(settings.get('ui_theme', 'Light').capitalize())
        if theme_index >= 0:
            self.ui_theme.setCurrentIndex(theme_index)
        
        # Email Settings
        self.smtp_host.setText(settings.get('smtp_host', 'smtp.gmail.com'))
        self.smtp_port.setText(settings.get('smtp_port', '587'))
        self.smtp_user.setText(settings.get('smtp_user', ''))
        self.smtp_password.setText(settings.get('smtp_password', ''))
        self.smtp_from_email.setText(settings.get('smtp_from_email', ''))
        self.smtp_use_tls.setChecked(settings.get('smtp_use_tls', '1') == '1')
        
        # Backup Settings
        self.auto_backup.setChecked(settings.get('backup_enabled', '0') == '1')
        self.backup_path.setText(settings.get('backup_path', ''))
        
        # Logo
        logo_data = settings.get('company_logo', '')
        if logo_data:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(logo_data))
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                self.logo_data = logo_data
            except:
                self.logo_preview.setText("📷\n\nNo Logo\n\nUpload an image file")
                self.logo_data = None
        else:
            self.logo_preview.setText("📷\n\nNo Logo\n\nUpload an image file")
            self.logo_data = None
        
        self.unsaved_changes = False
    
    def save_settings(self):
        try:
            # Business Info
            self.controller.update_setting('business_name', self.business_name.text())
            self.controller.update_setting('business_address', self.business_address.toPlainText())
            self.controller.update_setting('business_phone', self.business_phone.text())
            self.controller.update_setting('business_email', self.business_email.text())
            self.controller.update_setting('business_website', self.business_website.text())
            self.controller.update_setting('business_gst', self.business_gst.text())
            self.controller.update_setting('business_pan', self.business_pan.text())
            
            # Bank Details
            self.controller.update_setting('bank_name', self.bank_name.text())
            self.controller.update_setting('bank_account_name', self.bank_account_name.text())
            self.controller.update_setting('bank_account_number', self.bank_account_number.text())
            self.controller.update_setting('bank_ifsc', self.bank_ifsc.text())
            self.controller.update_setting('bank_branch', self.bank_branch.text())
            self.controller.update_setting('bank_upi_id', self.bank_upi_id.text())
            
            # Tax Settings
            self.controller.update_setting('default_cgst', self.default_cgst.text())
            self.controller.update_setting('default_sgst', self.default_sgst.text())
            self.controller.update_setting('default_igst', self.default_igst.text())
            
            # Invoice Settings
            self.controller.update_setting('currency_symbol', self.currency_symbol.text())
            self.controller.update_setting('invoice_prefix', self.invoice_prefix.text())
            self.controller.update_setting('invoice_terms', self.invoice_terms.toPlainText())
            
            # UI Settings
            self.controller.update_setting('ui_theme', self.ui_theme.currentText().lower())
            
            # Email Settings
            self.controller.update_setting('smtp_host', self.smtp_host.text())
            self.controller.update_setting('smtp_port', self.smtp_port.text())
            self.controller.update_setting('smtp_user', self.smtp_user.text())
            self.controller.update_setting('smtp_password', self.smtp_password.text())
            self.controller.update_setting('smtp_from_email', self.smtp_from_email.text())
            self.controller.update_setting('smtp_use_tls', '1' if self.smtp_use_tls.isChecked() else '0')
            
            # Backup Settings
            self.controller.update_setting('backup_enabled', '1' if self.auto_backup.isChecked() else '0')
            self.controller.update_setting('backup_path', self.backup_path.text())
            
            # Logo
            if self.logo_data:
                self.controller.update_setting('company_logo', self.logo_data)
            else:
                self.controller.update_setting('company_logo', '')
            
            QMessageBox.information(self, "Success", "All settings saved successfully!")
            self.settings_saved.emit()
            self.unsaved_changes = False
            self.status_indicator.setText("● All settings saved")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 12px;
                    padding: 5px 15px;
                    background-color: #e8f5e9;
                    border-radius: 15px;
                }
            """)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def backup_database(self):
        backup_path = self.backup_path.text() if self.backup_path.text() else None
        if backup_path:
            import datetime
            file_path = os.path.join(backup_path, f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Backup Files (*.db)")
        
        if file_path:
            if self.backup_restore.backup(file_path):
                QMessageBox.information(self, "Success", f"Database backed up successfully!\nLocation: {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to backup database!")
    
    def restore_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database Files (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Confirm Restore", 
                                        "Restoring will overwrite current data. Continue?\nThe application will close after restore.",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.backup_restore.restore(file_path):
                    QMessageBox.information(self, "Success", "Database restored successfully! Please restart the application.")
                    import sys
                    sys.exit(0)
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database!")
    
    def refresh(self):
        self.load_settings()


class ModernTabWidget(QTabWidget):
    """Enhanced tab widget with improved styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)


class ModernScrollArea(QScrollArea):
    """Enhanced scroll area with smooth scrolling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)


# Usage example
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Mock auth service for testing
    class MockAuthService:
        pass
    
    auth_service = MockAuthService()
    
    # Use the enhanced SettingsWindow
    window = SettingsWindow(auth_service)
    window.show()
    
    sys.exit(app.exec_())