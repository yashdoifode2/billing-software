from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QTextEdit, QPushButton, QDoubleSpinBox, QMessageBox)
from PyQt5.QtCore import Qt

class ProductDialog(QDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setup_ui()
        if product:
            self.setWindowTitle("Edit Product")
            self.load_data()
        else:
            self.setWindowTitle("Add Product")
    
    def setup_ui(self):
        self.setModal(True)
        self.setFixedSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setPrefix("$ ")
        self.price_input.setDecimals(2)
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setRange(0, 100)
        self.tax_input.setSuffix(" %")
        self.tax_input.setDecimals(2)
        
        form_layout.addRow("Name *:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Price *:", self.price_input)
        form_layout.addRow("Tax Rate (%):", self.tax_input)
        
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
        self.name_input.setText(self.product.get('name', ''))
        self.description_input.setText(self.product.get('description', ''))
        self.price_input.setValue(self.product.get('price', 0))
        self.tax_input.setValue(self.product.get('tax_rate', 0))
    
    def get_data(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return None
        
        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Price must be greater than 0!")
            return None
        
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'price': self.price_input.value(),
            'tax_rate': self.tax_input.value()
        }
    
    def accept(self):
        if self.get_data():
            super().accept()