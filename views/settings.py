from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox,
                             QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from controllers.settings_controller import SettingsController
from utils.backup_restore import BackupRestore
import os

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = SettingsController()
        self.backup_restore = BackupRestore()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Settings")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Business Information
        business_group = QGroupBox("Business Information")
        business_layout = QFormLayout(business_group)
        
        self.business_name = QLineEdit()
        self.business_address = QTextEdit()
        self.business_address.setMaximumHeight(80)
        self.business_phone = QLineEdit()
        self.business_email = QLineEdit()
        
        business_layout.addRow("Business Name:", self.business_name)
        business_layout.addRow("Address:", self.business_address)
        business_layout.addRow("Phone:", self.business_phone)
        business_layout.addRow("Email:", self.business_email)
        
        layout.addWidget(business_group)
        
        # Invoice Settings
        invoice_group = QGroupBox("Invoice Settings")
        invoice_layout = QFormLayout(invoice_group)
        
        self.gst_percentage = QLineEdit()
        self.currency_symbol = QLineEdit()
        self.invoice_prefix = QLineEdit()
        self.invoice_terms = QTextEdit()
        self.invoice_terms.setMaximumHeight(80)
        
        invoice_layout.addRow("GST Percentage (%):", self.gst_percentage)
        invoice_layout.addRow("Currency Symbol:", self.currency_symbol)
        invoice_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        invoice_layout.addRow("Terms & Conditions:", self.invoice_terms)
        
        layout.addWidget(invoice_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.backup_btn = QPushButton("💿 Backup Database")
        self.backup_btn.clicked.connect(self.backup_database)
        
        self.restore_btn = QPushButton("🔄 Restore Database")
        self.restore_btn.clicked.connect(self.restore_database)
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.backup_btn)
        actions_layout.addWidget(self.restore_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        layout.addStretch()
    
    def load_settings(self):
        settings = self.controller.get_settings()
        self.business_name.setText(settings.get('business_name', ''))
        self.business_address.setText(settings.get('business_address', ''))
        self.business_phone.setText(settings.get('business_phone', ''))
        self.business_email.setText(settings.get('business_email', ''))
        self.gst_percentage.setText(settings.get('gst_percentage', '18'))
        self.currency_symbol.setText(settings.get('currency_symbol', '$'))
        self.invoice_prefix.setText(settings.get('invoice_prefix', 'INV'))
        self.invoice_terms.setText(settings.get('invoice_terms', ''))
    
    def save_settings(self):
        self.controller.update_setting('business_name', self.business_name.text())
        self.controller.update_setting('business_address', self.business_address.toPlainText())
        self.controller.update_setting('business_phone', self.business_phone.text())
        self.controller.update_setting('business_email', self.business_email.text())
        self.controller.update_setting('gst_percentage', self.gst_percentage.text())
        self.controller.update_setting('currency_symbol', self.currency_symbol.text())
        self.controller.update_setting('invoice_prefix', self.invoice_prefix.text())
        self.controller.update_setting('invoice_terms', self.invoice_terms.toPlainText())
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def backup_database(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Backup Files (*.db)")
        if file_path:
            if self.backup_restore.backup(file_path):
                QMessageBox.information(self, "Success", "Database backed up successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to backup database!")
    
    def restore_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database Files (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Confirm Restore", 
                                        "Restoring will overwrite current data. Continue?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.backup_restore.restore(file_path):
                    QMessageBox.information(self, "Success", "Database restored successfully! Please restart the application.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database!")