from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt

class DashboardWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        stats_data = [
            ("Total Revenue", "₹0", "#3498db"),
            ("Total Invoices", "0", "#27ae60"),
            ("Pending Amount", "₹0", "#e74c3c"),
            ("Total Customers", "0", "#f39c12"),
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            card = self.create_stat_card(title, value, color)
            stats_layout.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(stats_layout)
        
        # Welcome message
        welcome = QLabel(f"Welcome back, {self.auth_service.current_user['full_name']}!")
        welcome.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-top: 30px;")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        layout.addStretch()
    
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #ecf0f1;
            }}
        """)
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def refresh(self):
        print("Dashboard refreshed")