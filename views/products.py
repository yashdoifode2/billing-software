from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
from controllers.product_controller import ProductController

class ProductsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        # Create controller after UI is ready
        self.controller = ProductController(self)
        # Connect button after controller exists
        self.add_btn.clicked.connect(self.controller.add_product)
        # Now load the data
        self.controller.load_products()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title and search
        top_layout = QHBoxLayout()
        title = QLabel("Product Management")
        title.setObjectName("page_title")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search products...")
        self.search_box.textChanged.connect(self.on_search)
        top_layout.addWidget(self.search_box)
        
        layout.addLayout(top_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Product")
        button_layout.addWidget(self.add_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Product table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Price", "Tax Rate (%)", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def populate_table(self, products):
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(product.get('description', '')[:50]))
            self.table.setItem(row, 3, QTableWidgetItem(f"${product['price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(product.get('tax_rate', 0))))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 30)
            edit_btn.setToolTip("Edit Product")
            edit_btn.clicked.connect(lambda checked, pid=product['id']: self.controller.edit_product(pid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Product")
            delete_btn.clicked.connect(lambda checked, pid=product['id']: self.controller.delete_product(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def on_search(self, text):
        self.controller.search_products(text)