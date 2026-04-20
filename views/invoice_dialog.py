from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QSpinBox, QDoubleSpinBox, QMessageBox, QHeaderView,
                             QTextEdit, QDateEdit, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from models.customer import Customer
from models.product import Product
from controllers.settings_controller import SettingsController
from services.tax_service import TaxService

class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_model = Customer()
        self.product_model = Product()
        self.settings = SettingsController()
        self.tax_service = TaxService()
        self.items = []
        self.is_interstate = False
        self.setup_ui()
        self.load_data()
        self.setWindowTitle("Create Invoice")
        self.setModal(True)
        self.resize(1000, 700)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Customer selection
        form_layout = QFormLayout()
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.currentIndexChanged.connect(self.on_customer_change)
        form_layout.addRow("Customer:", self.customer_combo)
        
        # GST checkbox for interstate
        self.gst_check = QCheckBox("Inter-State Sale (IGST applies)")
        self.gst_check.toggled.connect(self.on_gst_type_change)
        form_layout.addRow("", self.gst_check)
        
        layout.addLayout(form_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels(["Product", "HSN", "Qty", "Price", "CGST", "SGST", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.items_table)
        
        # Add item button
        self.add_item_btn = QPushButton("➕ Add Item")
        self.add_item_btn.clicked.connect(self.add_item)
        layout.addWidget(self.add_item_btn)
        
        # Totals
        totals_frame = QWidget()
        totals_layout = QFormLayout(totals_frame)
        
        self.subtotal_label = QLabel("₹0.00")
        self.cgst_label = QLabel("₹0.00")
        self.sgst_label = QLabel("₹0.00")
        self.igst_label = QLabel("₹0.00")
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")
        
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        totals_layout.addRow("CGST:", self.cgst_label)
        totals_layout.addRow("SGST:", self.sgst_label)
        totals_layout.addRow("IGST:", self.igst_label)
        totals_layout.addRow("Grand Total:", self.total_label)
        
        layout.addWidget(totals_frame)
        
        # Due date
        due_layout = QHBoxLayout()
        due_layout.addWidget(QLabel("Due Date:"))
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        due_layout.addWidget(self.due_date)
        due_layout.addStretch()
        layout.addLayout(due_layout)
        
        # Notes and Terms
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_input)
        
        self.terms_input = QTextEdit()
        self.terms_input.setMaximumHeight(60)
        layout.addWidget(QLabel("Terms & Conditions:"))
        layout.addWidget(self.terms_input)
        
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
        customers = self.customer_model.get_all()
        if customers:
            for customer in customers:
                self.customer_combo.addItem(f"{customer['name']} - {customer.get('gst_number', 'No GST')}", 
                                           customer['id'])
    
    def on_customer_change(self):
        # Check if customer has GST (for interstate determination)
        customer_id = self.customer_combo.currentData()
        if customer_id:
            customer = self.customer_model.get_by_id(customer_id)
            if customer and customer.get('gst_number'):
                self.gst_check.setEnabled(True)
            else:
                self.gst_check.setEnabled(False)
                self.gst_check.setChecked(False)
    
    def on_gst_type_change(self):
        self.is_interstate = self.gst_check.isChecked()
        # Refresh items to recalculate tax
        if self.items:
            self.refresh_items_table()
            self.calculate_totals()
    
    def add_item(self):
        products = self.product_model.get_all()
        if not products:
            QMessageBox.warning(self, "No Products", "Please add products first!")
            return
        
        dialog = AddItemDialog(products, self.is_interstate, self)
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
            self.items_table.setItem(row, 1, QTableWidgetItem(item.get('hsn_code', '')))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"₹{item['unit_price']:.2f}"))
            
            if self.is_interstate:
                self.items_table.setItem(row, 4, QTableWidgetItem("-"))
                self.items_table.setItem(row, 5, QTableWidgetItem("-"))
            else:
                self.items_table.setItem(row, 4, QTableWidgetItem(f"{item.get('cgst_rate', 0)}%"))
                self.items_table.setItem(row, 5, QTableWidgetItem(f"{item.get('sgst_rate', 0)}%"))
            
            self.items_table.setItem(row, 6, QTableWidgetItem(f"₹{item['total']:.2f}"))
    
    def calculate_totals(self):
        subtotal = sum(item['subtotal'] for item in self.items)
        cgst_total = sum(item.get('cgst_amount', 0) for item in self.items)
        sgst_total = sum(item.get('sgst_amount', 0) for item in self.items)
        igst_total = sum(item.get('igst_amount', 0) for item in self.items)
        total = subtotal + cgst_total + sgst_total + igst_total
        
        self.subtotal_label.setText(f"₹{subtotal:.2f}")
        self.cgst_label.setText(f"₹{cgst_total:.2f}")
        self.sgst_label.setText(f"₹{sgst_total:.2f}")
        self.igst_label.setText(f"₹{igst_total:.2f}")
        self.total_label.setText(f"₹{total:.2f}")
    
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
            'notes': self.notes_input.toPlainText(),
            'terms': self.terms_input.toPlainText(),
            'due_date': self.due_date.date().toString("yyyy-MM-dd")
        }
    
    def accept(self):
        if self.get_invoice_data():
            super().accept()


