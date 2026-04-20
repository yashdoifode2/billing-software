from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QListWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from views.dashboard import DashboardWidget
from views.customers import CustomersWidget
from views.products import ProductsWidget
from views.invoices import InvoicesWidget
from views.settings import SettingsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Invoice System")
        self.setGeometry(100, 100, 1200, 700)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(10)
        
        # Logo/title
        title = QLabel("Invoice System")
        title.setObjectName("sidebar_title")
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("📊 Dashboard", 0),
            ("👥 Customers", 1),
            ("📦 Products", 2),
            ("📄 Invoices", 3),
            ("⚙️ Settings", 4)
        ]
        
        for text, index in nav_items:
            btn = QListWidget()
            btn.addItem(text)
            btn.setMaximumHeight(50)
            btn.setObjectName("nav_button")
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[index] = btn
        
        sidebar_layout.addStretch()
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.dashboard = DashboardWidget()
        self.customers = CustomersWidget()
        self.products = ProductsWidget()
        self.invoices = InvoicesWidget()
        self.settings = SettingsWidget()
        
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.customers)
        self.stacked_widget.addWidget(self.products)
        self.stacked_widget.addWidget(self.invoices)
        self.stacked_widget.addWidget(self.settings)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)
    
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        # Refresh dashboard when switching to it
        if index == 0:
            self.dashboard.refresh_data()
    
    def apply_styles(self):
        with open('resources/styles.qss', 'r') as f:
            self.setStyleSheet(f.read())