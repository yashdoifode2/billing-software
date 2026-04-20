from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
                             QMessageBox, QScrollArea, QFrame, QGridLayout,
                             QProgressBar, QComboBox, QDateEdit, QLineEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.expense_controller import ExpenseController

class ModernButton(QPushButton):
    """Custom styled button for consistent UI"""
    def __init__(self, text, color="#3498db", icon="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.2)};
            }}
        """)
    
    def darken_color(self, color, factor=0.1):
        # Simplified color darkening - you can implement full RGB logic if needed
        if color == "#3498db":
            return "#2980b9"
        elif color == "#e74c3c":
            return "#c0392b"
        elif color == "#27ae60":
            return "#229954"
        elif color == "#f39c12":
            return "#e67e22"
        return color

class StatsCard(QFrame):
    """Card widget for displaying statistics"""
    def __init__(self, title, value, icon="📊", color="#3498db"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value label
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
        """)
        layout.addWidget(value_label)
        
        self.value_label = value_label
    
    def update_value(self, value):
        self.value_label.setText(str(value))

class ExpensesWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = ExpenseController(self, auth_service)
        self.setup_ui()
        self.controller.load_expenses()
        self.setup_styles()
    
    def setup_styles(self):
        """Set global styles for the widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db20;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #3498db;
                font-size: 13px;
                color: #2c3e50;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #bdc3c7;
                border-radius: 5px;
                min-width: 20px;
            }
            QComboBox, QDateEdit, QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus, QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #ecf0f1;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
    
    def setup_ui(self):
        # Main layout with margins for better spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section with title and filter
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("💰 Expense Management")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Quick filter
        filter_label = QLabel("Filter by category:")
        filter_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        header_layout.addWidget(filter_label)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.setMinimumWidth(150)
        self.category_filter.currentTextChanged.connect(self.apply_filter)
        header_layout.addWidget(self.category_filter)
        
        main_layout.addLayout(header_layout)
        
        # Stats Cards Section
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_expenses_card = StatsCard("Total Expenses", "₹0", "💰", "#3498db")
        self.avg_expense_card = StatsCard("Average Expense", "₹0", "📈", "#27ae60")
        self.highest_expense_card = StatsCard("Highest Expense", "₹0", "🔝", "#e74c3c")
        self.total_transactions_card = StatsCard("Total Transactions", "0", "📊", "#f39c12")
        
        stats_layout.addWidget(self.total_expenses_card)
        stats_layout.addWidget(self.avg_expense_card)
        stats_layout.addWidget(self.highest_expense_card)
        stats_layout.addWidget(self.total_transactions_card)
        
        main_layout.addLayout(stats_layout)
        
        # Action Buttons Section
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.add_btn = ModernButton("➕ Add Expense", "#3498db")
        self.add_btn.clicked.connect(self.controller.add_expense)
        action_layout.addWidget(self.add_btn)
        
        self.refresh_btn = ModernButton("🔄 Refresh", "#27ae60")
        self.refresh_btn.clicked.connect(self.refresh)
        action_layout.addWidget(self.refresh_btn)
        
        self.export_btn = ModernButton("📥 Export Data", "#f39c12")
        self.export_btn.clicked.connect(self.export_data)
        action_layout.addWidget(self.export_btn)
        
        action_layout.addStretch()
        
        # Search bar
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 16px;")
        action_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search expenses...")
        self.search_box.setMinimumWidth(200)
        self.search_box.textChanged.connect(self.apply_filter)
        action_layout.addWidget(self.search_box)
        
        main_layout.addLayout(action_layout)
        
        # Table with Scroll Area
        table_container = QFrame()
        table_container.setFrameStyle(QFrame.NoFrame)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Description", "Amount", "Actions"])
        
        # Configure table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 120)  # Date
        self.table.setColumnWidth(2, 150)  # Category
        self.table.setColumnWidth(3, 300)  # Description
        self.table.setColumnWidth(4, 120)  # Amount
        self.table.setColumnWidth(5, 100)  # Actions
        
        # Enable horizontal scrolling if needed
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        scroll_area.setWidget(self.table)
        table_layout.addWidget(scroll_area)
        
        main_layout.addWidget(table_container, stretch=1)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: #7f8c8d;
            padding: 8px;
            font-size: 12px;
            background-color: white;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_label)
    
    def update_statistics(self, expenses):
        """Update statistics cards with current data"""
        if not expenses:
            self.total_expenses_card.update_value("₹0")
            self.avg_expense_card.update_value("₹0")
            self.highest_expense_card.update_value("₹0")
            self.total_transactions_card.update_value("0")
            return
        
        total = sum(e['amount'] for e in expenses)
        avg = total / len(expenses)
        highest = max(e['amount'] for e in expenses)
        
        self.total_expenses_card.update_value(f"₹{total:,.2f}")
        self.avg_expense_card.update_value(f"₹{avg:,.2f}")
        self.highest_expense_card.update_value(f"₹{highest:,.2f}")
        self.total_transactions_card.update_value(str(len(expenses)))
    
    def populate_table(self, expenses):
        """Populate table with expense data and apply filters"""
        # Update category filter dropdown
        categories = set(exp['category'] for exp in expenses)
        current_filter = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(sorted(categories))
        if current_filter in categories:
            self.category_filter.setCurrentText(current_filter)
        
        # Apply filters
        filtered_expenses = self.filter_expenses(expenses)
        
        # Update statistics with filtered data
        self.update_statistics(filtered_expenses)
        
        # Populate table
        self.table.setRowCount(len(filtered_expenses))
        self.table.setSortingEnabled(False)  # Disable sorting during population
        
        for row, expense in enumerate(filtered_expenses):
            # ID
            id_item = QTableWidgetItem(str(expense['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Date
            date_item = QTableWidgetItem(expense['expense_date'][:10])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, date_item)
            
            # Category with colored background
            category_item = QTableWidgetItem(expense['category'])
            category_colors = {
                'Food': '#27ae60', 'Transport': '#3498db', 'Shopping': '#e74c3c',
                'Entertainment': '#f39c12', 'Bills': '#9b59b6', 'Healthcare': '#1abc9c'
            }
            color = category_colors.get(expense['category'], '#7f8c8d')
            category_item.setForeground(QColor(color))
            category_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 2, category_item)
            
            # Description
            desc = expense.get('description', '')[:50]
            self.table.setItem(row, 3, QTableWidgetItem(desc))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{expense['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if expense['amount'] > 1000:
                amount_item.setForeground(QColor("#e74c3c"))
            elif expense['amount'] > 500:
                amount_item.setForeground(QColor("#f39c12"))
            else:
                amount_item.setForeground(QColor("#27ae60"))
            self.table.setItem(row, 4, amount_item)
            
            # Action buttons
            actions_widget = self.create_action_buttons(expense['id'])
            self.table.setCellWidget(row, 5, actions_widget)
        
        self.table.setSortingEnabled(True)
        self.update_status(f"Showing {len(filtered_expenses)} of {len(expenses)} expenses")
    
    def create_action_buttons(self, expense_id):
        """Create action buttons for table row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setToolTip("Edit Expense")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(lambda checked, eid=expense_id: self.controller.edit_expense(eid))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Delete Expense")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda checked, eid=expense_id: self.controller.delete_expense(eid))
        
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        
        return widget
    
    def filter_expenses(self, expenses):
        """Apply category and search filters to expenses"""
        filtered = expenses.copy()
        
        # Apply category filter
        category = self.category_filter.currentText()
        if category != "All Categories":
            filtered = [e for e in filtered if e['category'] == category]
        
        # Apply search filter
        search_text = self.search_box.text().lower()
        if search_text:
            filtered = [e for e in filtered if 
                       search_text in e.get('description', '').lower() or
                       search_text in e['category'].lower() or
                       search_text in str(e['amount'])]
        
        return filtered
    
    def apply_filter(self):
        """Apply current filters to the table"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'expenses'):
            self.populate_table(self.controller.expenses)
    
    def export_data(self):
        """Export expense data to CSV"""
        from PyQt5.QtWidgets import QFileDialog
        import csv
        
        if not hasattr(self.controller, 'expenses') or not self.controller.expenses:
            QMessageBox.warning(self, "No Data", "No expenses to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Expenses", "", "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['id', 'expense_date', 'category', 'description', 'amount']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for expense in self.controller.expenses:
                        writer.writerow({
                            'id': expense['id'],
                            'expense_date': expense['expense_date'],
                            'category': expense['category'],
                            'description': expense.get('description', ''),
                            'amount': expense['amount']
                        })
                QMessageBox.information(self, "Success", f"Exported {len(self.controller.expenses)} expenses to {file_path}")
                self.update_status(f"Exported {len(self.controller.expenses)} expenses")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)
    
    def refresh(self):
        """Refresh the expense list"""
        self.update_status("Refreshing expenses...")
        self.controller.load_expenses()
        self.update_status("Expenses refreshed successfully")