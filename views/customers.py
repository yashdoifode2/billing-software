from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
from controllers.customer_controller import CustomerController

class CustomersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # Create controller after UI is ready
        self.controller = CustomerController(self)
        # Connect button after controller exists
        self.add_btn.clicked.connect(self.controller.add_customer)
        # Now load the data
        self.controller.load_customers()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title and search
        top_layout = QHBoxLayout()
        title = QLabel("Customer Management")
        title.setObjectName("page_title")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
        self.search_box.textChanged.connect(self.on_search)
        top_layout.addWidget(self.search_box)
        
        layout.addLayout(top_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Customer")
        button_layout.addWidget(self.add_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Customer table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "GST Number", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def populate_table(self, customers):
        self.table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            id_item = QTableWidgetItem(str(customer['id']))
            id_item.setData(Qt.UserRole, customer['id'])
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(customer['name']))
            self.table.setItem(row, 2, QTableWidgetItem(customer.get('phone', '')))
            self.table.setItem(row, 3, QTableWidgetItem(customer.get('email', '')))
            self.table.setItem(row, 4, QTableWidgetItem(customer.get('gst_number', '')))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 30)
            edit_btn.setToolTip("Edit Customer")
            # Use lambda with default argument to capture current customer id
            edit_btn.clicked.connect(lambda checked, cid=customer['id']: self.controller.edit_customer(cid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Customer")
            delete_btn.clicked.connect(lambda checked, cid=customer['id']: self.controller.delete_customer(cid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def on_search(self, text):
        self.controller.search_customers(text)