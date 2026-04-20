from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox,
                             QTextEdit, QFileDialog, QMessageBox, QComboBox,
                             QCheckBox, QTabWidget, QSpinBox, QScrollArea,
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from utils.backup_restore import BackupRestore

class SettingsWidget(QWidget):
    settings_saved = pyqtSignal()
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = SettingsController()
        self.backup_restore = BackupRestore()
        self.logo_data = None
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("System Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
                color: white;
            }
        """)
        
        # Create all tabs
        self.create_business_tab()
        self.create_bank_tab()
        self.create_tax_tab()
        self.create_invoice_tab()
        self.create_email_tab()
        self.create_backup_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Bottom button bar
        button_bar = QFrame()
        button_bar.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_bar)
        
        # Save button
        self.save_btn = QPushButton("💾 Save All Settings")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset to Saved")
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.reset_btn.clicked.connect(self.load_settings)
        button_layout.addWidget(self.reset_btn)
        
        layout.addWidget(button_bar)
    
    def create_business_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Scroll area for business tab
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Logo Section
        logo_group = QGroupBox("Company Logo")
        logo_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        logo_layout = QVBoxLayout(logo_group)
        
        # Logo preview frame
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        preview_frame.setFixedSize(200, 200)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.logo_preview = QLabel()
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setFixedSize(180, 180)
        self.logo_preview.setStyleSheet("border: none;")
        self.logo_preview.setText("No Logo\n\nClick 'Upload Logo' to add")
        preview_layout.addWidget(self.logo_preview, alignment=Qt.AlignCenter)
        
        logo_layout.addWidget(preview_frame, alignment=Qt.AlignCenter)
        
        # Logo buttons
        logo_btn_layout = QHBoxLayout()
        logo_btn_layout.addStretch()
        
        self.upload_logo_btn = QPushButton("📁 Upload Logo")
        self.upload_logo_btn.setMinimumHeight(35)
        self.upload_logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.upload_logo_btn.clicked.connect(self.upload_logo)
        logo_btn_layout.addWidget(self.upload_logo_btn)
        
        self.remove_logo_btn = QPushButton("🗑️ Remove Logo")
        self.remove_logo_btn.setMinimumHeight(35)
        self.remove_logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        logo_btn_layout.addWidget(self.remove_logo_btn)
        
        logo_btn_layout.addStretch()
        logo_layout.addLayout(logo_btn_layout)
        
        scroll_layout.addWidget(logo_group)
        
        # Business Information
        business_group = QGroupBox("Business Information")
        business_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(business_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.business_name = QLineEdit()
        self.business_name.setPlaceholderText("Enter business name")
        self.business_name.setMinimumHeight(35)
        
        self.business_address = QTextEdit()
        self.business_address.setMaximumHeight(80)
        self.business_address.setPlaceholderText("Enter business address")
        
        self.business_phone = QLineEdit()
        self.business_phone.setPlaceholderText("Phone number")
        self.business_phone.setMinimumHeight(35)
        
        self.business_email = QLineEdit()
        self.business_email.setPlaceholderText("Email address")
        self.business_email.setMinimumHeight(35)
        
        self.business_website = QLineEdit()
        self.business_website.setPlaceholderText("Website URL")
        self.business_website.setMinimumHeight(35)
        
        self.business_gst = QLineEdit()
        self.business_gst.setPlaceholderText("GST Number")
        self.business_gst.setMinimumHeight(35)
        
        self.business_pan = QLineEdit()
        self.business_pan.setPlaceholderText("PAN Number")
        self.business_pan.setMinimumHeight(35)
        
        form_layout.addRow("Business Name:", self.business_name)
        form_layout.addRow("Address:", self.business_address)
        form_layout.addRow("Phone:", self.business_phone)
        form_layout.addRow("Email:", self.business_email)
        form_layout.addRow("Website:", self.business_website)
        form_layout.addRow("GST Number:", self.business_gst)
        form_layout.addRow("PAN Number:", self.business_pan)
        
        scroll_layout.addWidget(business_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "🏢 Business Info")
    
    def create_bank_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        bank_group = QGroupBox("Bank Account Details")
        bank_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(bank_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.bank_name = QLineEdit()
        self.bank_name.setPlaceholderText("Bank name")
        self.bank_name.setMinimumHeight(35)
        
        self.bank_account_name = QLineEdit()
        self.bank_account_name.setPlaceholderText("Account holder name")
        self.bank_account_name.setMinimumHeight(35)
        
        self.bank_account_number = QLineEdit()
        self.bank_account_number.setPlaceholderText("Account number")
        self.bank_account_number.setMinimumHeight(35)
        
        self.bank_ifsc = QLineEdit()
        self.bank_ifsc.setPlaceholderText("IFSC code")
        self.bank_ifsc.setMinimumHeight(35)
        
        self.bank_branch = QLineEdit()
        self.bank_branch.setPlaceholderText("Branch name")
        self.bank_branch.setMinimumHeight(35)
        
        self.bank_upi_id = QLineEdit()
        self.bank_upi_id.setPlaceholderText("UPI ID (e.g., business@bank)")
        self.bank_upi_id.setMinimumHeight(35)
        
        form_layout.addRow("Bank Name:", self.bank_name)
        form_layout.addRow("Account Holder Name:", self.bank_account_name)
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
        
        tax_group = QGroupBox("Default Tax Rates")
        tax_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(tax_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.default_cgst = QLineEdit()
        self.default_cgst.setPlaceholderText("9")
        self.default_cgst.setMinimumHeight(35)
        
        self.default_sgst = QLineEdit()
        self.default_sgst.setPlaceholderText("9")
        self.default_sgst.setMinimumHeight(35)
        
        self.default_igst = QLineEdit()
        self.default_igst.setPlaceholderText("18")
        self.default_igst.setMinimumHeight(35)
        
        form_layout.addRow("Default CGST Rate (%):", self.default_cgst)
        form_layout.addRow("Default SGST Rate (%):", self.default_sgst)
        form_layout.addRow("Default IGST Rate (%):", self.default_igst)
        
        # Info label
        info_label = QLabel("Note: These rates will be applied as defaults when adding new products")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 10px;")
        
        layout.addWidget(tax_group)
        layout.addWidget(info_label)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💰 Tax Settings")
    
    def create_invoice_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        invoice_group = QGroupBox("Invoice Settings")
        invoice_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(invoice_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.currency_symbol = QLineEdit()
        self.currency_symbol.setPlaceholderText("₹")
        self.currency_symbol.setMaximumWidth(100)
        self.currency_symbol.setMinimumHeight(35)
        
        self.invoice_prefix = QLineEdit()
        self.invoice_prefix.setPlaceholderText("INV")
        self.invoice_prefix.setMinimumHeight(35)
        
        self.invoice_terms = QTextEdit()
        self.invoice_terms.setMaximumHeight(100)
        self.invoice_terms.setPlaceholderText("Enter terms and conditions for invoices...")
        
        form_layout.addRow("Currency Symbol:", self.currency_symbol)
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        form_layout.addRow("Terms & Conditions:", self.invoice_terms)
        
        scroll_layout.addWidget(invoice_group)
        
        # UI Settings
        ui_group = QGroupBox("User Interface")
        ui_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        ui_layout = QFormLayout(ui_group)
        ui_layout.setSpacing(15)
        ui_layout.setLabelAlignment(Qt.AlignRight)
        
        self.ui_theme = QComboBox()
        self.ui_theme.addItems(["light", "dark"])
        self.ui_theme.setMinimumHeight(35)
        
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
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        smtp_group = QGroupBox("SMTP Configuration")
        smtp_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(smtp_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.smtp_host = QLineEdit()
        self.smtp_host.setPlaceholderText("smtp.gmail.com")
        self.smtp_host.setMinimumHeight(35)
        
        self.smtp_port = QLineEdit()
        self.smtp_port.setPlaceholderText("587")
        self.smtp_port.setMinimumHeight(35)
        
        self.smtp_user = QLineEdit()
        self.smtp_user.setPlaceholderText("your-email@gmail.com")
        self.smtp_user.setMinimumHeight(35)
        
        self.smtp_password = QLineEdit()
        self.smtp_password.setPlaceholderText("Your email password or app password")
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setMinimumHeight(35)
        
        self.smtp_from_email = QLineEdit()
        self.smtp_from_email.setPlaceholderText("sender@example.com")
        self.smtp_from_email.setMinimumHeight(35)
        
        self.smtp_use_tls = QCheckBox("Use TLS/SSL")
        self.smtp_use_tls.setChecked(True)
        
        form_layout.addRow("SMTP Host:", self.smtp_host)
        form_layout.addRow("SMTP Port:", self.smtp_port)
        form_layout.addRow("Username:", self.smtp_user)
        form_layout.addRow("Password:", self.smtp_password)
        form_layout.addRow("From Email:", self.smtp_from_email)
        form_layout.addRow("", self.smtp_use_tls)
        
        scroll_layout.addWidget(smtp_group)
        
        # Test Email Section
        test_group = QGroupBox("Test Email Configuration")
        test_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        test_layout = QHBoxLayout(test_group)
        
        self.test_email = QLineEdit()
        self.test_email.setPlaceholderText("Enter email address to send test")
        self.test_email.setMinimumHeight(35)
        test_layout.addWidget(self.test_email)
        
        self.test_btn = QPushButton("Send Test Email")
        self.test_btn.setMinimumHeight(35)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.test_btn.clicked.connect(self.send_test_email)
        test_layout.addWidget(self.test_btn)
        
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
        
        backup_group = QGroupBox("Backup Settings")
        backup_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        form_layout = QFormLayout(backup_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.auto_backup = QCheckBox("Enable Auto Backup")
        
        self.backup_path = QLineEdit()
        self.backup_path.setPlaceholderText("Select backup directory")
        self.backup_path.setMinimumHeight(35)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setMinimumHeight(35)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        browse_btn.clicked.connect(self.browse_backup_path)
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path)
        backup_path_layout.addWidget(browse_btn)
        
        form_layout.addRow("", self.auto_backup)
        form_layout.addRow("Backup Path:", backup_path_layout)
        
        layout.addWidget(backup_group)
        
        # Manual backup buttons
        manual_group = QGroupBox("Manual Backup & Restore")
        manual_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        button_layout = QHBoxLayout(manual_group)
        
        backup_now_btn = QPushButton("💿 Backup Now")
        backup_now_btn.setMinimumHeight(40)
        backup_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        backup_now_btn.clicked.connect(self.backup_database)
        button_layout.addWidget(backup_now_btn)
        
        restore_btn = QPushButton("🔄 Restore Database")
        restore_btn.setMinimumHeight(40)
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        restore_btn.clicked.connect(self.restore_database)
        button_layout.addWidget(restore_btn)
        
        button_layout.addStretch()
        
        layout.addWidget(manual_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💾 Backup & Restore")
    
    def browse_backup_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            self.backup_path.setText(directory)
    
    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Logo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Check file size (max 2MB)
            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024:
                QMessageBox.warning(self, "File Too Large", "Logo file size should be less than 2MB!")
                return
            
            # Load and display image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            
            # Convert to base64
            with open(file_path, 'rb') as f:
                self.logo_data = base64.b64encode(f.read()).decode('utf-8')
            
            QMessageBox.information(self, "Success", "Logo loaded successfully! Click 'Save All Settings' to save.")
    
    def remove_logo(self):
        reply = QMessageBox.question(self, "Remove Logo", 
                                    "Are you sure you want to remove the logo?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logo_data = None
            self.logo_preview.setText("No Logo\n\nClick 'Upload Logo' to add")
            self.logo_preview.setPixmap(QPixmap())
            QMessageBox.information(self, "Success", "Logo removed! Click 'Save All Settings' to save.")
    
    def send_test_email(self):
        email = self.test_email.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Please enter a test email address!")
            return
        
        from services.email_service import EmailService
        email_service = EmailService()
        
        # Create a simple test email
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
        self.test_btn.setText("Send Test Email")
        
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
        theme_index = self.ui_theme.findText(settings.get('ui_theme', 'light'))
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
                scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                self.logo_data = logo_data
            except:
                self.logo_preview.setText("No Logo\n\nClick 'Upload Logo' to add")
                self.logo_data = None
        else:
            self.logo_preview.setText("No Logo\n\nClick 'Upload Logo' to add")
            self.logo_data = None
    
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
            self.controller.update_setting('ui_theme', self.ui_theme.currentText())
            
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