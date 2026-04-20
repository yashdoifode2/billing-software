from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
                             QMessageBox)
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Description", "Amount", "Actions"])
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
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 30)
            edit_btn.setToolTip("Edit Expense")
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
            edit_btn.clicked.connect(lambda checked, eid=expense['id']: self.controller.edit_expense(eid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 30)
            delete_btn.setToolTip("Delete Expense")
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
            delete_btn.clicked.connect(lambda checked, eid=expense['id']: self.controller.delete_expense(eid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.resizeColumnsToContents()
    
    def refresh(self):
        self.controller.load_expenses()