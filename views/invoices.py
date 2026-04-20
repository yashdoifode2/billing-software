from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from controllers.invoice_controller import InvoiceController

class InvoicesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # Create controller after UI is ready
        self.controller = InvoiceController(self)
        # Connect button after controller exists
        self.create_btn.clicked.connect(self.controller.create_invoice)
        # Now load the data
        self.controller.load_invoices()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title and search
        top_layout = QHBoxLayout()
        title = QLabel("Invoice Management")
        title.setObjectName("page_title")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search invoices...")
        self.search_box.textChanged.connect(self.on_search)
        top_layout.addWidget(self.search_box)
        
        layout.addLayout(top_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_btn = QPushButton("➕ Create Invoice")
        button_layout.addWidget(self.create_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Invoice table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Invoice #", "Customer", "Date", "Total", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def populate_table(self, invoices):
        self.table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            self.table.setItem(row, 0, QTableWidgetItem(str(invoice['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(invoice['invoice_number']))
            self.table.setItem(row, 2, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(invoice['invoice_date'][:10]))
            self.table.setItem(row, 4, QTableWidgetItem(f"${invoice['grand_total']:.2f}"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton("👁️ View")
            view_btn.setFixedSize(60, 30)
            view_btn.setToolTip("View Invoice")
            view_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.view_invoice(iid))
            
            pdf_btn = QPushButton("📄 PDF")
            pdf_btn.setFixedSize(60, 30)
            pdf_btn.setToolTip("Export PDF")
            pdf_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.export_pdf(iid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Invoice")
            delete_btn.clicked.connect(lambda checked, iid=invoice['id']: self.controller.delete_invoice(iid))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def on_search(self, text):
        self.controller.search_invoices(text)