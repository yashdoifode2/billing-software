from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models.invoice import Invoice
from controllers.settings_controller import SettingsController

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.invoice_model = Invoice()
        self.settings = SettingsController()
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Dashboard")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Stats cards layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_invoices_card = self.create_stat_card("Total Invoices", "0")
        self.total_revenue_card = self.create_stat_card("Total Revenue", "$0")
        
        stats_layout.addWidget(self.total_invoices_card)
        stats_layout.addWidget(self.total_revenue_card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Recent invoices
        recent_label = QLabel("Recent Invoices")
        recent_label.setObjectName("section_title")
        layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Total"])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recent_table)
    
    def create_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("stat_card")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setObjectName("stat_title")
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def refresh_data(self):
        stats = self.invoice_model.get_dashboard_stats()
        settings = self.settings.get_settings()
        currency = settings.get('currency_symbol', '$')
        
        self.total_invoices_card.findChild(QLabel, "stat_value").setText(str(stats['total_invoices']))
        self.total_revenue_card.findChild(QLabel, "stat_value").setText(f"{currency}{stats['total_revenue']:,.2f}")
        
        # Update recent invoices table
        self.recent_table.setRowCount(len(stats['recent_invoices']))
        for row, invoice in enumerate(stats['recent_invoices']):
            self.recent_table.setItem(row, 0, QTableWidgetItem(invoice['invoice_number']))
            self.recent_table.setItem(row, 1, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
            self.recent_table.setItem(row, 2, QTableWidgetItem(invoice['invoice_date'][:10]))
            self.recent_table.setItem(row, 3, QTableWidgetItem(f"{currency}{invoice['grand_total']:,.2f}"))