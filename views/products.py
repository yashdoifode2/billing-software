# fixed_products.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QHeaderView, QScrollArea, QFrame, QGridLayout,
                             QComboBox, QGroupBox, QMessageBox, QProgressBar,
                             QSplitter, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QPainter
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.product_controller import ProductController

class ModernTableWidget(QTableWidget):
    """Enhanced table widget with modern styling"""
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
                border-radius: 12px;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            ModernTableWidget::item {
                padding: 12px 10px;
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
                padding: 12px;
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
            QScrollBar:horizontal {
                border: none;
                background: #f1f1f1;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #c1c1c1;
                border-radius: 5px;
                min-width: 20px;
            }
        """)
        
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

class StatCard(QFrame):
    """Modern statistics card for product metrics"""
    def __init__(self, title, icon, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.color = color
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }}
            StatCard:hover {{
                background-color: #f8f9fa;
                border-color: {self.color};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)
        
        icon_container = QLabel(self.icon)
        icon_container.setStyleSheet(f"""
            background-color: {self.color}20;
            color: {self.color};
            font-size: 28px;
            padding: 10px;
            border-radius: 10px;
        """)
        icon_container.setFixedSize(50, 50)
        icon_container.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_container)
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
        text_layout.addWidget(title_label)
        
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"color: {self.color}; font-size: 24px; font-weight: bold;")
        text_layout.addWidget(self.value_label)
        
        layout.addWidget(text_container)
        layout.addStretch()
        
    def set_value(self, value):
        self.value_label.setText(str(value))

class SimpleBarChart(QFrame):
    """Simple bar chart using PyQt5 drawing"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        self.data = []
        self.labels = []
        self.title = ""
        
    def set_data(self, labels, values, title):
        self.labels = labels
        self.data = values
        self.title = title
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), Qt.white)
        
        # Draw title
        painter.setPen(QColor("#2c3e50"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 10, -10, -10), Qt.AlignTop | Qt.AlignHCenter, self.title)
        
        # Calculate chart area
        chart_rect = self.rect().adjusted(50, 50, -30, -30)
        
        if not self.data or max(self.data) == 0:
            painter.drawText(chart_rect, Qt.AlignCenter, "No data available")
            return
            
        # Draw bars
        bar_width = (chart_rect.width() - 20) / len(self.data) * 0.7
        spacing = (chart_rect.width() - 20) / len(self.data) * 0.3
        
        max_value = max(self.data)
        
        for i, (label, value) in enumerate(zip(self.labels, self.data)):
            x = chart_rect.x() + i * (bar_width + spacing) + spacing/2
            bar_height = (value / max_value) * chart_rect.height()
            y = chart_rect.y() + chart_rect.height() - bar_height
            
            # Draw bar
            color = QColor("#3498db")
            painter.fillRect(int(x), int(y), int(bar_width), int(bar_height), color)
            
            # Draw value on top of bar
            painter.setPen(QColor("#2c3e50"))
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(int(x), int(y - 5), int(bar_width), 20, Qt.AlignCenter, f"Rs.{value:,.0f}")
            
            # Draw label
            painter.drawText(int(x), int(chart_rect.y() + chart_rect.height() + 5), 
                           int(bar_width), 30, Qt.AlignCenter | Qt.TextWordWrap, label)

