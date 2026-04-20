from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.invoice_controller import InvoiceController

class InvoicesWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = InvoiceController(self, auth_service)
        self.setup_ui()
        self.controller.load_invoices()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title and search
        top_layout = QHBoxLayout()
        title = QLabel("Invoice Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search invoices...")
        self.search_box.setMinimumHeight(35)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.search_box.textChanged.connect(self.on_search)
        top_layout.addWidget(self.search_box)
        
        layout.addLayout(top_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_btn = QPushButton("➕ Create Invoice")
        self.create_btn.setMinimumHeight(40)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.create_btn.clicked.connect(self.controller.create_invoice)
        button_layout.addWidget(self.create_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Invoice table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Invoice #", "Customer", "Date", "Status", "Total", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
    
    def populate_table(self, invoices):
        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            self.table.setItem(row, 0, QTableWidgetItem(str(invoice['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(invoice['invoice_number']))
            self.table.setItem(row, 2, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(invoice['invoice_date'][:10]))
            
            # Status with color
            status = invoice.get('status', 'pending')
            status_item = QTableWidgetItem(status.upper())
            if status == 'paid':
                status_item.setForeground(Qt.green)
            elif status == 'pending':
                status_item.setForeground(Qt.blue)
            elif status == 'overdue':
                status_item.setForeground(Qt.red)
            else:
                status_item.setForeground(Qt.gray)
            self.table.setItem(row, 4, status_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(f"₹{invoice['grand_total']:.2f}"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton("👁️ View")
            view_btn.setFixedSize(65, 30)
            view_btn.setToolTip("View Invoice")
            view_btn.setStyleSheet("background-color: #3498db; color: white; border: none; border-radius: 3px;")
            view_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.view_invoice(iid))
            
            pdf_btn = QPushButton("📄 PDF")
            pdf_btn.setFixedSize(55, 30)
            pdf_btn.setToolTip("Export PDF")
            pdf_btn.setStyleSheet("background-color: #27ae60; color: white; border: none; border-radius: 3px;")
            pdf_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.export_pdf(iid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Invoice")
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.delete_invoice(iid))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 6, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def on_search(self, text):
        self.controller.search_invoices(text)
    
    def refresh(self):
        self.controller.load_invoices()