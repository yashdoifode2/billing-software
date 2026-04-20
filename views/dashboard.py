from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QGridLayout,
                             QDateEdit, QPushButton, QComboBox, QGroupBox,
                             QSplitter, QHeaderView)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.report_service import ReportService
from models.invoice import Invoice
from models.expense import Expense

class DashboardWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.report_service = ReportService()
        self.invoice_model = Invoice()
        self.expense_model = Expense()
        self.stats_cards = {}
        self.setup_ui()
        self.set_default_dates()
        self.refresh()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Date Filter Section
        filter_group = QGroupBox("Date Range Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        # From Date
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.from_date)
        
        # To Date
        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)
        
        # Quick filters
        filter_layout.addWidget(QLabel("Quick Filter:"))
        self.quick_filter = QComboBox()
        self.quick_filter.addItems(["Current Month", "Previous Month", "Last 30 Days", 
                                    "Last 90 Days", "This Year", "Last Year", "Custom"])
        self.quick_filter.currentTextChanged.connect(self.on_quick_filter)
        filter_layout.addWidget(self.quick_filter)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Filter")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.apply_btn.clicked.connect(self.refresh)
        filter_layout.addWidget(self.apply_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.reset_btn.clicked.connect(self.set_default_dates)
        filter_layout.addWidget(self.reset_btn)
        
        layout.addWidget(filter_group)
        
        # Stats cards grid - 2 rows of 3 cards each
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(20)
        
        stats_config = [
            ("Total Revenue", "revenue", "#2ecc71", "₹0"),
            ("Total Invoices", "invoices", "#3498db", "0"),
            ("Total Expenses", "expenses", "#e74c3c", "₹0"),
            ("Net Profit", "profit", "#27ae60", "₹0"),
            ("Pending Amount", "pending", "#f39c12", "₹0"),
            ("Avg. Invoice Value", "avg_invoice", "#9b59b6", "₹0"),
        ]
        
        for i, (title_text, key, color, default) in enumerate(stats_config):
            card, value_label = self.create_stat_card(title_text, default, color)
            self.stats_grid.addWidget(card, i // 3, i % 3)
            self.stats_cards[key] = value_label
        
        layout.addLayout(self.stats_grid)
        
        # Period label
        self.period_label = QLabel()
        self.period_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 5px;")
        self.period_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.period_label)
        
        # Create splitter for Recent Invoices and Top Products
        splitter = QSplitter(Qt.Vertical)
        
        # Recent Invoices Section (Expanded)
        recent_widget = QWidget()
        recent_layout = QVBoxLayout(recent_widget)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        
        recent_label = QLabel("Recent Invoices")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        recent_layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(6)
        self.recent_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Due Date", "Status", "Total"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        self.recent_table.setMinimumHeight(300)
        recent_layout.addWidget(self.recent_table)
        
        splitter.addWidget(recent_widget)
        
        # Top Products Section
        products_widget = QWidget()
        products_layout = QVBoxLayout(products_widget)
        products_layout.setContentsMargins(0, 0, 0, 0)
        
        top_products_label = QLabel("Top Selling Products/Services")
        top_products_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        products_layout.addWidget(top_products_label)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels(["Product Name", "HSN Code", "Quantity Sold", "Revenue"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_products_table.setAlternatingRowColors(True)
        self.top_products_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        self.top_products_table.setMinimumHeight(250)
        products_layout.addWidget(self.top_products_table)
        
        splitter.addWidget(products_widget)
        
        # Set splitter proportions (60% recent invoices, 40% top products)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
    
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                border-left: 5px solid {color};
            }}
        """)
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card, value_label
    
    def set_default_dates(self):
        """Set default date range to current month"""
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        
        self.from_date.setDate(first_day)
        self.to_date.setDate(today)
        self.quick_filter.setCurrentText("Current Month")
        self.refresh()
    
    def on_quick_filter(self, filter_text):
        """Handle quick filter selection"""
        today = QDate.currentDate()
        
        if filter_text == "Current Month":
            first_day = QDate(today.year(), today.month(), 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
            self.refresh()
        
        elif filter_text == "Previous Month":
            if today.month() == 1:
                first_day = QDate(today.year() - 1, 12, 1)
                last_day = QDate(today.year() - 1, 12, 31)
            else:
                first_day = QDate(today.year(), today.month() - 1, 1)
                last_day = QDate(today.year(), today.month(), 1).addDays(-1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(last_day)
            self.refresh()
        
        elif filter_text == "Last 30 Days":
            self.from_date.setDate(today.addDays(-30))
            self.to_date.setDate(today)
            self.refresh()
        
        elif filter_text == "Last 90 Days":
            self.from_date.setDate(today.addDays(-90))
            self.to_date.setDate(today)
            self.refresh()
        
        elif filter_text == "This Year":
            first_day = QDate(today.year(), 1, 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
            self.refresh()
        
        elif filter_text == "Last Year":
            first_day = QDate(today.year() - 1, 1, 1)
            last_day = QDate(today.year() - 1, 12, 31)
            self.from_date.setDate(first_day)
            self.to_date.setDate(last_day)
            self.refresh()
    
    def refresh(self):
        try:
            # Get date range
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Update period label
            period_text = f"Showing data from: {from_date} to {to_date}"
            self.period_label.setText(period_text)
            
            # Get filtered data
            stats = self.get_filtered_stats(from_date, to_date)
            
            # Update stat cards
            self.stats_cards['revenue'].setText(f"₹{stats.get('total_revenue', 0):,.2f}")
            self.stats_cards['invoices'].setText(str(stats.get('total_invoices', 0)))
            self.stats_cards['expenses'].setText(f"₹{stats.get('total_expenses', 0):,.2f}")
            
            # Set profit color (red if negative)
            profit = stats.get('net_profit', 0)
            profit_color = "#27ae60" if profit >= 0 else "#e74c3c"
            self.stats_cards['profit'].setStyleSheet(f"color: {profit_color}; font-size: 28px; font-weight: bold;")
            self.stats_cards['profit'].setText(f"₹{profit:,.2f}")
            
            self.stats_cards['pending'].setText(f"₹{stats.get('pending_amount', 0):,.2f}")
            self.stats_cards['avg_invoice'].setText(f"₹{stats.get('avg_invoice_value', 0):,.2f}")
            
            # Update recent invoices
            recent_invoices = self.get_recent_invoices(from_date, to_date)
            self.recent_table.setRowCount(len(recent_invoices))
            for row, invoice in enumerate(recent_invoices):
                self.recent_table.setItem(row, 0, QTableWidgetItem(invoice.get('invoice_number', 'N/A')))
                self.recent_table.setItem(row, 1, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
                self.recent_table.setItem(row, 2, QTableWidgetItem(invoice.get('invoice_date', 'N/A')[:10]))
                self.recent_table.setItem(row, 3, QTableWidgetItem(invoice.get('due_date', 'N/A')[:10] if invoice.get('due_date') else 'N/A'))
                
                # Status with color
                status = invoice.get('status', 'pending')
                status_item = QTableWidgetItem(status.upper())
                if status == 'paid':
                    status_item.setForeground(Qt.green)
                    status_item.setBackground(Qt.transparent)
                elif status == 'pending':
                    status_item.setForeground(Qt.blue)
                elif status == 'overdue':
                    status_item.setForeground(Qt.red)
                else:
                    status_item.setForeground(Qt.gray)
                self.recent_table.setItem(row, 4, status_item)
                
                self.recent_table.setItem(row, 5, QTableWidgetItem(f"₹{invoice.get('grand_total', 0):,.2f}"))
            
            # Update top products
            top_products = self.get_top_products(from_date, to_date)
            self.top_products_table.setRowCount(len(top_products))
            for row, product in enumerate(top_products):
                self.top_products_table.setItem(row, 0, QTableWidgetItem(product.get('product_name', 'N/A')))
                self.top_products_table.setItem(row, 1, QTableWidgetItem(product.get('hsn_code', 'N/A')))
                quantity = product.get('total_quantity', 0)
                quantity_str = str(int(quantity)) if quantity.is_integer() else f"{quantity:.2f}"
                self.top_products_table.setItem(row, 2, QTableWidgetItem(quantity_str))
                self.top_products_table.setItem(row, 3, QTableWidgetItem(f"₹{product.get('total_revenue', 0):,.2f}"))
            
            # Resize tables to contents
            self.recent_table.resizeColumnsToContents()
            self.top_products_table.resizeColumnsToContents()
            
            print(f"Dashboard refreshed for period: {from_date} to {to_date}")
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
            import traceback
            traceback.print_exc()
    
    def get_filtered_stats(self, from_date, to_date):
        """Get filtered statistics for date range"""
        try:
            # Get invoices in date range
            query = """
                SELECT * FROM invoices 
                WHERE invoice_date BETWEEN ? AND ?
            """
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            invoices = db.fetch_all(query, (from_date, to_date))
            
            # Calculate totals
            total_revenue = sum(inv.get('grand_total', 0) for inv in invoices if inv.get('status') == 'paid')
            total_invoices = len(invoices)
            pending_amount = sum(inv.get('grand_total', 0) - inv.get('paid_amount', 0) for inv in invoices if inv.get('status') != 'paid')
            avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
            
            # Get expenses in date range
            expense_query = "SELECT SUM(amount) as total FROM expenses WHERE expense_date BETWEEN ? AND ?"
            expenses = db.fetch_one(expense_query, (from_date, to_date))
            total_expenses = expenses['total'] if expenses and expenses['total'] else 0
            
            net_profit = total_revenue - total_expenses
            
            return {
                'total_revenue': total_revenue,
                'total_invoices': total_invoices,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
                'pending_amount': pending_amount,
                'avg_invoice_value': avg_invoice_value
            }
        except Exception as e:
            print(f"Error getting filtered stats: {e}")
            return {
                'total_revenue': 0,
                'total_invoices': 0,
                'total_expenses': 0,
                'net_profit': 0,
                'pending_amount': 0,
                'avg_invoice_value': 0
            }
    
    def get_recent_invoices(self, from_date, to_date, limit=50):
        """Get recent invoices for date range"""
        query = """
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.invoice_date BETWEEN ? AND ?
            ORDER BY i.invoice_date DESC
            LIMIT ?
        """
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        return db.fetch_all(query, (from_date, to_date, limit))
    
    def get_top_products(self, from_date, to_date, limit=10):
        """Get top selling products for date range"""
        query = """
            SELECT p.name as product_name, 
                   p.hsn_code,
                   SUM(ii.quantity) as total_quantity,
                   SUM(ii.total) as total_revenue
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.invoice_date BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        return db.fetch_all(query, (from_date, to_date, limit))