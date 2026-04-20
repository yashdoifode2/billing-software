from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QDoubleSpinBox, QMessageBox, QHeaderView,
                             QTextEdit, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QDate
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.customer import Customer
from models.product import Product
from models.invoice import Invoice

class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_model = Customer()
        self.product_model = Product()
        self.invoice_model = Invoice()
        self.items = []
        self.setup_ui()
        self.load_data()
        self.setWindowTitle("Create Invoice")
        self.setModal(True)
        self.resize(900, 700)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Customer selection
        customer_group = QGroupBox("Customer Information")
        customer_layout = QFormLayout(customer_group)
        
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(35)
        customer_layout.addRow("Select Customer:", self.customer_combo)
        
        layout.addWidget(customer_group)
        
        # Items section
        items_group = QGroupBox("Invoice Items")
        items_layout = QVBoxLayout(items_group)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Price", "Tax%", "Total", "Actions"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        items_layout.addWidget(self.items_table)
        
        # Add item button
        self.add_item_btn = QPushButton("➕ Add Product")
        self.add_item_btn.setMinimumHeight(35)
        self.add_item_btn.clicked.connect(self.add_item)
        items_layout.addWidget(self.add_item_btn)
        
        layout.addWidget(items_group)
        
        # Totals section
        totals_group = QGroupBox("Invoice Summary")
        totals_layout = QFormLayout(totals_group)
        
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-size: 14px;")
        self.tax_label = QLabel("₹0.00")
        self.tax_label.setStyleSheet("font-size: 14px;")
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        totals_layout.addRow("Tax Amount:", self.tax_label)
        totals_layout.addRow("Grand Total:", self.total_label)
        
        layout.addWidget(totals_group)
        
        # Invoice details
        details_group = QGroupBox("Invoice Details")
        details_layout = QFormLayout(details_group)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        details_layout.addRow("Due Date:", self.due_date)
        details_layout.addRow("Notes:", self.notes_input)
        
        layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Invoice")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_invoice)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
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
                self.customer_combo.addItem(f"{customer['name']} - {customer.get('phone', 'No phone')}", 
                                           customer['id'])
    
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
            self.items_table.setItem(row, 2, QTableWidgetItem(f"₹{item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item.get('tax_rate', 0)}%"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"₹{item['total']:.2f}"))
            
            # Remove button
            remove_btn = QPushButton("❌")
            remove_btn.setFixedSize(30, 25)
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 5, remove_btn)
        
        self.items_table.resizeColumnsToContents()
    
    def remove_item(self, row):
        self.items.pop(row)
        self.refresh_items_table()
        self.calculate_totals()
    
    def calculate_totals(self):
        subtotal = sum(item['subtotal'] for item in self.items)
        tax = sum(item.get('tax_amount', 0) for item in self.items)
        total = subtotal + tax
        
        self.subtotal_label.setText(f"₹{subtotal:.2f}")
        self.tax_label.setText(f"₹{tax:.2f}")
        self.total_label.setText(f"₹{total:.2f}")
    
    def save_invoice(self):
        if self.customer_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Error", "Please select a customer!")
            return
        
        if not self.items:
            QMessageBox.warning(self, "Error", "Please add at least one item!")
            return
        
        customer_id = self.customer_combo.currentData()
        notes = self.notes_input.toPlainText()
        
        # Prepare items for saving
        invoice_items = []
        for item in self.items:
            invoice_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'tax_rate': item.get('tax_rate', 0),
                'cgst_rate': item.get('cgst_rate', 0),
                'sgst_rate': item.get('sgst_rate', 0),
                'igst_rate': item.get('igst_rate', 0),
                'cgst_amount': item.get('cgst_amount', 0),
                'sgst_amount': item.get('sgst_amount', 0),
                'igst_amount': item.get('igst_amount', 0),
                'tax_amount': item.get('tax_amount', 0),
                'total': item['total']
            })
        
        try:
            invoice_id = self.invoice_model.create(customer_id, invoice_items, notes)
            if invoice_id:
                QMessageBox.information(self, "Success", f"Invoice created successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create invoice!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating invoice: {str(e)}")
    
    def accept(self):
        self.save_invoice()


class AddItemDialog(QDialog):
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.products = products
        self.selected_product = None
        self.setup_ui()
        self.setWindowTitle("Add Product to Invoice")
        self.setModal(True)
        self.setFixedSize(450, 350)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        for product in self.products:
            self.product_combo.addItem(
                f"{product['name']} - ₹{product['price']:.2f}", 
                product['id']
            )
        self.product_combo.currentIndexChanged.connect(self.on_product_change)
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 9999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setDecimals(2)
        
        form_layout.addRow("Product:", self.product_combo)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        layout.addLayout(form_layout)
        
        # Product details
        self.details_label = QLabel()
        self.details_label.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add to Invoice")
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.on_product_change()
    
    def on_product_change(self):
        product_id = self.product_combo.currentData()
        for product in self.products:
            if product['id'] == product_id:
                self.selected_product = product
                break
        
        if self.selected_product:
            cgst = self.selected_product.get('tax_rate_cgst', 0)
            sgst = self.selected_product.get('tax_rate_sgst', 0)
            igst = self.selected_product.get('tax_rate_igst', 0)
            tax_rate = cgst + sgst + igst
            
            self.details_label.setText(
                f"Price: ₹{self.selected_product['price']:.2f}\n"
                f"Tax Rate: {tax_rate}% (CGST: {cgst}%, SGST: {sgst}%, IGST: {igst}%)"
            )
    
    def get_item(self):
        if not self.selected_product:
            return None
        
        quantity = self.quantity_spin.value()
        unit_price = self.selected_product['price']
        subtotal = quantity * unit_price
        
        cgst_rate = self.selected_product.get('tax_rate_cgst', 0)
        sgst_rate = self.selected_product.get('tax_rate_sgst', 0)
        igst_rate = self.selected_product.get('tax_rate_igst', 0)
        tax_rate = cgst_rate + sgst_rate + igst_rate
        tax_amount = subtotal * tax_rate / 100
        total = subtotal + tax_amount
        
        return {
            'product_id': self.selected_product['id'],
            'product_name': self.selected_product['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'tax_rate': tax_rate,
            'cgst_rate': cgst_rate,
            'sgst_rate': sgst_rate,
            'igst_rate': igst_rate,
            'cgst_amount': subtotal * cgst_rate / 100,
            'sgst_amount': subtotal * sgst_rate / 100,
            'igst_amount': subtotal * igst_rate / 100,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total
        }