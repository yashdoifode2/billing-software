from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.report_service import ReportService

class DashboardWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.report_service = ReportService()
        self.stats_cards = {}
        self.setup_ui()
        self.refresh()
        
        # Auto-refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Stats cards grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        stats_config = [
            ("Total Customers", "customers", "#3498db"),
            ("Total Products", "products", "#27ae60"),
            ("Total Invoices", "invoices", "#f39c12"),
            ("Total Revenue", "revenue", "#2ecc71"),
            ("Pending Amount", "pending", "#e74c3c"),
            ("Total Expenses", "expenses", "#9b59b6"),
        ]
        
        for i, (title_text, key, color) in enumerate(stats_config):
            card, value_label = self.create_stat_card(title_text, "0", color)
            stats_grid.addWidget(card, i // 2, i % 2)
            self.stats_cards[key] = value_label
        
        layout.addLayout(stats_grid)
        
        # Recent Invoices Section
        recent_label = QLabel("Recent Invoices")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
        layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Total"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.recent_table)
    
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
        value_label.setObjectName(f"value_{title.lower().replace(' ', '_')}")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card, value_label
    
    def refresh(self):
        try:
            stats = self.report_service.get_dashboard_stats()
            
            # Update stat cards using the stored value labels
            if 'customers' in self.stats_cards:
                self.stats_cards['customers'].setText(str(stats.get('total_customers', 0)))
            if 'products' in self.stats_cards:
                self.stats_cards['products'].setText(str(stats.get('total_products', 0)))
            if 'invoices' in self.stats_cards:
                self.stats_cards['invoices'].setText(str(stats.get('total_invoices', 0)))
            if 'revenue' in self.stats_cards:
                self.stats_cards['revenue'].setText(f"₹{stats.get('total_revenue', 0):,.2f}")
            if 'pending' in self.stats_cards:
                self.stats_cards['pending'].setText(f"₹{stats.get('pending_amount', 0):,.2f}")
            if 'expenses' in self.stats_cards:
                self.stats_cards['expenses'].setText(f"₹{stats.get('total_expenses', 0):,.2f}")
            
            # Update recent invoices table
            recent = stats.get('recent_invoices', [])
            self.recent_table.setRowCount(len(recent))
            for row, invoice in enumerate(recent):
                self.recent_table.setItem(row, 0, QTableWidgetItem(invoice.get('invoice_number', 'N/A')))
                self.recent_table.setItem(row, 1, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
                self.recent_table.setItem(row, 2, QTableWidgetItem(invoice.get('invoice_date', 'N/A')[:10] if invoice.get('invoice_date') else 'N/A'))
                self.recent_table.setItem(row, 3, QTableWidgetItem(f"₹{invoice.get('grand_total', 0):,.2f}"))
            
            print("Dashboard refreshed successfully")
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
            import traceback
            traceback.print_exc()