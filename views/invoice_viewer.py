from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QComboBox, QMessageBox, QDoubleSpinBox, QHeaderView)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from models.invoice import Invoice

class InvoiceViewer(QDialog):
    def __init__(self, invoice_data, auth_service, parent=None):
        super().__init__(parent)
        self.invoice = invoice_data
        self.auth_service = auth_service
        self.settings_controller = SettingsController()
        self.invoice_model = Invoice()
        self.setup_ui()
        self.setWindowTitle(f"Invoice {invoice_data['invoice_number']}")
        self.setModal(True)
        self.resize(900, 800)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        settings = self.settings_controller.get_settings()
        currency = settings.get('currency_symbol', '₹')
        business_name = settings.get('business_name', 'Business Name')
        
        # Business Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px;")
        header_layout = QVBoxLayout(header_frame)
        
        business_label = QLabel(f"<h2>{business_name}</h2>")
        business_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(business_label)
        
        business_details = QLabel(f"{settings.get('business_address', '')}<br>"
                                  f"Phone: {settings.get('business_phone', '')} | Email: {settings.get('business_email', '')}<br>"
                                  f"GST: {settings.get('business_gst', '')}")
        business_details.setAlignment(Qt.AlignCenter)
        business_details.setWordWrap(True)
        header_layout.addWidget(business_details)
        
        layout.addWidget(header_frame)
        
        # Invoice Title and Status
        title_layout = QHBoxLayout()
        invoice_title = QLabel(f"<h2>TAX INVOICE</h2>")
        invoice_title.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(invoice_title)
        title_layout.addStretch()
        
        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 5px;")
        status_layout = QHBoxLayout(status_frame)
        status_layout.addWidget(QLabel("<b>Status:</b>"))
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pending", "paid", "overdue", "cancelled"])
        current_status = self.invoice.get('status', 'pending')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        self.status_combo.currentTextChanged.connect(self.update_status)
        status_layout.addWidget(self.status_combo)
        title_layout.addWidget(status_frame)
        
        layout.addLayout(title_layout)
        
        # Invoice Details
        details_layout = QHBoxLayout()
        details_layout.addWidget(QLabel(f"<b>Invoice No:</b> {self.invoice['invoice_number']}"))
        details_layout.addStretch()
        details_layout.addWidget(QLabel(f"<b>Date:</b> {self.invoice['invoice_date'][:10]}"))
        details_layout.addStretch()
        details_layout.addWidget(QLabel(f"<b>Due Date:</b> {self.invoice.get('due_date', 'N/A')[:10] if self.invoice.get('due_date') else 'N/A'}"))
        layout.addLayout(details_layout)
        
        # Customer Details
        customer_frame = QFrame()
        customer_frame.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; margin-top: 10px;")
        customer_layout = QVBoxLayout(customer_frame)
        customer_layout.addWidget(QLabel("<b>Bill To:</b>"))
        customer_layout.addWidget(QLabel(f"Name: {self.invoice.get('customer_name', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"Address: {self.invoice.get('address', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"Phone: {self.invoice.get('phone', 'N/A')}"))
        customer_layout.addWidget(QLabel(f"GSTIN: {self.invoice.get('gst_number', 'N/A')}"))
        layout.addWidget(customer_frame)
        
        # Items Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["S.No", "Description", "HSN/SAC", "Quantity", "Unit Price", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.setRowCount(len(self.invoice['items']))
        for row, item in enumerate(self.invoice['items'], 1):
            self.table.setItem(row-1, 0, QTableWidgetItem(str(row)))
            self.table.setItem(row-1, 1, QTableWidgetItem(item['product_name']))
            self.table.setItem(row-1, 2, QTableWidgetItem(item.get('hsn_code', '')))
            self.table.setItem(row-1, 3, QTableWidgetItem(str(int(item['quantity'])) if item['quantity'].is_integer() else str(item['quantity'])))
            self.table.setItem(row-1, 4, QTableWidgetItem(f"{currency}{item['unit_price']:.2f}"))
            
            tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
            amount = item['total']
            self.table.setItem(row-1, 5, QTableWidgetItem(f"{currency}{amount:.2f}"))
        
        layout.addWidget(self.table)
        
        # Tax Breakdown
        tax_frame = QFrame()
        tax_frame.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; margin-top: 10px;")
        tax_layout = QVBoxLayout(tax_frame)
        tax_layout.addWidget(QLabel("<b>Tax Breakdown:</b>"))
        
        cgst_total = sum(item.get('cgst_amount', 0) for item in self.invoice['items'])
        sgst_total = sum(item.get('sgst_amount', 0) for item in self.invoice['items'])
        igst_total = sum(item.get('igst_amount', 0) for item in self.invoice['items'])
        
        if cgst_total > 0:
            tax_layout.addWidget(QLabel(f"CGST: {currency}{cgst_total:.2f}"))
        if sgst_total > 0:
            tax_layout.addWidget(QLabel(f"SGST: {currency}{sgst_total:.2f}"))
        if igst_total > 0:
            tax_layout.addWidget(QLabel(f"IGST: {currency}{igst_total:.2f}"))
        
        layout.addWidget(tax_frame)
        
        # Payment Section
        paid_amount = self.invoice.get('paid_amount', 0)
        balance_due = self.invoice['grand_total'] - paid_amount
        
        if self.invoice.get('status') != 'paid' and balance_due > 0:
            payment_frame = QFrame()
            payment_frame.setStyleSheet("border: 1px solid #27ae60; border-radius: 5px; padding: 10px; background-color: #e8f8f5; margin-top: 10px;")
            payment_layout = QHBoxLayout(payment_frame)
            
            payment_layout.addWidget(QLabel("Record Payment:"))
            self.payment_amount = QDoubleSpinBox()
            self.payment_amount.setRange(0.01, balance_due)
            self.payment_amount.setValue(balance_due)
            self.payment_amount.setPrefix(f"{currency} ")
            self.payment_amount.setDecimals(2)
            payment_layout.addWidget(self.payment_amount)
            
            self.payment_method = QComboBox()
            self.payment_method.addItems(["Cash", "Bank Transfer", "Cheque", "Credit Card", "UPI"])
            payment_layout.addWidget(self.payment_method)
            
            pay_btn = QPushButton("Add Payment")
            pay_btn.setStyleSheet("background-color: #27ae60; color: white;")
            pay_btn.clicked.connect(self.add_payment)
            payment_layout.addWidget(pay_btn)
            
            layout.addWidget(payment_frame)
        
        # Totals
        totals_frame = QFrame()
        totals_frame.setStyleSheet("margin-top: 15px; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        totals_layout = QVBoxLayout(totals_frame)
        
        totals_layout.addWidget(QLabel(f"<b>Subtotal:</b> {currency}{self.invoice['subtotal']:.2f}"))
        totals_layout.addWidget(QLabel(f"<b>Tax Total:</b> {currency}{self.invoice['tax_total']:.2f}"))
        
        if paid_amount > 0:
            totals_layout.addWidget(QLabel(f"<b>Paid Amount:</b> {currency}{paid_amount:.2f}"))
            totals_layout.addWidget(QLabel(f"<b>Balance Due:</b> {currency}{balance_due:.2f}"))
        
        total_label = QLabel(f"<h2>Grand Total: {currency}{self.invoice['grand_total']:.2f}</h2>")
        total_label.setStyleSheet("color: #27ae60;")
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
        
        # Button Layout
        button_layout = QHBoxLayout()
        
        # PDF Export Button
        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.setMinimumHeight(40)
        pdf_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(pdf_btn)
        
        button_layout.addStretch()
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def update_status(self, status):
        reply = QMessageBox.question(self, "Update Status", 
                                    f"Change invoice status to '{status.upper()}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.invoice_model.update_status(self.invoice['id'], status)
            self.invoice['status'] = status
            QMessageBox.information(self, "Success", f"Invoice status updated to {status.upper()}")
    
    def add_payment(self):
        amount = self.payment_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid amount!")
            return
        
        payment_method = self.payment_method.currentText()
        
        reply = QMessageBox.question(self, "Record Payment", 
                                    f"Record payment of ₹{amount:.2f} via {payment_method}?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.invoice_model.update_payment_status(self.invoice['id'], amount)
            QMessageBox.information(self, "Success", "Payment recorded successfully!")
            self.accept()  # Close and reopen to refresh
    
    def export_pdf(self):
        from controllers.invoice_controller import InvoiceController
        controller = InvoiceController(None, self.auth_service)
        controller.export_pdf(self.invoice['id'])