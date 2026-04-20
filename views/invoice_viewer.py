from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
                             QHeaderView, QFrame)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController

class InvoiceViewer(QDialog):
    def __init__(self, invoice_data, auth_service, parent=None):
        super().__init__(parent)
        self.invoice = invoice_data
        self.auth_service = auth_service
        self.settings_controller = SettingsController()
        self.setup_ui()
        self.setWindowTitle(f"Invoice {invoice_data['invoice_number']}")
        self.setModal(True)
        self.resize(800, 700)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        settings = self.settings_controller.get_settings()
        currency = settings.get('currency_symbol', '₹')
        business_name = settings.get('business_name', 'Business Name')
        
        # Header Frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 5px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        business_label = QLabel(business_name)
        business_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        business_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(business_label)
        
        header_layout.addWidget(QLabel(settings.get('business_address', '')))
        header_layout.addWidget(QLabel(f"Phone: {settings.get('business_phone', '')}"))
        header_layout.addWidget(QLabel(f"Email: {settings.get('business_email', '')}"))
        header_layout.addWidget(QLabel(f"GST: {settings.get('business_gst', '')}"))
        
        layout.addWidget(header_frame)
        
        # Invoice Title
        title = QLabel(f"TAX INVOICE")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        title2 = QLabel(f"Invoice #: {self.invoice['invoice_number']}")
        title2.setStyleSheet("font-size: 16px;")
        title2.setAlignment(Qt.AlignCenter)
        layout.addWidget(title2)
        
        # Customer and Invoice Details
        details_frame = QFrame()
        details_layout = QHBoxLayout(details_frame)
        
        # Customer Details
        customer_group = QFrame()
        customer_group.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px;")
        customer_layout = QVBoxLayout(customer_group)
        customer_layout.addWidget(QLabel("<b>Bill To:</b>"))
        customer_layout.addWidget(QLabel(f"Name: {self.invoice.get('customer_name', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"Address: {self.invoice.get('address', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"Phone: {self.invoice.get('phone', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"GST: {self.invoice.get('gst_number', 'N/A')}"))
        details_layout.addWidget(customer_group)
        
        # Invoice Details
        invoice_group = QFrame()
        invoice_group.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px;")
        invoice_layout = QVBoxLayout(invoice_group)
        invoice_layout.addWidget(QLabel("<b>Invoice Details:</b>"))
        invoice_layout.addWidget(QLabel(f"Invoice Date: {self.invoice['invoice_date'][:10]}"))
        invoice_layout.addWidget(QLabel(f"Due Date: {self.invoice.get('due_date', 'N/A')[:10] if self.invoice.get('due_date') else 'N/A'}"))
        invoice_layout.addWidget(QLabel(f"Status: {self.invoice.get('status', 'pending').upper()}"))
        details_layout.addWidget(invoice_group)
        
        layout.addWidget(details_frame)
        
        # Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Product", "HSN", "Quantity", "Unit Price", "Tax", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.items_table.setRowCount(len(self.invoice['items']))
        for row, item in enumerate(self.invoice['items']):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(item.get('hsn_code', '')))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{currency}{item['unit_price']:.2f}"))
            
            tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{tax_rate}%"))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"{currency}{item['total']:.2f}"))
        
        layout.addWidget(self.items_table)
        
        # Totals
        totals_frame = QFrame()
        totals_frame.setStyleSheet("margin-top: 20px;")
        totals_layout = QVBoxLayout(totals_frame)
        
        totals_layout.addWidget(QLabel(f"<b>Subtotal:</b> {currency}{self.invoice['subtotal']:.2f}"))
        totals_layout.addWidget(QLabel(f"<b>Tax Total:</b> {currency}{self.invoice['tax_total']:.2f}"))
        
        total_label = QLabel(f"<b>Grand Total:</b> {currency}{self.invoice['grand_total']:.2f}")
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        totals_layout.addWidget(total_label)
        
        layout.addWidget(totals_frame)
        
        # Notes
        if self.invoice.get('notes'):
            notes_frame = QFrame()
            notes_frame.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; margin-top: 10px;")
            notes_layout = QVBoxLayout(notes_frame)
            notes_layout.addWidget(QLabel("<b>Notes:</b>"))
            notes_layout.addWidget(QLabel(self.invoice['notes']))
            layout.addWidget(notes_frame)
        
        # Terms
        terms = settings.get('invoice_terms', '')
        if terms:
            terms_frame = QFrame()
            terms_frame.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; margin-top: 10px;")
            terms_layout = QVBoxLayout(terms_frame)
            terms_layout.addWidget(QLabel("<b>Terms & Conditions:</b>"))
            terms_layout.addWidget(QLabel(terms))
            layout.addWidget(terms_frame)
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; margin-top: 20px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)