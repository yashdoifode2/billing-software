from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
                             QHeaderView)
from PyQt5.QtCore import Qt
from controllers.settings_controller import SettingsController

class InvoiceViewer(QDialog):
    def __init__(self, invoice_data, parent=None):
        super().__init__(parent)
        self.invoice = invoice_data
        self.settings = SettingsController()
        self.setup_ui()
        self.setWindowTitle(f"Invoice {invoice_data['invoice_number']}")
        self.setModal(True)
        self.resize(800, 700)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        settings = self.settings.get_settings()
        currency = settings.get('currency_symbol', '$')
        
        # Business info
        business_label = QLabel(settings.get('business_name', 'Business Name'))
        business_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        business_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(business_label)
        
        layout.addWidget(QLabel(settings.get('business_address', '')))
        layout.addWidget(QLabel(f"Phone: {settings.get('business_phone', '')}"))
        layout.addWidget(QLabel(f"Email: {settings.get('business_email', '')}"))
        
        # Invoice title
        title = QLabel(f"INVOICE #{self.invoice['invoice_number']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel(f"Date: {self.invoice['invoice_date'][:10]}"))
        
        # Customer info
        layout.addWidget(QLabel("\nBill To:"))
        layout.addWidget(QLabel(f"Name: {self.invoice.get('customer_name', 'N/A')}"))
        layout.addWidget(QLabel(f"Address: {self.invoice.get('address', 'N/A')}"))
        layout.addWidget(QLabel(f"Phone: {self.invoice.get('phone', 'N/A')}"))
        layout.addWidget(QLabel(f"GST: {self.invoice.get('gst_number', 'N/A')}"))
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Tax", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.items_table.setRowCount(len(self.invoice['items']))
        for row, item in enumerate(self.invoice['items']):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{currency}{item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['tax_rate']}%"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{currency}{item['total']:.2f}"))
        
        layout.addWidget(self.items_table)
        
        # Totals
        layout.addWidget(QLabel(f"Subtotal: {currency}{self.invoice['subtotal']:.2f}"))
        layout.addWidget(QLabel(f"Tax Total: {currency}{self.invoice['tax_total']:.2f}"))
        total_label = QLabel(f"Grand Total: {currency}{self.invoice['grand_total']:.2f}")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(total_label)
        
        # Notes
        if self.invoice.get('notes'):
            layout.addWidget(QLabel("\nNotes:"))
            layout.addWidget(QLabel(self.invoice['notes']))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)