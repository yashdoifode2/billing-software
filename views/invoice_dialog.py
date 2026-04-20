from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QSpinBox, QDoubleSpinBox, QMessageBox, QHeaderView,
                             QTextEdit)
from PyQt5.QtCore import Qt
from models.customer import Customer
from models.product import Product
from controllers.settings_controller import SettingsController

class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_model = Customer()
        self.product_model = Product()
        self.settings = SettingsController()
        self.items = []
        self.setup_ui()
        self.load_data()
        self.setWindowTitle("Create Invoice")
        self.setModal(True)
        self.resize(800, 600)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer selection
        form_layout = QFormLayout()
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        form_layout.addRow("Customer:", self.customer_combo)
        layout.addLayout(form_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Tax (%)", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.items_table)
        
        # Add item button
        self.add_item_btn = QPushButton("➕ Add Item")
        self.add_item_btn.clicked.connect(self.add_item)
        layout.addWidget(self.add_item_btn)
        
        # Totals
        totals_layout = QFormLayout()
        self.subtotal_label = QLabel("$0.00")
        self.tax_label = QLabel("$0.00")
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        totals_layout.addRow("Tax:", self.tax_label)
        totals_layout.addRow("Grand Total:", self.total_label)
        layout.addLayout(totals_layout)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Invoice")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def load_data(self):
        # Load customers
        customers = self.customer_model.get_all()
        if customers:
            for customer in customers:
                self.customer_combo.addItem(customer['name'], customer['id'])
    
    def add_item(self):
        products = self.product_model.get_all()
        if not products:
            QMessageBox.warning(self, "No Products", "Please add products first!")
            return
            
        dialog = AddItemDialog(products, self)
        if dialog.exec_():
            item = dialog.get_item()
            if item:
                self.items.append(item)
                self.refresh_items_table()
                self.calculate_totals()
    
    def refresh_items_table(self):
        self.items_table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(str(item['tax_rate'])))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"${item['total']:.2f}"))
    
    def calculate_totals(self):
        subtotal = sum(item['subtotal'] for item in self.items)
        tax = sum(item['tax_amount'] for item in self.items)
        total = subtotal + tax
        
        settings = self.settings.get_settings()
        currency = settings.get('currency_symbol', '$')
        
        self.subtotal_label.setText(f"{currency}{subtotal:.2f}")
        self.tax_label.setText(f"{currency}{tax:.2f}")
        self.total_label.setText(f"{currency}{total:.2f}")
    
    def get_invoice_data(self):
        if self.customer_combo.currentIndex() < 0 or self.customer_combo.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a customer!")
            return None
        
        if not self.items:
            QMessageBox.warning(self, "Validation Error", "Please add at least one item!")
            return None
        
        return {
            'customer_id': self.customer_combo.currentData(),
            'items': self.items,
            'notes': self.notes_input.toPlainText()
        }
    
    def accept(self):
        if self.get_invoice_data():
            super().accept()


class AddItemDialog(QDialog):
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.products = products
        self.selected_product = None
        self.setup_ui()
        self.setWindowTitle("Add Item")
        self.setModal(True)
        self.setFixedSize(400, 300)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        for product in self.products:
            self.product_combo.addItem(f"{product['name']} - ${product['price']:.2f}", product['id'])
        self.product_combo.currentIndexChanged.connect(self.on_product_change)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.quantity_spin.setValue(1)
        
        form_layout.addRow("Product:", self.product_combo)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Initialize selected product
        self.on_product_change()
    
    def on_product_change(self):
        product_id = self.product_combo.currentData()
        for product in self.products:
            if product['id'] == product_id:
                self.selected_product = product
                break
    
    def get_item(self):
        if not self.selected_product:
            return None
        
        quantity = self.quantity_spin.value()
        unit_price = self.selected_product['price']
        tax_rate = self.selected_product.get('tax_rate', 0)
        subtotal = quantity * unit_price
        tax_amount = subtotal * tax_rate / 100
        total = subtotal + tax_amount
        
        return {
            'product_id': self.selected_product['id'],
            'product_name': self.selected_product['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'tax_rate': tax_rate,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total
        }