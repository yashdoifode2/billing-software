from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ReportsWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Coming Soon message
        coming_soon = QLabel("📊 Reports Module Coming Soon")
        coming_soon.setStyleSheet("font-size: 18px; color: #7f8c8d; margin-top: 100px;")
        coming_soon.setAlignment(Qt.AlignCenter)
        layout.addWidget(coming_soon)
        
        layout.addStretch()
    
    def refresh(self):
        pass