from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QTextEdit, QPushButton, QDoubleSpinBox, 
                             QMessageBox, QComboBox, QLabel)
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
        self.setModal(True)
        self.resize(550, 600)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.hsn_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setPrefix("₹ ")
        self.price_input.setDecimals(2)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 999999)
        self.cost_input.setPrefix("₹ ")
        self.cost_input.setDecimals(2)
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["pcs", "kg", "litre", "meter", "dozen", "box"])
        
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setRange(0, 999999)
        self.stock_input.setDecimals(2)
        
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setRange(0, 100)
        self.cgst_input.setSuffix(" %")
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(9)
        
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setRange(0, 100)
        self.sgst_input.setSuffix(" %")
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(9)
        
        self.igst_input = QDoubleSpinBox()
        self.igst_input.setRange(0, 100)
        self.igst_input.setSuffix(" %")
        self.igst_input.setDecimals(2)
        self.igst_input.setValue(0)
        
        form_layout.addRow("Name *:", self.name_input)
        form_layout.addRow("HSN Code:", self.hsn_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Selling Price *:", self.price_input)
        form_layout.addRow("Cost Price:", self.cost_input)
        form_layout.addRow("Unit:", self.unit_combo)
        form_layout.addRow("Stock Quantity:", self.stock_input)
        form_layout.addRow(QLabel("<b>Tax Rates</b>"))
        form_layout.addRow("CGST Rate:", self.cgst_input)
        form_layout.addRow("SGST Rate:", self.sgst_input)
        form_layout.addRow("IGST Rate:", self.igst_input)
        
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
        self.hsn_input.setText(self.product.get('hsn_code', ''))
        self.description_input.setText(self.product.get('description', ''))
        self.price_input.setValue(self.product.get('price', 0))
        self.cost_input.setValue(self.product.get('cost_price', 0))
        
        index = self.unit_combo.findText(self.product.get('unit', 'pcs'))
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        
        self.stock_input.setValue(self.product.get('stock_quantity', 0))
        self.cgst_input.setValue(self.product.get('tax_rate_cgst', 0))
        self.sgst_input.setValue(self.product.get('tax_rate_sgst', 0))
        self.igst_input.setValue(self.product.get('tax_rate_igst', 0))
    
    def get_data(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return None
        
        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Selling price must be greater than 0!")
            return None
        
        return {
            'name': self.name_input.text().strip(),
            'hsn_code': self.hsn_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'price': self.price_input.value(),
            'cost_price': self.cost_input.value(),
            'unit': self.unit_combo.currentText(),
            'stock_quantity': self.stock_input.value(),
            'tax_rate_cgst': self.cgst_input.value(),
            'tax_rate_sgst': self.sgst_input.value(),
            'tax_rate_igst': self.igst_input.value()
        }
    
    def accept(self):
        if self.get_data():
            super().accept()