class SimplePieChart(QFrame):
    """Simple pie chart using PyQt5 drawing"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        self.data = {}
        self.title = ""
        
    def set_data(self, data_dict, title):
        self.data = data_dict
        self.title = title
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), Qt.white)
        
        # Draw title
        painter.setPen(QColor("#2c3e50"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 10, -10, -10), Qt.AlignTop | Qt.AlignHCenter, self.title)
        
        # Calculate pie area
        pie_size = min(self.width() - 200, self.height() - 100)
        pie_rect = QRect((self.width() - pie_size) // 2, (self.height() - pie_size) // 2, pie_size, pie_size)
        
        # Draw pie chart
        colors = [QColor("#2ecc71"), QColor("#f39c12"), QColor("#e74c3c"), QColor("#3498db"), QColor("#9b59b6")]
        total = sum(self.data.values())
        
        if total == 0:
            painter.drawText(pie_rect, Qt.AlignCenter, "No data available")
            return
            
        start_angle = 0
        legend_y = 50
        
        for i, (label, value) in enumerate(self.data.items()):
            angle = int(360 * value / total)
            
            # Draw pie slice
            painter.setBrush(colors[i % len(colors)])
            painter.drawPie(pie_rect, start_angle * 16, angle * 16)
            
            # Draw legend
            legend_x = self.width() - 150
            painter.fillRect(legend_x, legend_y, 15, 15, colors[i % len(colors)])
            painter.setPen(QColor("#2c3e50"))
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(legend_x + 20, legend_y + 12, f"{label}: {value} ({value/total*100:.1f}%)")
            
            legend_y += 25
            start_angle += angle

class ProductDetailsWidget(QWidget):
    """Product details and quick actions widget"""
    product_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_product = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        info_layout = QVBoxLayout(self.info_frame)
        
        self.product_icon = QLabel("📦")
        self.product_icon.setStyleSheet("""
            font-size: 48px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 40px;
            padding: 15px;
        """)
        self.product_icon.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.product_icon)
        
        self.product_name = QLabel("Select a product")
        self.product_name.setStyleSheet("color: white; font-size: 18px; font-weight: bold; text-align: center;")
        self.product_name.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.product_name)
        
        self.product_details = QLabel()
        self.product_details.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px;")
        self.product_details.setAlignment(Qt.AlignCenter)
        self.product_details.setWordWrap(True)
        info_layout.addWidget(self.product_details)
        
        layout.addWidget(self.info_frame)
        
        actions_group = QGroupBox("Quick Actions")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        actions_layout = QGridLayout(actions_group)
        
        self.edit_btn = QPushButton("✏️ Edit Product")
        self.edit_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        self.edit_btn.clicked.connect(self.edit_product)
        actions_layout.addWidget(self.edit_btn, 0, 0)
        
        self.duplicate_btn = QPushButton("📋 Duplicate")
        self.duplicate_btn.setStyleSheet(self.get_button_style("#9b59b6", "#8e44ad"))
        self.duplicate_btn.clicked.connect(self.duplicate_product)
        actions_layout.addWidget(self.duplicate_btn, 0, 1)
        
        self.stock_btn = QPushButton("📊 Update Stock")
        self.stock_btn.setStyleSheet(self.get_button_style("#f39c12", "#e67e22"))
        self.stock_btn.clicked.connect(self.update_stock)
        actions_layout.addWidget(self.stock_btn, 1, 0)
        
        self.price_btn = QPushButton("💰 Update Price")
        self.price_btn.setStyleSheet(self.get_button_style("#1abc9c", "#16a085"))
        self.price_btn.clicked.connect(self.update_price)
        actions_layout.addWidget(self.price_btn, 1, 1)
        
        layout.addWidget(actions_group)
        
        stock_group = QGroupBox("Stock Level")
        stock_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        stock_layout = QVBoxLayout(stock_group)
        self.stock_progress = QProgressBar()
        self.stock_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
            }
        """)
        stock_layout.addWidget(self.stock_progress)
        
        self.stock_label = QLabel()
        self.stock_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        self.stock_label.setAlignment(Qt.AlignCenter)
        stock_layout.addWidget(self.stock_label)
        
        layout.addWidget(stock_group)
        
    def get_button_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
        
    def update_product(self, product):
        """Update product details display"""
        self.current_product = product
        if product:
            self.product_name.setText(product.get('name', 'Unknown'))
            
            details = f"""
            📋 SKU: {product.get('sku', 'N/A')}<br>
            💰 Price: Rs. {product.get('price', 0):,.2f}<br>
            📊 Stock: {product.get('stock_quantity', 0)} units<br>
            🏷️ Category: {product.get('category', 'N/A')}<br>
            📈 Tax Rate: {product.get('tax_rate_cgst', 0) + product.get('tax_rate_sgst', 0)}%<br>
            """
            self.product_details.setText(details)
            
            stock = product.get('stock_quantity', 0)
            max_stock = 1000
            percentage = min(100, (stock / max_stock) * 100)
            
            self.stock_progress.setValue(int(percentage))
            
            if stock <= 10:
                self.stock_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #e74c3c; border-radius: 5px; }
                """)
                self.stock_label.setText(f"⚠️ Low Stock! Only {stock} units remaining")
            elif stock <= 50:
                self.stock_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #f39c12; border-radius: 5px; }
                """)
                self.stock_label.setText(f"📦 Stock level: {stock} units (Medium)")
            else:
                self.stock_progress.setStyleSheet("""
                    QProgressBar::chunk { background-color: #2ecc71; border-radius: 5px; }
                """)
                self.stock_label.setText(f"✅ Stock level: {stock} units (Good)")
                
    def edit_product(self):
        if self.current_product:
            self.product_selected.emit(self.current_product)
            
    def duplicate_product(self):
        if self.current_product:
            QMessageBox.information(self, "Duplicate Product", 
                                   f"Duplicating product: {self.current_product['name']}")
            
    def update_stock(self):
        if self.current_product:
            QMessageBox.information(self, "Update Stock", 
                                   f"Updating stock for: {self.current_product['name']}")
            
    def update_price(self):
        if self.current_product:
            QMessageBox.information(self, "Update Price", 
                                   f"Updating price for: {self.current_product['name']}")

class ProductsWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = ProductController(self, auth_service)
        self.current_product = None
        self.setup_ui()
        self.controller.load_products()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(300000)
        
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
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
        """)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Product Management")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_products_card = StatCard("Total Products", "📦", "#3498db")
        self.low_stock_card = StatCard("Low Stock Items", "⚠️", "#e74c3c")
        self.categories_card = StatCard("Categories", "🏷️", "#9b59b6")
        
        stats_layout.addWidget(self.total_products_card)
        stats_layout.addWidget(self.low_stock_card)
        stats_layout.addWidget(self.categories_card)
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
        
        # Search and Filter
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: white; border-radius: 15px; padding: 15px;")
        filter_layout = QHBoxLayout(filter_frame)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search products...")
        self.search_box.setMinimumHeight(40)
        self.search_box.setStyleSheet("border: 1px solid #dee2e6; border-radius: 10px; padding: 8px 15px;")
        self.search_box.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_box, 2)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Electronics", "Clothing", "Food", "Furniture"])
        self.category_filter.setStyleSheet("padding: 8px; border: 1px solid #dee2e6; border-radius: 8px;")
        filter_layout.addWidget(self.category_filter, 1)
        
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        apply_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Charts Section - Using PyQt5 native drawing
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)
        
        self.bar_chart = SimpleBarChart()
        self.pie_chart = SimplePieChart()
        
        charts_layout.addWidget(self.bar_chart)
        charts_layout.addWidget(self.pie_chart)
        main_layout.addWidget(charts_container)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        
        # Product Table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        
        table_header = QHBoxLayout()
        table_label = QLabel("Product List")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        table_header.addWidget(table_label)
        table_header.addStretch()
        
        self.add_btn = QPushButton("➕ Add Product")
        self.add_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        self.add_btn.clicked.connect(self.controller.add_product)
        table_header.addWidget(self.add_btn)
        
        table_layout.addLayout(table_header)
        
        self.table = ModernTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "SKU", "Name", "Category", "Price", "Stock", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumWidth(600)
        self.table.itemSelectionChanged.connect(self.on_product_selected)
        table_layout.addWidget(self.table)
        
        splitter.addWidget(table_container)
        
        # Product Details
        self.product_details = ProductDetailsWidget()
        self.product_details.product_selected.connect(self.on_edit_product)
        splitter.addWidget(self.product_details)
        
        splitter.setSizes([700, 300])
        main_layout.addWidget(splitter)
        
        # Status Bar
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 8px; margin-top: 10px;")
        status_layout = QHBoxLayout(status_bar)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.record_count = QLabel("0 records")
        self.record_count.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.record_count)
        main_layout.addWidget(status_bar)
        
        scroll_area.setWidget(main_widget)
        
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(scroll_area)
        
    def get_button_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
        
    def populate_table(self, products):
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product.get('sku', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(product.get('name', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(product.get('category', 'N/A')))
            
            price = product.get('price', 0)
            price_item = QTableWidgetItem(f"Rs. {price:,.2f}")
            if price > 10000:
                price_item.setForeground(QColor("#28a745"))
            self.table.setItem(row, 4, price_item)
            
            stock = product.get('stock_quantity', 0)
            stock_item = QTableWidgetItem(str(stock))
            if stock <= 10:
                stock_item.setForeground(QColor("#e74c3c"))
            elif stock <= 50:
                stock_item.setForeground(QColor("#f39c12"))
            else:
                stock_item.setForeground(QColor("#2ecc71"))
            self.table.setItem(row, 5, stock_item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(8)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 32)
            edit_btn.setStyleSheet("background-color: #3498db; color: white; border: none; border-radius: 6px;")
            edit_btn.clicked.connect(lambda checked, pid=product['id']: self.controller.edit_product(pid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 32)
            delete_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; border-radius: 6px;")
            delete_btn.clicked.connect(lambda checked, pid=product['id']: self.delete_product_with_confirmation(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 6, actions_widget)
        
        self.update_statistics(products)
        self.update_charts(products)
        self.record_count.setText(f"{len(products)} records")
        self.table.resizeColumnsToContents()
        
    def update_statistics(self, products):
        total = len(products)
        low_stock = len([p for p in products if p.get('stock_quantity', 0) <= 10])
        categories = len(set(p.get('category', 'Other') for p in products))
        
        self.total_products_card.set_value(total)
        self.low_stock_card.set_value(low_stock)
        self.categories_card.set_value(categories)
        
    def update_charts(self, products):
        """Update charts using PyQt5 native drawing"""
        try:
            if products:
                # Top 5 products by price for bar chart
                top_products = sorted(products, key=lambda x: x.get('price', 0), reverse=True)[:5]
                product_names = [p.get('name', 'Unknown')[:15] for p in top_products]
                revenues = [p.get('price', 0) for p in top_products]
                self.bar_chart.set_data(product_names, revenues, "Top Products by Price")
                
                # Stock status for pie chart
                stock_status = {
                    'Low Stock': len([p for p in products if p.get('stock_quantity', 0) <= 10]),
                    'Medium Stock': len([p for p in products if 10 < p.get('stock_quantity', 0) <= 50]),
                    'Good Stock': len([p for p in products if p.get('stock_quantity', 0) > 50])
                }
                self.pie_chart.set_data(stock_status, "Stock Distribution")
        except Exception as e:
            print(f"Error updating charts: {e}")
        
    def on_product_selected(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            product = {
                'id': int(self.table.item(row, 0).text()),
                'sku': self.table.item(row, 1).text(),
                'name': self.table.item(row, 2).text(),
                'category': self.table.item(row, 3).text(),
                'price': float(self.table.item(row, 4).text().replace('Rs.', '').replace(',', '').strip()),
                'stock_quantity': int(self.table.item(row, 5).text()),
            }
            self.current_product = product
            self.product_details.update_product(product)
            
    def delete_product_with_confirmation(self, product_id):
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     'Are you sure you want to delete this product?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.delete_product(product_id)
            
    def on_edit_product(self, product):
        if product:
            self.controller.edit_product(product['id'])
            
    def on_search(self, text):
        self.controller.search_products(text)
        
    def apply_filters(self):
        self.status_label.setText("Applying filters...")
        self.controller.load_products()
        
    def refresh(self):
        self.controller.load_products()
        
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()