from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDateEdit, QGroupBox, QFormLayout, QComboBox,
                             QFileDialog, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QDate
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.invoice import Invoice
from models.expense import Expense

class ReportsWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.invoice_model = Invoice()
        self.expense_model = Expense()
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Financial Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Date range
        date_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout(date_group)
        
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        self.refresh_btn = QPushButton("Refresh Reports")
        self.refresh_btn.clicked.connect(self.load_reports)
        date_layout.addWidget(self.refresh_btn)
        
        date_layout.addStretch()
        layout.addWidget(date_group)
        
        # Tab widget for different reports
        self.tab_widget = QTabWidget()
        
        # Revenue Report Tab
        self.revenue_tab = self.create_revenue_tab()
        self.tab_widget.addTab(self.revenue_tab, "Revenue Report")
        
        # Expense Report Tab
        self.expense_tab = self.create_expense_tab()
        self.tab_widget.addTab(self.expense_tab, "Expense Report")
        
        # Profit/Loss Tab
        self.profit_tab = self.create_profit_tab()
        self.tab_widget.addTab(self.profit_tab, "Profit & Loss")
        
        # Outstanding Tab
        self.outstanding_tab = self.create_outstanding_tab()
        self.tab_widget.addTab(self.outstanding_tab, "Outstanding Invoices")
        
        layout.addWidget(self.tab_widget)
    
    def create_revenue_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.revenue_table = QTableWidget()
        self.revenue_table.setColumnCount(3)
        self.revenue_table.setHorizontalHeaderLabels(["Date", "Invoice Count", "Revenue"])
        self.revenue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.revenue_table)
        
        self.revenue_total = QLabel()
        self.revenue_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 10px;")
        layout.addWidget(self.revenue_total)
        
        return widget
    
    def create_expense_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)
        self.expense_table.setHorizontalHeaderLabels(["Category", "Count", "Total Amount", "Percentage"])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.expense_table)
        
        self.expense_total = QLabel()
        self.expense_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c; margin-top: 10px;")
        layout.addWidget(self.expense_total)
        
        return widget
    
    def create_profit_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.profit_table = QTableWidget()
        self.profit_table.setColumnCount(2)
        self.profit_table.setHorizontalHeaderLabels(["Particulars", "Amount"])
        self.profit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.profit_table)
        
        self.profit_label = QLabel()
        self.profit_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.profit_label)
        
        return widget
    
    def create_outstanding_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.outstanding_table = QTableWidget()
        self.outstanding_table.setColumnCount(5)
        self.outstanding_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Due Date", "Amount Due"])
        self.outstanding_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.outstanding_table)
        
        self.outstanding_total = QLabel()
        self.outstanding_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c; margin-top: 10px;")
        layout.addWidget(self.outstanding_total)
        
        return widget
    
    def load_reports(self):
        self.load_revenue_report()
        self.load_expense_report()
        self.load_profit_loss()
        self.load_outstanding()
    
    def load_revenue_report(self):
        # Get paid invoices
        invoices = self.invoice_model.get_all()
        paid_invoices = [inv for inv in invoices if inv.get('status') == 'paid']
        
        # Group by date
        revenue_data = {}
        for inv in paid_invoices:
            date = inv['invoice_date'][:10]
            if date not in revenue_data:
                revenue_data[date] = {'count': 0, 'total': 0}
            revenue_data[date]['count'] += 1
            revenue_data[date]['total'] += inv['grand_total']
        
        # Display
        self.revenue_table.setRowCount(len(revenue_data))
        total_revenue = 0
        for row, (date, data) in enumerate(sorted(revenue_data.items(), reverse=True)):
            self.revenue_table.setItem(row, 0, QTableWidgetItem(date))
            self.revenue_table.setItem(row, 1, QTableWidgetItem(str(data['count'])))
            self.revenue_table.setItem(row, 2, QTableWidgetItem(f"₹{data['total']:.2f}"))
            total_revenue += data['total']
        
        self.revenue_total.setText(f"Total Revenue: ₹{total_revenue:,.2f}")
    
    def load_expense_report(self):
        expenses = self.expense_model.get_all()
        
        # Group by category
        expense_data = {}
        total_expenses = 0
        for exp in expenses:
            category = exp['category']
            if category not in expense_data:
                expense_data[category] = {'count': 0, 'total': 0}
            expense_data[category]['count'] += 1
            expense_data[category]['total'] += exp['amount']
            total_expenses += exp['amount']
        
        # Display
        self.expense_table.setRowCount(len(expense_data))
        for row, (category, data) in enumerate(expense_data.items()):
            percentage = (data['total'] / total_expenses * 100) if total_expenses > 0 else 0
            self.expense_table.setItem(row, 0, QTableWidgetItem(category))
            self.expense_table.setItem(row, 1, QTableWidgetItem(str(data['count'])))
            self.expense_table.setItem(row, 2, QTableWidgetItem(f"₹{data['total']:.2f}"))
            self.expense_table.setItem(row, 3, QTableWidgetItem(f"{percentage:.1f}%"))
        
        self.expense_total.setText(f"Total Expenses: ₹{total_expenses:,.2f}")
    
    def load_profit_loss(self):
        # Get revenue
        invoices = self.invoice_model.get_all()
        paid_invoices = [inv for inv in invoices if inv.get('status') == 'paid']
        total_revenue = sum(inv['grand_total'] for inv in paid_invoices)
        
        # Get expenses
        expenses = self.expense_model.get_all()
        total_expenses = sum(exp['amount'] for exp in expenses)
        
        net_profit = total_revenue - total_expenses
        
        # Display
        data = [
            ("Total Revenue", f"₹{total_revenue:,.2f}"),
            ("Total Expenses", f"₹{total_expenses:,.2f}"),
            ("Net Profit/Loss", f"₹{net_profit:,.2f}")
        ]
        
        self.profit_table.setRowCount(len(data))
        for row, (label, amount) in enumerate(data):
            self.profit_table.setItem(row, 0, QTableWidgetItem(label))
            self.profit_table.setItem(row, 1, QTableWidgetItem(amount))
        
        profit_color = "#27ae60" if net_profit >= 0 else "#e74c3c"
        profit_text = "Profit" if net_profit >= 0 else "Loss"
        self.profit_label.setText(f"Net {profit_text}: ₹{abs(net_profit):,.2f}")
        self.profit_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {profit_color};")
    
    def load_outstanding(self):
        invoices = self.invoice_model.get_all()
        outstanding = [inv for inv in invoices if inv.get('status') != 'paid']
        
        self.outstanding_table.setRowCount(len(outstanding))
        total_due = 0
        for row, inv in enumerate(outstanding):
            due_amount = inv['grand_total'] - inv.get('paid_amount', 0)
            self.outstanding_table.setItem(row, 0, QTableWidgetItem(inv['invoice_number']))
            self.outstanding_table.setItem(row, 1, QTableWidgetItem(inv.get('customer_name', 'N/A')))
            self.outstanding_table.setItem(row, 2, QTableWidgetItem(inv['invoice_date'][:10]))
            self.outstanding_table.setItem(row, 3, QTableWidgetItem(inv.get('due_date', 'N/A')[:10] if inv.get('due_date') else 'N/A'))
            self.outstanding_table.setItem(row, 4, QTableWidgetItem(f"₹{due_amount:.2f}"))
            total_due += due_amount
        
        self.outstanding_total.setText(f"Total Outstanding: ₹{total_due:,.2f}")
    
    def refresh(self):
        self.load_reports()