from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt

class CustomerDialog(QDialog):
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setup_ui()
        if customer:
            self.setWindowTitle("Edit Customer")
            self.load_data()
        else:
            self.setWindowTitle("Add Customer")
        self.setModal(True)
        self.resize(500, 450)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(100)
        self.gst_input = QLineEdit()
        
        form_layout.addRow("Name *:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("GST Number:", self.gst_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        self.name_input.setText(self.customer.get('name', ''))
        self.phone_input.setText(self.customer.get('phone', ''))
        self.email_input.setText(self.customer.get('email', ''))
        self.address_input.setText(self.customer.get('address', ''))
        self.gst_input.setText(self.customer.get('gst_number', ''))
    
    def get_data(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Customer name is required!")
            return None
        
        return {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.toPlainText().strip(),
            'gst_number': self.gst_input.text().strip()
        }
    
    def accept(self):
        if self.get_data():
            super().accept()