from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox,
                             QTextEdit, QFileDialog, QMessageBox, QComboBox,
                             QCheckBox, QTabWidget, QSpinBox, QScrollArea)
from PyQt5.QtCore import Qt
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from utils.backup_restore import BackupRestore
from views.logo_upload_dialog import LogoUploadDialog

class SettingsWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = SettingsController()
        self.backup_restore = BackupRestore()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Tab widget for settings
        self.tab_widget = QTabWidget()
        
        # Business tab
        self.business_tab = self.create_business_tab()
        self.tab_widget.addTab(self.business_tab, "🏢 Business Info")
        
        # Bank Details tab
        self.bank_tab = self.create_bank_tab()
        self.tab_widget.addTab(self.bank_tab, "🏦 Bank Details")
        
        # Tax tab
        self.tax_tab = self.create_tax_tab()
        self.tab_widget.addTab(self.tax_tab, "💰 Tax Settings")
        
        # Invoice tab
        self.invoice_tab = self.create_invoice_tab()
        self.tab_widget.addTab(self.invoice_tab, "📄 Invoice Settings")
        
        # Email tab
        self.email_tab = self.create_email_tab()
        self.tab_widget.addTab(self.email_tab, "📧 Email (SMTP)")
        
        # Backup tab
        self.backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(self.backup_tab, "💾 Backup & Restore")
        
        scroll_layout.addWidget(self.tab_widget)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
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
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
    
    def create_business_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logo Section
        logo_group = QGroupBox("Company Logo")
        logo_layout = QVBoxLayout(logo_group)
        
        self.logo_preview = QLabel()
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setStyleSheet("""
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            background-color: #f8f9fa;
        """)
        self.logo_preview.setScaledContents(True)
        logo_layout.addWidget(self.logo_preview, alignment=Qt.AlignCenter)
        
        logo_btn_layout = QHBoxLayout()
        self.upload_logo_btn = QPushButton("📁 Upload Logo")
        self.upload_logo_btn.clicked.connect(self.upload_logo)
        logo_btn_layout.addWidget(self.upload_logo_btn)
        
        self.remove_logo_btn = QPushButton("🗑️ Remove Logo")
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        logo_btn_layout.addWidget(self.remove_logo_btn)
        logo_layout.addLayout(logo_btn_layout)
        
        layout.addWidget(logo_group)
        
        # Business Information
        business_group = QGroupBox("Business Information")
        form_layout = QFormLayout(business_group)
        
        self.business_name = QLineEdit()
        self.business_address = QTextEdit()
        self.business_address.setMaximumHeight(80)
        self.business_phone = QLineEdit()
        self.business_email = QLineEdit()
        self.business_gst = QLineEdit()
        self.business_pan = QLineEdit()
        self.business_website = QLineEdit()
        
        form_layout.addRow("Business Name:", self.business_name)
        form_layout.addRow("Address:", self.business_address)
        form_layout.addRow("Phone:", self.business_phone)
        form_layout.addRow("Email:", self.business_email)
        form_layout.addRow("Website:", self.business_website)
        form_layout.addRow("GST Number:", self.business_gst)
        form_layout.addRow("PAN Number:", self.business_pan)
        
        layout.addWidget(business_group)
        layout.addStretch()
        
        return widget
    
    def create_bank_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        bank_group = QGroupBox("Bank Account Details")
        form_layout = QFormLayout(bank_group)
        
        self.bank_name = QLineEdit()
        self.bank_account_name = QLineEdit()
        self.bank_account_number = QLineEdit()
        self.bank_ifsc = QLineEdit()
        self.bank_branch = QLineEdit()
        self.bank_upi_id = QLineEdit()
        
        form_layout.addRow("Bank Name:", self.bank_name)
        form_layout.addRow("Account Holder Name:", self.bank_account_name)
        form_layout.addRow("Account Number:", self.bank_account_number)
        form_layout.addRow("IFSC Code:", self.bank_ifsc)
        form_layout.addRow("Branch:", self.bank_branch)
        form_layout.addRow("UPI ID:", self.bank_upi_id)
        
        layout.addWidget(bank_group)
        layout.addStretch()
        
        return widget
    
    def create_tax_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        tax_group = QGroupBox("Default Tax Rates")
        form_layout = QFormLayout(tax_group)
        
        self.default_cgst = QLineEdit()
        self.default_sgst = QLineEdit()
        self.default_igst = QLineEdit()
        
        form_layout.addRow("Default CGST Rate (%):", self.default_cgst)
        form_layout.addRow("Default SGST Rate (%):", self.default_sgst)
        form_layout.addRow("Default IGST Rate (%):", self.default_igst)
        
        layout.addWidget(tax_group)
        layout.addStretch()
        
        return widget
    
    def create_invoice_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        invoice_group = QGroupBox("Invoice Settings")
        form_layout = QFormLayout(invoice_group)
        
        self.currency_symbol = QLineEdit()
        self.currency_symbol.setMaximumWidth(80)
        self.invoice_prefix = QLineEdit()
        self.invoice_terms = QTextEdit()
        self.invoice_terms.setMaximumHeight(100)
        
        form_layout.addRow("Currency Symbol:", self.currency_symbol)
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        form_layout.addRow("Terms & Conditions:", self.invoice_terms)
        
        layout.addWidget(invoice_group)
        
        # UI Settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.ui_theme = QComboBox()
        self.ui_theme.addItems(["light", "dark"])
        
        ui_layout.addRow("Theme:", self.ui_theme)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        return widget
    
    def create_email_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        smtp_group = QGroupBox("SMTP Configuration")
        form_layout = QFormLayout(smtp_group)
        
        self.smtp_host = QLineEdit()
        self.smtp_host.setPlaceholderText("smtp.gmail.com")
        
        self.smtp_port = QLineEdit()
        self.smtp_port.setPlaceholderText("587")
        
        self.smtp_user = QLineEdit()
        self.smtp_user.setPlaceholderText("your-email@gmail.com")
        
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setPlaceholderText("Your email password or app password")
        
        self.smtp_from_email = QLineEdit()
        self.smtp_from_email.setPlaceholderText("sender@example.com")
        
        self.smtp_use_tls = QCheckBox("Use TLS/SSL")
        self.smtp_use_tls.setChecked(True)
        
        form_layout.addRow("SMTP Host:", self.smtp_host)
        form_layout.addRow("SMTP Port:", self.smtp_port)
        form_layout.addRow("Username:", self.smtp_user)
        form_layout.addRow("Password:", self.smtp_password)
        form_layout.addRow("From Email:", self.smtp_from_email)
        form_layout.addRow("", self.smtp_use_tls)
        
        layout.addWidget(smtp_group)
        
        # Test Email Section
        test_group = QGroupBox("Test Email Configuration")
        test_layout = QFormLayout(test_group)
        
        self.test_email = QLineEdit()
        self.test_email.setPlaceholderText("Enter email address to send test")
        
        self.test_btn = QPushButton("Send Test Email")
        self.test_btn.clicked.connect(self.send_test_email)
        
        test_layout.addRow("Test Email:", self.test_email)
        test_layout.addRow("", self.test_btn)
        
        layout.addWidget(test_group)
        layout.addStretch()
        
        return widget
    
    def create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        backup_group = QGroupBox("Backup Settings")
        form_layout = QFormLayout(backup_group)
        
        self.auto_backup = QCheckBox("Enable Auto Backup")
        self.backup_path = QLineEdit()
        self.backup_path.setPlaceholderText("Select backup directory")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_backup_path)
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path)
        backup_path_layout.addWidget(browse_btn)
        
        form_layout.addRow("", self.auto_backup)
        form_layout.addRow("Backup Path:", backup_path_layout)
        
        layout.addWidget(backup_group)
        
        # Manual backup buttons
        button_layout = QHBoxLayout()
        
        backup_now_btn = QPushButton("💿 Backup Now")
        backup_now_btn.setMinimumHeight(40)
        backup_now_btn.clicked.connect(self.backup_database)
        
        restore_btn = QPushButton("🔄 Restore Database")
        restore_btn.setMinimumHeight(40)
        restore_btn.clicked.connect(self.restore_database)
        
        button_layout.addWidget(backup_now_btn)
        button_layout.addWidget(restore_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def browse_backup_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            self.backup_path.setText(directory)
    
    def upload_logo(self):
        current_logo = self.controller.get_setting('company_logo')
        dialog = LogoUploadDialog(current_logo, self)
        if dialog.exec_():
            logo_data = dialog.get_logo_data()
            if logo_data:
                self.controller.update_setting('company_logo', logo_data)
                self.display_logo(logo_data)
                QMessageBox.information(self, "Success", "Logo uploaded successfully!")
            else:
                self.controller.update_setting('company_logo', '')
                self.logo_preview.setText("No Logo")
                self.logo_preview.setPixmap(QPixmap())
                QMessageBox.information(self, "Success", "Logo removed!")
    
    def remove_logo(self):
        reply = QMessageBox.question(self, "Remove Logo", 
                                    "Are you sure you want to remove the logo?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.update_setting('company_logo', '')
            self.logo_preview.setText("No Logo")
            self.logo_preview.setPixmap(QPixmap())
            QMessageBox.information(self, "Success", "Logo removed successfully!")
    
    def display_logo(self, logo_data):
        if logo_data:
            try:
                from PyQt5.QtGui import QPixmap
                import base64
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(logo_data))
                scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
            except:
                self.logo_preview.setText("Invalid Logo")
    
    def send_test_email(self):
        email = self.test_email.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Please enter a test email address!")
            return
        
        from services.email_service import EmailService
        email_service = EmailService()
        
        # Create a simple test email
        subject = "Test Email from Invoice System"
        body = """
        <h2>Test Email</h2>
        <p>This is a test email from your Invoice Management System.</p>
        <p>If you received this email, your SMTP settings are configured correctly!</p>
        <br>
        <p>Best regards,<br>Invoice System</p>
        """
        
        success, message = email_service.send_email(email, subject, body)
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
            self.display_logo(logo_data)
        else:
            self.logo_preview.setText("No Logo")
    
    def save_settings(self):
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
        
        QMessageBox.information(self, "Success", "All settings saved successfully!")
    
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
                    QApplication.quit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database!")
    
    def refresh(self):
        self.load_settings()