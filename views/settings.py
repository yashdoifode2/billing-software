from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox,
                             QTextEdit, QFileDialog, QMessageBox, QComboBox,
                             QCheckBox, QTabWidget)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from utils.backup_restore import BackupRestore

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
        
        # Tab widget for settings
        self.tab_widget = QTabWidget()
        
        # Business tab
        self.business_tab = self.create_business_tab()
        self.tab_widget.addTab(self.business_tab, "Business Info")
        
        # Tax tab
        self.tax_tab = self.create_tax_tab()
        self.tab_widget.addTab(self.tax_tab, "Tax Settings")
        
        # Invoice tab
        self.invoice_tab = self.create_invoice_tab()
        self.tab_widget.addTab(self.invoice_tab, "Invoice Settings")
        
        # Backup tab
        self.backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(self.backup_tab, "Backup & Restore")
        
        layout.addWidget(self.tab_widget)
        
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
        
        group = QGroupBox("Business Information")
        form_layout = QFormLayout(group)
        
        self.business_name = QLineEdit()
        self.business_address = QTextEdit()
        self.business_address.setMaximumHeight(80)
        self.business_phone = QLineEdit()
        self.business_email = QLineEdit()
        self.business_gst = QLineEdit()
        self.business_pan = QLineEdit()
        
        form_layout.addRow("Business Name:", self.business_name)
        form_layout.addRow("Address:", self.business_address)
        form_layout.addRow("Phone:", self.business_phone)
        form_layout.addRow("Email:", self.business_email)
        form_layout.addRow("GST Number:", self.business_gst)
        form_layout.addRow("PAN Number:", self.business_pan)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return widget
    
    def create_tax_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Default Tax Rates")
        form_layout = QFormLayout(group)
        
        self.default_cgst = QLineEdit()
        self.default_sgst = QLineEdit()
        self.default_igst = QLineEdit()
        
        form_layout.addRow("Default CGST Rate (%):", self.default_cgst)
        form_layout.addRow("Default SGST Rate (%):", self.default_sgst)
        form_layout.addRow("Default IGST Rate (%):", self.default_igst)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return widget
    
    def create_invoice_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Invoice Settings")
        form_layout = QFormLayout(group)
        
        self.currency_symbol = QLineEdit()
        self.currency_symbol.setMaximumWidth(80)
        self.invoice_prefix = QLineEdit()
        self.invoice_terms = QTextEdit()
        self.invoice_terms.setMaximumHeight(100)
        
        form_layout.addRow("Currency Symbol:", self.currency_symbol)
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        form_layout.addRow("Terms & Conditions:", self.invoice_terms)
        
        layout.addWidget(group)
        
        # UI Settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.ui_theme = QComboBox()
        self.ui_theme.addItems(["light", "dark"])
        
        ui_layout.addRow("Theme:", self.ui_theme)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        return widget
    
    def create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Backup Settings")
        form_layout = QFormLayout(group)
        
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
        
        layout.addWidget(group)
        
        # Manual backup buttons
        button_layout = QHBoxLayout()
        
        backup_now_btn = QPushButton("💿 Backup Now")
        backup_now_btn.clicked.connect(self.backup_database)
        
        restore_btn = QPushButton("🔄 Restore Database")
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
    
    def load_settings(self):
        settings = self.controller.get_settings()
        self.business_name.setText(settings.get('business_name', ''))
        self.business_address.setText(settings.get('business_address', ''))
        self.business_phone.setText(settings.get('business_phone', ''))
        self.business_email.setText(settings.get('business_email', ''))
        self.business_gst.setText(settings.get('business_gst', ''))
        self.business_pan.setText(settings.get('business_pan', ''))
        self.currency_symbol.setText(settings.get('currency_symbol', '₹'))
        self.invoice_prefix.setText(settings.get('invoice_prefix', 'INV'))
        self.invoice_terms.setText(settings.get('invoice_terms', ''))
        self.default_cgst.setText(settings.get('default_cgst', '9'))
        self.default_sgst.setText(settings.get('default_sgst', '9'))
        self.default_igst.setText(settings.get('default_igst', '18'))
        
        theme_index = self.ui_theme.findText(settings.get('ui_theme', 'light'))
        if theme_index >= 0:
            self.ui_theme.setCurrentIndex(theme_index)
        
        self.auto_backup.setChecked(settings.get('backup_enabled', '0') == '1')
        self.backup_path.setText(settings.get('backup_path', ''))
    
    def save_settings(self):
        self.controller.update_setting('business_name', self.business_name.text())
        self.controller.update_setting('business_address', self.business_address.toPlainText())
        self.controller.update_setting('business_phone', self.business_phone.text())
        self.controller.update_setting('business_email', self.business_email.text())
        self.controller.update_setting('business_gst', self.business_gst.text())
        self.controller.update_setting('business_pan', self.business_pan.text())
        self.controller.update_setting('currency_symbol', self.currency_symbol.text())
        self.controller.update_setting('invoice_prefix', self.invoice_prefix.text())
        self.controller.update_setting('invoice_terms', self.invoice_terms.toPlainText())
        self.controller.update_setting('default_cgst', self.default_cgst.text())
        self.controller.update_setting('default_sgst', self.default_sgst.text())
        self.controller.update_setting('default_igst', self.default_igst.text())
        self.controller.update_setting('ui_theme', self.ui_theme.currentText())
        self.controller.update_setting('backup_enabled', '1' if self.auto_backup.isChecked() else '0')
        self.controller.update_setting('backup_path', self.backup_path.text())
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
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