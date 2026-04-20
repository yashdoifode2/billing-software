from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.expense_controller import ExpenseController

class ExpensesWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = ExpenseController(self, auth_service)
        self.setup_ui()
        self.controller.load_expenses()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Expense Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Expense")
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
        self.add_btn.clicked.connect(self.controller.add_expense)
        button_layout.addWidget(self.add_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Expense table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Description", "Amount"])
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
    
    def populate_table(self, expenses):
        self.table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(str(expense['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(expense['expense_date'][:10]))
            self.table.setItem(row, 2, QTableWidgetItem(expense['category']))
            self.table.setItem(row, 3, QTableWidgetItem(expense.get('description', '')[:50]))
            self.table.setItem(row, 4, QTableWidgetItem(f"₹{expense['amount']:.2f}"))
        
        self.table.resizeColumnsToContents()
    
    def refresh(self):
        self.controller.load_expenses()