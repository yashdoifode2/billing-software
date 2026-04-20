from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QComboBox, QMessageBox, QDoubleSpinBox, QHeaderView,
                             QLineEdit, QProgressBar, QScrollArea, QSplitter,
                             QWidget, QGridLayout, QGroupBox, QSizePolicy,
                             QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.settings_controller import SettingsController
from models.invoice import Invoice
from utils.pdf_generator import PDFGenerator
from services.email_service import EmailService

class EmailWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def __init__(self, to_email, invoice_data, settings):
        super().__init__()
        self.to_email = to_email
        self.invoice_data = invoice_data
        self.settings = settings
    
    def run(self):
        try:
            self.progress.emit("Generating PDF...")
            
            import tempfile
            import os
            from datetime import datetime
            
            temp_dir = tempfile.gettempdir()
            pdf_filename = f"invoice_{self.invoice_data['invoice_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            pdf_gen = PDFGenerator(self.invoice_data, self.settings)
            pdf_gen.generate(pdf_path)
            
            self.progress.emit("Sending email...")
            
            email_service = EmailService()
            business_name = self.settings.get('business_name', 'Business')
            subject = f"Invoice {self.invoice_data['invoice_number']} from {business_name}"
            
            currency = self.settings.get('currency_symbol', '₹')
            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .invoice-details {{ margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #3498db; color: white; }}
                    .total {{ font-size: 18px; font-weight: bold; color: #27ae60; }}
                    .footer {{ margin-top: 30px; padding: 20px; background-color: #ecf0f1; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>{business_name}</h2>
                    <p>{self.settings.get('business_address', '')}</p>
                    <p>Phone: {self.settings.get('business_phone', '')} | Email: {self.settings.get('business_email', '')}</p>
                </div>
                
                <div class="content">
                    <h2>Invoice {self.invoice_data['invoice_number']}</h2>
                    <p><strong>Date:</strong> {self.invoice_data['invoice_date'][:10]}</p>
                    <p><strong>Due Date:</strong> {self.invoice_data.get('due_date', 'N/A')[:10] if self.invoice_data.get('due_date') else 'N/A'}</p>
                    
                    <div class="invoice-details">
                        <h3>Bill To:</h3>
                        <p>
                            <strong>{self.invoice_data.get('customer_name', 'N/A')}</strong><br>
                            {self.invoice_data.get('address', 'N/A')}<br>
                            Phone: {self.invoice_data.get('phone', 'N/A')}<br>
                            GST: {self.invoice_data.get('gst_number', 'N/A')}
                        </p>
                    </div>
                    
                    <h3>Invoice Items:</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Tax</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for item in self.invoice_data['items']:
                tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
                body += f"""
                            <tr>
                                <td>{item['product_name']}</td>
                                <td>{int(item['quantity']) if item['quantity'].is_integer() else item['quantity']}</td>
                                <td>{currency}{item['unit_price']:.2f}</td>
                                <td>{tax_rate}%</td>
                                <td>{currency}{item['total']:.2f}</td>
                            </tr>
                """
            
            body += f"""
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 20px; text-align: right;">
                        <p><strong>Subtotal:</strong> {currency}{self.invoice_data['subtotal']:.2f}</p>
                        <p><strong>Tax Total:</strong> {currency}{self.invoice_data['tax_total']:.2f}</p>
                        <p class="total"><strong>Grand Total:</strong> {currency}{self.invoice_data['grand_total']:.2f}</p>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <h3>Bank Details:</h3>
                        <p>
                            <strong>Bank:</strong> {self.settings.get('bank_name', 'N/A')}<br>
                            <strong>Account Name:</strong> {self.settings.get('bank_account_name', 'N/A')}<br>
                            <strong>Account Number:</strong> {self.settings.get('bank_account_number', 'N/A')}<br>
                            <strong>IFSC Code:</strong> {self.settings.get('bank_ifsc', 'N/A')}<br>
                            <strong>UPI ID:</strong> {self.settings.get('bank_upi_id', 'N/A')}
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>{self.settings.get('invoice_terms', 'Thank you for your business!')}</p>
                    <p><small>This is a computer generated invoice. No signature required.</small></p>
                </div>
            </body>
            </html>
            """
            
            success, message = email_service.send_email(self.to_email, subject, body, pdf_path)
            
            try:
                os.remove(pdf_path)
            except:
                pass
            
            self.finished.emit(success, message)
            
        except Exception as e:
            self.finished.emit(False, str(e))


class ModernInvoiceViewer(QDialog):
    def __init__(self, invoice_data, auth_service, parent=None):
        super().__init__(parent)
        self.invoice = invoice_data
        self.auth_service = auth_service
        self.settings_controller = SettingsController()
        self.invoice_model = Invoice()
        self.email_worker = None
        
        # Set window flags for minimize and maximize buttons
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                           Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
        self.apply_styles()
        self.setWindowTitle(f"Invoice {invoice_data['invoice_number']}")
        self.setModal(True)
        self.resize(1200, 900)
        
        # Enable window to be resizable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def apply_styles(self):
        """Apply professional CSS styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
            }
            QLabel[bHeading="true"] {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton[btnDanger="true"] {
                background-color: #e74c3c;
            }
            QPushButton[btnDanger="true"]:hover {
                background-color: #c0392b;
            }
            QPushButton[btnSuccess="true"] {
                background-color: #27ae60;
            }
            QPushButton[btnSuccess="true"]:hover {
                background-color: #229954;
            }
            QPushButton[btnSecondary="true"] {
                background-color: #95a5a6;
            }
            QPushButton[btnSecondary="true"]:hover {
                background-color: #7f8c8d;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QComboBox {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QDoubleSpinBox, QLineEdit {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QDoubleSpinBox:focus, QLineEdit:focus {
                border-color: #3498db;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QProgressBar {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        settings = self.settings_controller.get_settings()
        currency = settings.get('currency_symbol', '₹')
        business_name = settings.get('business_name', 'Business Name')
        
        # Header Section
        header_widget = self.create_header_section(settings, business_name)
        content_layout.addWidget(header_widget)
        
        # Invoice Info Bar
        info_bar = self.create_info_bar()
        content_layout.addWidget(info_bar)
        
        # Splitter for main content (Customer + Items)
        main_splitter = QSplitter(Qt.Vertical)
        
        # Customer Section
        customer_widget = self.create_customer_section()
        main_splitter.addWidget(customer_widget)
        
        # Items Table Section
        items_widget = self.create_items_section(currency)
        main_splitter.addWidget(items_widget)
        
        main_splitter.setSizes([200, 400])
        content_layout.addWidget(main_splitter)
        
        # Bottom Sections (Tax, Payment, Bank, etc.)
        bottom_widget = self.create_bottom_sections(currency, settings)
        content_layout.addWidget(bottom_widget)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(30)
        content_layout.addWidget(self.progress_bar)
        
        # Button Section
        button_widget = self.create_button_section()
        content_layout.addWidget(button_widget)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_header_section(self, settings, business_name):
        """Create professional header section"""
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Left side - Logo/Business Info
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Logo if exists
        logo_data = settings.get('company_logo', '')
        if logo_data:
            try:
                from PyQt5.QtGui import QPixmap
                import base64
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(logo_data))
                logo_label = QLabel()
                logo_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                left_layout.addWidget(logo_label, alignment=Qt.AlignLeft)
            except:
                pass
        
        business_label = QLabel(f"<h1 style='color: white; margin: 0;'>{business_name}</h1>")
        business_label.setTextFormat(Qt.RichText)
        left_layout.addWidget(business_label)
        
        business_details = QLabel(f"{settings.get('business_address', '')}<br>"
                                 f"📞 {settings.get('business_phone', '')} | ✉️ {settings.get('business_email', '')}<br>"
                                 f"GST: {settings.get('business_gst', '')}")
        business_details.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        business_details.setWordWrap(True)
        left_layout.addWidget(business_details)
        
        # Right side - Invoice Title
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignRight)
        
        invoice_title = QLabel("TAX INVOICE")
        invoice_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f39c12;")
        right_layout.addWidget(invoice_title)
        
        invoice_number = QLabel(f"#{self.invoice['invoice_number']}")
        invoice_number.setStyleSheet("font-size: 16px; color: white;")
        right_layout.addWidget(invoice_number)
        
        header_layout.addWidget(left_widget)
        header_layout.addStretch()
        header_layout.addWidget(right_widget)
        
        return header_widget
    
    def create_info_bar(self):
        """Create info bar with invoice details"""
        info_widget = QFrame()
        info_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        info_layout = QGridLayout(info_widget)
        info_layout.setSpacing(15)
        
        # Invoice Date
        date_frame = QFrame()
        date_layout = QVBoxLayout(date_frame)
        date_layout.setContentsMargins(10, 5, 10, 5)
        date_layout.addWidget(QLabel("📅 INVOICE DATE"))
        date_layout.addWidget(QLabel(f"<b>{self.invoice['invoice_date'][:10]}</b>"))
        info_layout.addWidget(date_frame, 0, 0)
        
        # Due Date
        due_date_frame = QFrame()
        due_date_layout = QVBoxLayout(due_date_frame)
        due_date_layout.setContentsMargins(10, 5, 10, 5)
        due_date_layout.addWidget(QLabel("⏰ DUE DATE"))
        due_date_text = self.invoice.get('due_date', 'N/A')[:10] if self.invoice.get('due_date') else 'N/A'
        due_date_layout.addWidget(QLabel(f"<b>{due_date_text}</b>"))
        info_layout.addWidget(due_date_frame, 0, 1)
        
        # Status
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)
        status_layout.addWidget(QLabel("📊 STATUS:"))
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pending", "paid", "overdue", "cancelled"])
        current_status = self.invoice.get('status', 'pending')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        self.status_combo.currentTextChanged.connect(self.update_status)
        
        # Style status based on value
        status_colors = {
            'pending': '#f39c12',
            'paid': '#27ae60',
            'overdue': '#e74c3c',
            'cancelled': '#95a5a6'
        }
        self.status_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {status_colors.get(current_status, '#3498db')};
                color: white;
                font-weight: bold;
            }}
        """)
        
        status_layout.addWidget(self.status_combo)
        info_layout.addWidget(status_frame, 0, 2)
        
        info_layout.setColumnStretch(0, 1)
        info_layout.setColumnStretch(1, 1)
        info_layout.setColumnStretch(2, 1)
        
        return info_widget
    
    def create_customer_section(self):
        """Create customer information section"""
        customer_group = QGroupBox("👤 CUSTOMER INFORMATION")
        customer_layout = QGridLayout(customer_group)
        customer_layout.setSpacing(10)
        
        customer_layout.addWidget(QLabel("<b>Name:</b>"), 0, 0)
        customer_layout.addWidget(QLabel(self.invoice.get('customer_name', 'N/A')), 0, 1)
        
        customer_layout.addWidget(QLabel("<b>Address:</b>"), 1, 0)
        customer_layout.addWidget(QLabel(self.invoice.get('address', 'N/A')), 1, 1)
        
        customer_layout.addWidget(QLabel("<b>Phone:</b>"), 2, 0)
        customer_layout.addWidget(QLabel(self.invoice.get('phone', 'N/A')), 2, 1)
        
        customer_layout.addWidget(QLabel("<b>GSTIN:</b>"), 3, 0)
        customer_layout.addWidget(QLabel(self.invoice.get('gst_number', 'N/A')), 3, 1)
        
        if self.invoice.get('email'):
            customer_layout.addWidget(QLabel("<b>Email:</b>"), 4, 0)
            customer_layout.addWidget(QLabel(self.invoice.get('email', 'N/A')), 4, 1)
        
        customer_layout.setColumnStretch(1, 3)
        
        return customer_group
    
    def create_items_section(self, currency):
        """Create items table section"""
        items_group = QGroupBox("📦 INVOICE ITEMS")
        items_layout = QVBoxLayout(items_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["S.No", "Description", "HSN/SAC", "Quantity", "Unit Price", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        self.table.setRowCount(len(self.invoice['items']))
        for row, item in enumerate(self.invoice['items'], 1):
            self.table.setItem(row-1, 0, QTableWidgetItem(str(row)))
            self.table.setItem(row-1, 1, QTableWidgetItem(item['product_name']))
            self.table.setItem(row-1, 2, QTableWidgetItem(item.get('hsn_code', '')))
            quantity = item['quantity']
            quantity_str = str(int(quantity)) if quantity.is_integer() else f"{quantity:.2f}"
            self.table.setItem(row-1, 3, QTableWidgetItem(quantity_str))
            self.table.setItem(row-1, 4, QTableWidgetItem(f"{currency}{item['unit_price']:.2f}"))
            amount = item['total']
            self.table.setItem(row-1, 5, QTableWidgetItem(f"{currency}{amount:.2f}"))
        
        items_layout.addWidget(self.table)
        
        return items_group
    
    def create_bottom_sections(self, currency, settings):
        """Create bottom sections (tax, payment, bank details)"""
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(20)
        
        # Left side - Tax and Payment
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Tax Breakdown
        tax_group = QGroupBox("💰 TAX BREAKDOWN")
        tax_layout = QVBoxLayout(tax_group)
        
        cgst_total = sum(item.get('cgst_amount', 0) for item in self.invoice['items'])
        sgst_total = sum(item.get('sgst_amount', 0) for item in self.invoice['items'])
        igst_total = sum(item.get('igst_amount', 0) for item in self.invoice['items'])
        
        if cgst_total > 0:
            tax_layout.addWidget(QLabel(f"CGST: {currency}{cgst_total:.2f}"))
        if sgst_total > 0:
            tax_layout.addWidget(QLabel(f"SGST: {currency}{sgst_total:.2f}"))
        if igst_total > 0:
            tax_layout.addWidget(QLabel(f"IGST: {currency}{igst_total:.2f}"))
        
        left_layout.addWidget(tax_group)
        
        # Payment Section
        paid_amount = self.invoice.get('paid_amount', 0)
        balance_due = self.invoice['grand_total'] - paid_amount
        
        if self.invoice.get('status') != 'paid' and balance_due > 0:
            payment_group = QGroupBox("💳 RECORD PAYMENT")
            payment_layout = QVBoxLayout(payment_group)
            
            amount_layout = QHBoxLayout()
            amount_layout.addWidget(QLabel("Amount:"))
            self.payment_amount = QDoubleSpinBox()
            self.payment_amount.setRange(0.01, balance_due)
            self.payment_amount.setValue(balance_due)
            self.payment_amount.setPrefix(f"{currency} ")
            self.payment_amount.setDecimals(2)
            amount_layout.addWidget(self.payment_amount)
            payment_layout.addLayout(amount_layout)
            
            method_layout = QHBoxLayout()
            method_layout.addWidget(QLabel("Method:"))
            self.payment_method = QComboBox()
            self.payment_method.addItems(["Cash", "Bank Transfer", "Cheque", "Credit Card", "UPI"])
            method_layout.addWidget(self.payment_method)
            payment_layout.addLayout(method_layout)
            
            pay_btn = QPushButton("Add Payment")
            pay_btn.setProperty("btnSuccess", True)
            pay_btn.clicked.connect(self.add_payment)
            payment_layout.addWidget(pay_btn)
            
            left_layout.addWidget(payment_group)
        
        # Right side - Totals and Bank Details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Totals
        totals_group = QGroupBox("📊 INVOICE SUMMARY")
        totals_layout = QVBoxLayout(totals_group)
        
        totals_layout.addWidget(QLabel(f"<b>Subtotal:</b> {currency}{self.invoice['subtotal']:.2f}"))
        totals_layout.addWidget(QLabel(f"<b>Tax Total:</b> {currency}{self.invoice['tax_total']:.2f}"))
        
        if paid_amount > 0:
            totals_layout.addWidget(QLabel(f"<b>Paid Amount:</b> {currency}{paid_amount:.2f}"))
            totals_layout.addWidget(QLabel(f"<b>Balance Due:</b> {currency}{balance_due:.2f}"))
        
        total_label = QLabel(f"<h2>Grand Total: {currency}{self.invoice['grand_total']:.2f}</h2>")
        total_label.setStyleSheet("color: #27ae60;")
        totals_layout.addWidget(total_label)
        
        right_layout.addWidget(totals_group)
        
        # Bank Details
        bank_name = settings.get('bank_name', '')
        if bank_name:
            bank_group = QGroupBox("🏦 BANK DETAILS")
            bank_layout = QVBoxLayout(bank_group)
            
            if settings.get('bank_name'):
                bank_layout.addWidget(QLabel(f"<b>Bank:</b> {settings.get('bank_name')}"))
            if settings.get('bank_account_name'):
                bank_layout.addWidget(QLabel(f"<b>Account Name:</b> {settings.get('bank_account_name')}"))
            if settings.get('bank_account_number'):
                bank_layout.addWidget(QLabel(f"<b>Account Number:</b> {settings.get('bank_account_number')}"))
            if settings.get('bank_ifsc'):
                bank_layout.addWidget(QLabel(f"<b>IFSC Code:</b> {settings.get('bank_ifsc')}"))
            if settings.get('bank_upi_id'):
                bank_layout.addWidget(QLabel(f"<b>UPI ID:</b> {settings.get('bank_upi_id')}"))
            
            right_layout.addWidget(bank_group)
        
        # Notes
        if self.invoice.get('notes'):
            notes_group = QGroupBox("📝 NOTES")
            notes_layout = QVBoxLayout(notes_group)
            notes_layout.addWidget(QLabel(self.invoice['notes']))
            right_layout.addWidget(notes_group)
        
        # Terms
        terms = settings.get('invoice_terms', '')
        if terms:
            terms_group = QGroupBox("📋 TERMS & CONDITIONS")
            terms_layout = QVBoxLayout(terms_group)
            terms_layout.addWidget(QLabel(terms))
            right_layout.addWidget(terms_group)
        
        bottom_layout.addWidget(left_widget, 1)
        bottom_layout.addWidget(right_widget, 1)
        
        return bottom_widget
    
    def create_button_section(self):
        """Create button section with professional styling"""
        button_widget = QFrame()
        button_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(15)
        
        # Send Email Button
        self.email_btn = QPushButton("📧 Send Email to Customer")
        self.email_btn.setMinimumHeight(40)
        self.email_btn.setProperty("btnSuccess", True)
        self.email_btn.clicked.connect(self.send_email_dialog)
        button_layout.addWidget(self.email_btn)
        
        # PDF Export Button
        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.setMinimumHeight(40)
        pdf_btn.setProperty("btnDanger", True)
        pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(pdf_btn)
        
        button_layout.addStretch()
        
        # Close Button
        close_btn = QPushButton("✖ Close")
        close_btn.setMinimumHeight(40)
        close_btn.setProperty("btnSecondary", True)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        return button_widget
    
    def send_email_dialog(self):
        """Show dialog to enter customer email and send invoice"""
        customer_email = self.invoice.get('email', '')
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Send Invoice via Email")
        dialog.setModal(True)
        dialog.setFixedSize(500, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QPushButton {
                padding: 8px 20px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("Send Invoice to Customer")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header_label)
        
        layout.addWidget(QLabel(f"Invoice: <b>{self.invoice['invoice_number']}</b>"))
        layout.addWidget(QLabel(f"Customer: <b>{self.invoice.get('customer_name', 'N/A')}</b>"))
        
        layout.addWidget(QLabel("Email Address:"))
        email_input = QLineEdit()
        email_input.setText(customer_email)
        email_input.setPlaceholderText("customer@example.com")
        layout.addWidget(email_input)
        
        # Status label
        status_label = QLabel()
        status_label.setStyleSheet("color: #27ae60;")
        status_label.setWordWrap(True)
        layout.addWidget(status_label)
        
        button_layout = QHBoxLayout()
        send_btn = QPushButton("Send Email")
        send_btn.setProperty("btnSuccess", True)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("btnSecondary", True)
        
        button_layout.addWidget(send_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def send_email():
            email = email_input.text().strip()
            if not email:
                QMessageBox.warning(dialog, "Error", "Please enter an email address!")
                return
            
            send_btn.setEnabled(False)
            send_btn.setText("Sending...")
            status_label.setText("Sending email...")
            status_label.setStyleSheet("color: #3498db;")
            
            settings = self.settings_controller.get_settings()
            self.email_worker = EmailWorker(email, self.invoice, settings)
            self.email_worker.progress.connect(lambda msg: status_label.setText(msg))
            self.email_worker.finished.connect(lambda success, msg: self.on_email_sent(success, msg, dialog, send_btn))
            self.email_worker.start()
        
        def on_email_sent(success, message, dialog, send_btn):
            if success:
                status_label.setText("✓ Email sent successfully!")
                status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                QMessageBox.information(dialog, "Success", f"Invoice sent to {email_input.text()}!")
                dialog.accept()
            else:
                status_label.setText(f"✗ Failed: {message}")
                status_label.setStyleSheet("color: #e74c3c;")
                send_btn.setEnabled(True)
                send_btn.setText("Send Email")
        
        send_btn.clicked.connect(send_email)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def on_email_sent(self, success, message, dialog, send_btn):
        if success:
            QMessageBox.information(dialog, "Success", "Invoice sent successfully!")
            dialog.accept()
        else:
            QMessageBox.critical(dialog, "Error", f"Failed to send email: {message}")
            send_btn.setEnabled(True)
            send_btn.setText("Send Email")
    
    def update_status(self, status):
        reply = QMessageBox.question(self, "Update Status", 
                                    f"Change invoice status to '{status.upper()}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.invoice_model.update_status(self.invoice['id'], status)
            self.invoice['status'] = status
            
            # Update status combo style
            status_colors = {
                'pending': '#f39c12',
                'paid': '#27ae60',
                'overdue': '#e74c3c',
                'cancelled': '#95a5a6'
            }
            self.status_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {status_colors.get(status, '#3498db')};
                    color: white;
                    font-weight: bold;
                }}
            """)
            
            QMessageBox.information(self, "Success", f"Invoice status updated to {status.upper()}")
    
    def add_payment(self):
        amount = self.payment_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid amount!")
            return
        
        payment_method = self.payment_method.currentText()
        
        reply = QMessageBox.question(self, "Record Payment", 
                                    f"Record payment of {self.payment_amount.prefix()}{amount:.2f} via {payment_method}?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.invoice_model.update_payment_status(self.invoice['id'], amount)
            QMessageBox.information(self, "Success", "Payment recorded successfully!")
            self.accept()
    
    def export_pdf(self):
        from controllers.invoice_controller import InvoiceController
        controller = InvoiceController(None, self.auth_service)
        controller.export_pdf(self.invoice['id'])


# Keep backward compatibility
InvoiceViewer = ModernInvoiceViewer