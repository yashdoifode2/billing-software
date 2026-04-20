# enhanced_dashboard.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QGridLayout,
                             QDateEdit, QPushButton, QComboBox, QGroupBox,
                             QSplitter, QHeaderView, QScrollArea, QSizePolicy,
                             QSpacerItem, QApplication, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QDate, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QPainter, QPen
import sys
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.report_service import ReportService
from models.invoice import Invoice
from models.expense import Expense

class ModernCard(QFrame):
    """Modern styled card widget with hover effects"""
    clicked = pyqtSignal()
    
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 #f8f9fa);
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }}
            ModernCard:hover {{
                background-color: white;
                border: 1px solid {self.color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Title with icon placeholder
        title_layout = QHBoxLayout()
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #6c757d; font-size: 13px; font-weight: 500; letter-spacing: 0.5px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Value label
        self.value_label = QLabel("₹0")
        self.value_label.setStyleSheet(f"color: {self.color}; font-size: 32px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        # Trend indicator
        self.trend_label = QLabel()
        self.trend_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.trend_label)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def setup_animations(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def enterEvent(self, event):
        self.raise_()
        super().enterEvent(event)
        
    def update_value(self, value, trend=None):
        self.value_label.setText(value)
        if trend:
            trend_color = "#28a745" if trend > 0 else "#dc3545"
            trend_symbol = "▲" if trend > 0 else "▼"
            self.trend_label.setText(f"{trend_symbol} {abs(trend)}% from previous period")
            self.trend_label.setStyleSheet(f"color: {trend_color}; font-size: 11px;")

class ModernTableWidget(QTableWidget):
    """Enhanced table widget with better styling and functionality"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
        
    def setup_styling(self):
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        
        self.setStyleSheet("""
            ModernTableWidget {
                background-color: white;
                border: none;
                border-radius: 10px;
                gridline-color: #f0f0f0;
            }
            ModernTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            ModernTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            ModernTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 10px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                border-bottom: 2px solid #dee2e6;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Enable scrolling
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

class ChartWidget(FigureCanvas):
    """Matplotlib chart widget for visual analytics"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='#f8f9fa')
        super().__init__(self.figure)
        self.setParent(parent)
        self.setMinimumHeight(300)
        
        # Apply modern styling
        plt.style.use('seaborn-v0_8-darkgrid')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#f8f9fa')
        
    def plot_revenue_trend(self, dates, revenues):
        """Plot revenue trend over time"""
        self.ax.clear()
        
        # Create gradient fill
        self.ax.plot(dates, revenues, marker='o', linewidth=2, color='#3498db', markersize=6)
        self.ax.fill_between(range(len(dates)), revenues, alpha=0.3, color='#3498db')
        
        # Styling
        self.ax.set_title('Revenue Trend', fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel('Date', fontsize=11)
        self.ax.set_ylabel('Revenue (₹)', fontsize=11)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.tick_params(axis='both', labelsize=10)
        
        # Rotate x labels if needed
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.draw()
        
    def plot_expense_breakdown(self, categories, amounts):
        """Plot expense breakdown as pie chart"""
        self.ax.clear()
        
        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c']
        wedges, texts, autotexts = self.ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                                colors=colors[:len(categories)], startangle=90)
        
        # Style the text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
            
        self.ax.set_title('Expense Breakdown', fontsize=14, fontweight='bold', pad=20)
        self.ax.axis('equal')
        
        self.draw()

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
        
        # Setup auto-refresh timer (every 5 minutes)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(300000)  # 5 minutes
        
    def setup_ui(self):
        # Main layout with proper margins for resizing
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Scroll area for entire dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f4f6f9;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """)
        
        # Header Section
        header_layout = QHBoxLayout()
        
        # Title with gradient effect
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title = QLabel("Dashboard")
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        """)
        title_layout.addWidget(title)
        
        # Subtitle with date/time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-top: 5px;")
        self.update_datetime()
        title_layout.addWidget(self.datetime_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Refresh indicator
        self.refresh_indicator = QLabel("● Live")
        self.refresh_indicator.setStyleSheet("color: #28a745; font-size: 11px; font-weight: bold;")
        header_layout.addWidget(self.refresh_indicator)
        
        main_layout.addLayout(header_layout)
        
        # Date Filter Section with improved design
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)
        
        # Date range group
        date_group = QFrame()
        date_layout = QHBoxLayout(date_group)
        date_layout.setSpacing(10)
        
        # From Date
        from_container = QWidget()
        from_layout = QVBoxLayout(from_container)
        from_layout.setContentsMargins(0, 0, 0, 0)
        from_layout.addWidget(QLabel("From Date"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setStyleSheet(self.get_date_style())
        from_layout.addWidget(self.from_date)
        date_layout.addWidget(from_container)
        
        # To Date
        to_container = QWidget()
        to_layout = QVBoxLayout(to_container)
        to_layout.setContentsMargins(0, 0, 0, 0)
        to_layout.addWidget(QLabel("To Date"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet(self.get_date_style())
        to_layout.addWidget(self.to_date)
        date_layout.addWidget(to_container)
        
        filter_layout.addWidget(date_group)
        
        # Quick filters
        quick_container = QWidget()
        quick_layout = QVBoxLayout(quick_container)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        quick_layout.addWidget(QLabel("Quick Filter"))
        self.quick_filter = QComboBox()
        self.quick_filter.addItems(["Current Month", "Previous Month", "Last 30 Days", 
                                    "Last 90 Days", "This Year", "Last Year", "Custom"])
        self.quick_filter.currentTextChanged.connect(self.on_quick_filter)
        self.quick_filter.setStyleSheet(self.get_combobox_style())
        quick_layout.addWidget(self.quick_filter)
        filter_layout.addWidget(quick_container)
        
        filter_layout.addStretch()
        
        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        self.apply_btn = QPushButton("Apply Filter")
        self.apply_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        self.apply_btn.clicked.connect(self.refresh)
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(self.get_button_style("#95a5a6", "#7f8c8d"))
        self.reset_btn.clicked.connect(self.set_default_dates)
        button_layout.addWidget(self.reset_btn)
        
        filter_layout.addWidget(button_container)
        
        main_layout.addWidget(filter_frame)
        
        # Stats Cards Grid (Responsive)
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(20)
        self.stats_grid.setContentsMargins(0, 0, 0, 0)
        
        stats_config = [
            ("Total Revenue", "revenue", "#2ecc71"),
            ("Total Invoices", "invoices", "#3498db"),
            ("Total Expenses", "expenses", "#e74c3c"),
            ("Net Profit", "profit", "#27ae60"),
            ("Pending Amount", "pending", "#f39c12"),
            ("Avg. Invoice Value", "avg_invoice", "#9b59b6"),
        ]
        
        for i, (title_text, key, color) in enumerate(stats_config):
            card = ModernCard(title_text, color)
            self.stats_grid.addWidget(card, i // 3, i % 3)
            self.stats_cards[key] = card
        
        main_layout.addLayout(self.stats_grid)
        
        # Charts Section
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)
        
        # Revenue Trend Chart
        self.revenue_chart = ChartWidget(self, width=6, height=4)
        charts_layout.addWidget(self.revenue_chart)
        
        # Expense Breakdown Chart
        self.expense_chart = ChartWidget(self, width=5, height=4)
        charts_layout.addWidget(self.expense_chart)
        
        main_layout.addWidget(charts_container)
        
        # Splitter for Recent Invoices and Top Products
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dee2e6;
                height: 1px;
            }
        """)
        
        # Recent Invoices Section
        recent_widget = QWidget()
        recent_layout = QVBoxLayout(recent_widget)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        
        recent_header = QHBoxLayout()
        recent_label = QLabel("Recent Invoices")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        recent_header.addWidget(recent_label)
        
        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.setStyleSheet(self.get_button_style("#6c757d", "#5a6268", small=True))
        export_btn.clicked.connect(self.export_invoices)
        recent_header.addWidget(export_btn)
        
        recent_layout.addLayout(recent_header)
        
        self.recent_table = ModernTableWidget()
        self.recent_table.setColumnCount(7)
        self.recent_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Due Date", "Status", "Total", "Paid"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        
        self.top_products_table = ModernTableWidget()
        self.top_products_table.setColumnCount(5)
        self.top_products_table.setHorizontalHeaderLabels(["Product Name", "HSN Code", "Quantity Sold", "Revenue", "Contribution %"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_products_table.setMinimumHeight(250)
        products_layout.addWidget(self.top_products_table)
        
        splitter.addWidget(products_widget)
        
        splitter.setSizes([400, 300])
        main_layout.addWidget(splitter)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        last_update = QLabel(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        last_update.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(last_update)
        
        main_layout.addWidget(status_bar)
        
        # Set the scroll area
        scroll_area.setWidget(main_widget)
        
        # Main layout
        main_container = QVBoxLayout(self)
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.addWidget(scroll_area)
        
        # Make the widget responsive
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Setup timer for datetime
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Update every second
        
    def get_date_style(self):
        return """
            QDateEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                min-width: 120px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """
        
    def get_combobox_style(self):
        return """
            QComboBox {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
                margin-right: 5px;
            }
        """
        
    def get_button_style(self, bg_color, hover_color, small=False):
        padding = "6px 12px" if small else "10px 20px"
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: {padding};
                border-radius: 8px;
                font-weight: bold;
                font-size: {11 if small else 13}px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                padding-top: {int(padding.split()[0][0])+2}px;
            }}
        """
        
    def update_datetime(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.now().strftime("%B %d, %Y")
        self.datetime_label.setText(f"{current_date} | {current_time}")
        
    def set_default_dates(self):
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        
        self.from_date.setDate(first_day)
        self.to_date.setDate(today)
        self.quick_filter.setCurrentText("Current Month")
        self.refresh()
    
    def on_quick_filter(self, filter_text):
        today = QDate.currentDate()
        
        if filter_text == "Current Month":
            first_day = QDate(today.year(), today.month(), 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
        elif filter_text == "Previous Month":
            if today.month() == 1:
                first_day = QDate(today.year() - 1, 12, 1)
                last_day = QDate(today.year() - 1, 12, 31)
            else:
                first_day = QDate(today.year(), today.month() - 1, 1)
                last_day = QDate(today.year(), today.month(), 1).addDays(-1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(last_day)
        elif filter_text == "Last 30 Days":
            self.from_date.setDate(today.addDays(-30))
            self.to_date.setDate(today)
        elif filter_text == "Last 90 Days":
            self.from_date.setDate(today.addDays(-90))
            self.to_date.setDate(today)
        elif filter_text == "This Year":
            first_day = QDate(today.year(), 1, 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
        elif filter_text == "Last Year":
            first_day = QDate(today.year() - 1, 1, 1)
            last_day = QDate(today.year() - 1, 12, 31)
            self.from_date.setDate(first_day)
            self.to_date.setDate(last_day)
        
        if filter_text != "Custom":
            self.refresh()
    
    def refresh(self):
        try:
            self.status_label.setText("Loading data...")
            QApplication.processEvents()
            
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get filtered data
            stats = self.get_filtered_stats(from_date, to_date)
            
            # Update stat cards
            self.stats_cards['revenue'].update_value(f"₹{stats.get('total_revenue', 0):,.2f}")
            self.stats_cards['invoices'].update_value(str(stats.get('total_invoices', 0)))
            self.stats_cards['expenses'].update_value(f"₹{stats.get('total_expenses', 0):,.2f}")
            
            profit = stats.get('net_profit', 0)
            profit_color = "#27ae60" if profit >= 0 else "#e74c3c"
            self.stats_cards['profit'].update_value(f"₹{profit:,.2f}")
            
            self.stats_cards['pending'].update_value(f"₹{stats.get('pending_amount', 0):,.2f}")
            self.stats_cards['avg_invoice'].update_value(f"₹{stats.get('avg_invoice_value', 0):,.2f}")
            
            # Update charts
            self.update_charts(from_date, to_date)
            
            # Update recent invoices
            recent_invoices = self.get_recent_invoices(from_date, to_date)
            self.recent_table.setRowCount(len(recent_invoices))
            for row, invoice in enumerate(recent_invoices):
                self.recent_table.setItem(row, 0, QTableWidgetItem(invoice.get('invoice_number', 'N/A')))
                self.recent_table.setItem(row, 1, QTableWidgetItem(invoice.get('customer_name', 'N/A')))
                self.recent_table.setItem(row, 2, QTableWidgetItem(invoice.get('invoice_date', 'N/A')[:10]))
                self.recent_table.setItem(row, 3, QTableWidgetItem(invoice.get('due_date', 'N/A')[:10] if invoice.get('due_date') else 'N/A'))
                
                # Status with color and icon
                status = invoice.get('status', 'pending')
                status_item = QTableWidgetItem(status.upper())
                status_colors = {
                    'paid': '#28a745',
                    'pending': '#ffc107',
                    'overdue': '#dc3545',
                    'cancelled': '#6c757d'
                }
                status_item.setForeground(QColor(status_colors.get(status, '#6c757d')))
                self.recent_table.setItem(row, 4, status_item)
                
                self.recent_table.setItem(row, 5, QTableWidgetItem(f"₹{invoice.get('grand_total', 0):,.2f}"))
                paid_amount = invoice.get('paid_amount', 0)
                self.recent_table.setItem(row, 6, QTableWidgetItem(f"₹{paid_amount:,.2f}"))
                
                # Color code rows based on status
                if status == 'overdue':
                    for col in range(7):
                        self.recent_table.item(row, col).setBackground(QColor(255, 240, 240))
            
            # Update top products
            top_products = self.get_top_products(from_date, to_date)
            total_revenue = sum(p.get('total_revenue', 0) for p in top_products)
            self.top_products_table.setRowCount(len(top_products))
            for row, product in enumerate(top_products):
                self.top_products_table.setItem(row, 0, QTableWidgetItem(product.get('product_name', 'N/A')))
                self.top_products_table.setItem(row, 1, QTableWidgetItem(product.get('hsn_code', 'N/A')))
                quantity = product.get('total_quantity', 0)
                quantity_str = str(int(quantity)) if quantity.is_integer() else f"{quantity:.2f}"
                self.top_products_table.setItem(row, 2, QTableWidgetItem(quantity_str))
                revenue = product.get('total_revenue', 0)
                self.top_products_table.setItem(row, 3, QTableWidgetItem(f"₹{revenue:,.2f}"))
                
                # Contribution percentage
                contribution = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                contrib_item = QTableWidgetItem(f"{contribution:.1f}%")
                if contribution > 20:
                    contrib_item.setForeground(QColor("#28a745"))
                elif contribution > 10:
                    contrib_item.setForeground(QColor("#ffc107"))
                self.top_products_table.setItem(row, 4, contrib_item)
            
            # Resize tables
            self.recent_table.resizeColumnsToContents()
            self.top_products_table.resizeColumnsToContents()
            
            self.status_label.setText("Data loaded successfully")
            
            # Update refresh indicator
            self.refresh_indicator.setStyleSheet("color: #28a745; font-size: 11px; font-weight: bold;")
            QTimer.singleShot(2000, lambda: self.refresh_indicator.setStyleSheet("color: #6c757d; font-size: 11px;"))
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            print(f"Dashboard refresh error: {e}")
            import traceback
            traceback.print_exc()
    
    def update_charts(self, from_date, to_date):
        """Update visual analytics charts"""
        try:
            # Get daily revenue data
            query = """
                SELECT invoice_date, SUM(grand_total) as daily_revenue
                FROM invoices
                WHERE invoice_date BETWEEN ? AND ? AND status = 'paid'
                GROUP BY invoice_date
                ORDER BY invoice_date
            """
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            revenue_data = db.fetch_all(query, (from_date, to_date))
            
            if revenue_data:
                dates = [row['invoice_date'][5:10] for row in revenue_data]  # MM-DD format
                revenues = [row['daily_revenue'] for row in revenue_data]
                self.revenue_chart.plot_revenue_trend(dates, revenues)
            
            # Get expense breakdown by category
            expense_query = """
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE expense_date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
                LIMIT 6
            """
            expense_data = db.fetch_all(expense_query, (from_date, to_date))
            
            if expense_data:
                categories = [row['category'][:15] for row in expense_data]  # Truncate long names
                amounts = [row['total'] for row in expense_data]
                self.expense_chart.plot_expense_breakdown(categories, amounts)
                
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def export_invoices(self):
        """Export recent invoices to CSV"""
        try:
            from datetime import datetime
            import csv
            
            filename = f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                headers = [self.recent_table.horizontalHeaderItem(i).text() 
                          for i in range(self.recent_table.columnCount())]
                writer.writerow(headers)
                
                # Write data
                for row in range(self.recent_table.rowCount()):
                    row_data = []
                    for col in range(self.recent_table.columnCount()):
                        item = self.recent_table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            self.status_label.setText(f"Exported to {filename}")
        except Exception as e:
            self.status_label.setText(f"Export failed: {str(e)}")
    
    def get_filtered_stats(self, from_date, to_date):
        """Get filtered statistics for date range"""
        try:
            query = """
                SELECT * FROM invoices 
                WHERE invoice_date BETWEEN ? AND ?
            """
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            invoices = db.fetch_all(query, (from_date, to_date))
            
            total_revenue = sum(inv.get('grand_total', 0) for inv in invoices if inv.get('status') == 'paid')
            total_invoices = len(invoices)
            pending_amount = sum(inv.get('grand_total', 0) - inv.get('paid_amount', 0) 
                               for inv in invoices if inv.get('status') != 'paid')
            avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
            
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