from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.product_controller import ProductController

class ProductsWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = ProductController(self, auth_service)
        self.setup_ui()
        self.controller.load_products()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title and search
        top_layout = QHBoxLayout()
        title = QLabel("Product Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search products...")
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
        self.add_btn = QPushButton("➕ Add Product")
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.add_btn.clicked.connect(self.controller.add_product)
        button_layout.addWidget(self.add_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Product table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Tax Rate", "Actions"])
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
    
    def populate_table(self, products):
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"₹{product['price']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product.get('tax_rate_cgst', 0) + product.get('tax_rate_sgst', 0)}%"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 30)
            edit_btn.setToolTip("Edit Product")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, pid=product['id']: self.controller.edit_product(pid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Product")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, pid=product['id']: self.controller.delete_product(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 4, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def on_search(self, text):
        self.controller.search_products(text)
    
    def refresh(self):
        self.controller.load_products()