class AddItemDialog(QDialog):
    def __init__(self, products, is_interstate, parent=None):
        super().__init__(parent)
        self.products = products
        self.is_interstate = is_interstate
        self.selected_product = None
        self.setup_ui()
        self.setWindowTitle("Add Item")
        self.setModal(True)
        self.setFixedSize(500, 400)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        for product in self.products:
            self.product_combo.addItem(
                f"{product['name']} - ₹{product['price']:.2f} ({product.get('hsn_code', 'No HSN')})", 
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
        
        # Tax info display
        self.tax_info = QLabel()
        self.tax_info.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(self.tax_info)
        
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
        
        self.on_product_change()
    
    def on_product_change(self):
        product_id = self.product_combo.currentData()
        for product in self.products:
            if product['id'] == product_id:
                self.selected_product = product
                break
        
        if self.selected_product:
            if self.is_interstate:
                igst = self.selected_product.get('tax_rate_igst', 0)
                self.tax_info.setText(f"IGST: {igst}% (Inter-state sale)")
            else:
                cgst = self.selected_product.get('tax_rate_cgst', 0)
                sgst = self.selected_product.get('tax_rate_sgst', 0)
                self.tax_info.setText(f"CGST: {cgst}% | SGST: {sgst}% (Intra-state sale)")
    
    def get_item(self):
        if not self.selected_product:
            return None
        
        quantity = self.quantity_spin.value()
        unit_price = self.selected_product['price']
        subtotal = quantity * unit_price
        
        if self.is_interstate:
            igst_rate = self.selected_product.get('tax_rate_igst', 0)
            igst_amount = subtotal * igst_rate / 100
            total = subtotal + igst_amount
            
            return {
                'product_id': self.selected_product['id'],
                'product_name': self.selected_product['name'],
                'hsn_code': self.selected_product.get('hsn_code', ''),
                'quantity': quantity,
                'unit_price': unit_price,
                'cgst_rate': 0,
                'sgst_rate': 0,
                'igst_rate': igst_rate,
                'subtotal': subtotal,
                'cgst_amount': 0,
                'sgst_amount': 0,
                'igst_amount': igst_amount,
                'total': total
            }
        else:
            cgst_rate = self.selected_product.get('tax_rate_cgst', 0)
            sgst_rate = self.selected_product.get('tax_rate_sgst', 0)
            cgst_amount = subtotal * cgst_rate / 100
            sgst_amount = subtotal * sgst_rate / 100
            total = subtotal + cgst_amount + sgst_amount
            
            return {
                'product_id': self.selected_product['id'],
                'product_name': self.selected_product['name'],
                'hsn_code': self.selected_product.get('hsn_code', ''),
                'quantity': quantity,
                'unit_price': unit_price,
                'cgst_rate': cgst_rate,
                'sgst_rate': sgst_rate,
                'igst_rate': 0,
                'subtotal': subtotal,
                'cgst_amount': cgst_amount,
                'sgst_amount': sgst_amount,
                'igst_amount': 0,
                'total': total
            }