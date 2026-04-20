# fixed_customers.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QHeaderView, QScrollArea, QFrame, QGridLayout,
                             QComboBox, QDateEdit, QGroupBox, QMessageBox,
                             QProgressBar, QMenu, QAction, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QBrush, QLinearGradient
import sys
import os
from datetime import datetime, timedelta  # IMPORTANT: Added timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.customer_controller import CustomerController

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
        self.setWordWrap(False)
        
        self.setStyleSheet("""
            ModernTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            ModernTableWidget::item {
                padding: 14px 10px;
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
                text-transform: uppercase;
                letter-spacing: 0.5px;
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
            QScrollBar::handle:horizontal:hover {
                background: #a8a8a8;
            }
        """)
        
        # Enable smooth scrolling
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

class StatCard(QFrame):
    """Modern statistics card"""
    clicked = pyqtSignal()
    
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
        
        # Icon container
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
        
        # Text container
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

class CustomerProfileWidget(QWidget):
    """Customer profile summary widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.profile_frame = QFrame()
        self.profile_frame.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        profile_layout = QVBoxLayout(self.profile_frame)
        
        # Avatar
        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("""
            font-size: 48px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 40px;
            padding: 15px;
        """)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(self.avatar_label)
        
        # Customer name
        self.name_label = QLabel("Select a customer")
        self.name_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; text-align: center;")
        self.name_label.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(self.name_label)
        
        # Customer details
        self.details_label = QLabel()
        self.details_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px;")
        self.details_label.setAlignment(Qt.AlignCenter)
        self.details_label.setWordWrap(True)
        profile_layout.addWidget(self.details_label)
        
        layout.addWidget(self.profile_frame)
        
    def update_profile(self, customer):
        if customer:
            self.name_label.setText(customer.get('name', 'Unknown'))
            details = f"""
            📞 {customer.get('phone', 'N/A')}<br>
            ✉️ {customer.get('email', 'N/A')}<br>
            📍 {customer.get('address', 'N/A')}<br>
            🆔 GST: {customer.get('gst_number', 'N/A')}
            """
            self.details_label.setText(details)
        else:
            self.name_label.setText("No customer selected")
            self.details_label.setText("Select a customer from the list to view details")

class CustomersWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.controller = CustomerController(self, auth_service)
        self.current_customer = None
        self.setup_ui()
        self.controller.load_customers()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(300000)  # 5 minutes
        
    def setup_ui(self):
        # Main container with scroll area
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Scroll area for entire widget
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
        
        # Title with simple styling
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Customer Management")
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold;
            color: #2c3e50;
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Manage your customer relationships")
        subtitle.setStyleSheet("color: #6c757d; font-size: 13px; margin-top: 5px;")
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Stats cards
        stats_container = QHBoxLayout()
        stats_container.setSpacing(15)
        
        self.total_customers_card = StatCard("Total Customers", "👥", "#3498db")
        self.active_customers_card = StatCard("Active Customers", "✅", "#2ecc71")
        self.new_customers_card = StatCard("New (30 days)", "🆕", "#f39c12")
        
        stats_container.addWidget(self.total_customers_card)
        stats_container.addWidget(self.active_customers_card)
        stats_container.addWidget(self.new_customers_card)
        stats_container.addStretch()
        
        main_layout.addLayout(stats_container)
        
        # Search and filter section
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
        
        # Search box
        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(QLabel("Search Customers"))
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search by name, phone, or email...")
        self.search_box.setMinimumHeight(40)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_box.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_box)
        filter_layout.addWidget(search_container)
        
        # Filter by date range
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.addWidget(QLabel("Customer Since"))
        
        date_filter_layout = QHBoxLayout()
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-6))
        self.from_date.setStyleSheet(self.get_date_style())
        date_filter_layout.addWidget(self.from_date)
        
        date_filter_layout.addWidget(QLabel("to"))
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet(self.get_date_style())
        date_filter_layout.addWidget(self.to_date)
        
        date_layout.addLayout(date_filter_layout)
        filter_layout.addWidget(date_container)
        
        # Filter by status
        status_container = QWidget()
        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(QLabel("Customer Status"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Customers", "Active", "Inactive", "VIP", "Regular"])
        self.status_filter.setStyleSheet(self.get_combobox_style())
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        status_layout.addWidget(self.status_filter)
        filter_layout.addWidget(status_container)
        
        # Apply filter button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        apply_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Splitter for customer list and profile
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dee2e6;
                width: 1px;
            }
        """)
        
        # Left side - Customer table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table header with actions
        table_header = QHBoxLayout()
        table_label = QLabel("Customer List")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        table_header.addWidget(table_label)
        table_header.addStretch()
        
        # Action buttons
        self.add_btn = QPushButton("➕ Add Customer")
        self.add_btn.setMinimumHeight(38)
        self.add_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        self.add_btn.clicked.connect(self.controller.add_customer)
        table_header.addWidget(self.add_btn)
        
        self.export_btn = QPushButton("📊 Export")
        self.export_btn.setMinimumHeight(38)
        self.export_btn.setStyleSheet(self.get_button_style("#6c757d", "#5a6268"))
        self.export_btn.clicked.connect(self.export_customers)
        table_header.addWidget(self.export_btn)
        
        table_layout.addLayout(table_header)
        
        # Customer table
        self.table = ModernTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Total Spent", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumWidth(600)
        self.table.itemSelectionChanged.connect(self.on_customer_selected)
        table_layout.addWidget(self.table)
        
        splitter.addWidget(table_container)
        
        # Right side - Customer profile
        profile_container = QWidget()
        profile_layout = QVBoxLayout(profile_container)
        profile_layout.setContentsMargins(10, 0, 0, 0)
        
        # Profile widget
        self.profile_widget = CustomerProfileWidget()
        profile_layout.addWidget(self.profile_widget)
        
        # Quick actions
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
        
        self.new_invoice_btn = QPushButton("📄 New Invoice")
        self.new_invoice_btn.setStyleSheet(self.get_button_style("#2ecc71", "#27ae60"))
        self.new_invoice_btn.clicked.connect(self.create_invoice)
        actions_layout.addWidget(self.new_invoice_btn, 0, 0)
        
        self.view_history_btn = QPushButton("📜 View History")
        self.view_history_btn.setStyleSheet(self.get_button_style("#9b59b6", "#8e44ad"))
        self.view_history_btn.clicked.connect(self.view_history)
        actions_layout.addWidget(self.view_history_btn, 0, 1)
        
        self.send_email_btn = QPushButton("✉️ Send Email")
        self.send_email_btn.setStyleSheet(self.get_button_style("#f39c12", "#e67e22"))
        self.send_email_btn.clicked.connect(self.send_email)
        actions_layout.addWidget(self.send_email_btn, 1, 0)
        
        self.send_sms_btn = QPushButton("📱 Send SMS")
        self.send_sms_btn.setStyleSheet(self.get_button_style("#1abc9c", "#16a085"))
        self.send_sms_btn.clicked.connect(self.send_sms)
        actions_layout.addWidget(self.send_sms_btn, 1, 1)
        
        profile_layout.addWidget(actions_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        activity_layout = QVBoxLayout(activity_group)
        self.activity_list = QLabel("No recent activity")
        self.activity_list.setStyleSheet("color: #6c757d; padding: 10px;")
        self.activity_list.setWordWrap(True)
        activity_layout.addWidget(self.activity_list)
        
        profile_layout.addWidget(activity_group)
        
        splitter.addWidget(profile_container)
        
        # Set splitter proportions (70% table, 30% profile)
        splitter.setSizes([700, 300])
        
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
        
        self.record_count = QLabel("0 records")
        self.record_count.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.record_count)
        
        main_layout.addWidget(status_bar)
        
        # Set scroll area
        scroll_area.setWidget(main_widget)
        
        # Main layout
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(scroll_area)
        
    def get_date_style(self):
        return """
            QDateEdit {
                padding: 6px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                min-width: 100px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """
        
    def get_combobox_style(self):
        return """
            QComboBox {
                padding: 6px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                min-width: 120px;
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
        padding = "6px 12px" if small else "8px 16px"
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
            }}
        """
        
    def populate_table(self, customers):
        self.table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            # Basic info
            self.table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(customer.get('name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(customer.get('phone', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(customer.get('email', 'N/A')))
            
            # Total spent (if available from invoices)
            total_spent = customer.get('total_spent', 0)
            spent_item = QTableWidgetItem(f"Rs. {total_spent:,.2f}")
            if total_spent > 10000:
                spent_item.setForeground(QColor("#28a745"))
            elif total_spent > 5000:
                spent_item.setForeground(QColor("#ffc107"))
            self.table.setItem(row, 4, spent_item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(8)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(35, 32)
            edit_btn.setToolTip("Edit Customer")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, cid=customer['id']: self.controller.edit_customer(cid))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(35, 32)
            delete_btn.setToolTip("Delete Customer")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda checked, cid=customer['id']: self.delete_customer_with_confirmation(cid))
            
            view_btn = QPushButton("👁️")
            view_btn.setFixedSize(35, 32)
            view_btn.setToolTip("View Details")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            view_btn.clicked.connect(lambda checked, cid=customer['id']: self.view_customer_details(cid))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 5, actions_widget)
        
        # Update statistics
        self.update_statistics(customers)
        
        # Update record count
        self.record_count.setText(f"{len(customers)} records")
        
        self.table.resizeColumnsToContents()
        
    def update_statistics(self, customers):
        """Update statistics cards"""
        total = len(customers)
        active = len([c for c in customers if c.get('status', 'active') == 'active'])
        
        # Calculate new customers in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new = 0
        for c in customers:
            created_at = c.get('created_at', '')
            if created_at:
                try:
                    created_date = datetime.strptime(created_at[:10], '%Y-%m-%d')
                    if created_date > thirty_days_ago:
                        new += 1
                except:
                    pass
        
        self.total_customers_card.set_value(total)
        self.active_customers_card.set_value(active)
        self.new_customers_card.set_value(new)
        
    def on_customer_selected(self):
        """Handle customer selection from table"""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            customer = {
                'id': int(self.table.item(row, 0).text()),
                'name': self.table.item(row, 1).text(),
                'phone': self.table.item(row, 2).text(),
                'email': self.table.item(row, 3).text(),
                'total_spent': float(self.table.item(row, 4).text().replace('Rs.', '').replace(',', '').strip())
            }
            self.current_customer = customer
            self.profile_widget.update_profile(customer)
            self.load_recent_activity(customer['id'])
            
    def load_recent_activity(self, customer_id):
        """Load recent activity for selected customer"""
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            # Get recent invoices
            query = """
                SELECT invoice_number, invoice_date, grand_total, status
                FROM invoices
                WHERE customer_id = ?
                ORDER BY invoice_date DESC
                LIMIT 5
            """
            invoices = db.fetch_all(query, (customer_id,))
            
            if invoices:
                activity_text = "<b>Recent Invoices:</b><br><br>"
                for inv in invoices:
                    activity_text += f"📄 {inv['invoice_number']} - {inv['invoice_date'][:10]} - Rs. {inv['grand_total']:,.2f} ({inv['status']})<br>"
                self.activity_list.setText(activity_text)
            else:
                self.activity_list.setText("No recent activity")
        except Exception as e:
            print(f"Error loading activity: {e}")
            self.activity_list.setText("Unable to load activity")
            
    def delete_customer_with_confirmation(self, customer_id):
        """Delete customer with confirmation dialog"""
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     'Are you sure you want to delete this customer?\nThis action cannot be undone.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.controller.delete_customer(customer_id)
            
    def view_customer_details(self, customer_id):
        """View detailed customer information"""
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            query = "SELECT * FROM customers WHERE id = ?"
            customer = db.fetch_one(query, (customer_id,))
            
            if customer:
                details = f"""
                <b>Customer Details</b><br><br>
                <b>Name:</b> {customer.get('name', 'N/A')}<br>
                <b>Phone:</b> {customer.get('phone', 'N/A')}<br>
                <b>Email:</b> {customer.get('email', 'N/A')}<br>
                <b>Address:</b> {customer.get('address', 'N/A')}<br>
                <b>GST Number:</b> {customer.get('gst_number', 'N/A')}<br>
                <b>Customer Since:</b> {customer.get('created_at', 'N/A')[:10] if customer.get('created_at') else 'N/A'}<br>
                """
                
                QMessageBox.information(self, "Customer Details", details)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load customer details: {str(e)}")
            
    def create_invoice(self):
        """Create new invoice for selected customer"""
        if self.current_customer:
            QMessageBox.information(self, "Create Invoice", 
                                   f"Creating new invoice for {self.current_customer['name']}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a customer first")
            
    def view_history(self):
        """View customer transaction history"""
        if self.current_customer:
            QMessageBox.information(self, "Transaction History", 
                                   f"Showing transaction history for {self.current_customer['name']}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a customer first")
            
    def send_email(self):
        """Send email to customer"""
        if self.current_customer and self.current_customer.get('email'):
            QMessageBox.information(self, "Send Email", 
                                   f"Sending email to {self.current_customer['email']}")
        elif self.current_customer:
            QMessageBox.warning(self, "No Email", "This customer doesn't have an email address")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a customer first")
            
    def send_sms(self):
        """Send SMS to customer"""
        if self.current_customer and self.current_customer.get('phone'):
            QMessageBox.information(self, "Send SMS", 
                                   f"Sending SMS to {self.current_customer['phone']}")
        elif self.current_customer:
            QMessageBox.warning(self, "No Phone", "This customer doesn't have a phone number")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a customer first")
            
    def export_customers(self):
        """Export customer list to CSV"""
        try:
            from datetime import datetime
            import csv
            
            filename = f"customers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = [self.table.horizontalHeaderItem(i).text() 
                          for i in range(self.table.columnCount() - 1)]  # Exclude actions column
                writer.writerow(headers)
                
                # Write data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount() - 1):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            self.status_label.setText(f"Exported to {filename}")
            QMessageBox.information(self, "Export Successful", f"Customers exported to {filename}")
        except Exception as e:
            self.status_label.setText(f"Export failed: {str(e)}")
            QMessageBox.warning(self, "Export Failed", str(e))
            
    def on_search(self, text):
        """Handle search input"""
        self.status_label.setText(f"Searching for: {text}")
        self.controller.search_customers(text)
        
    def on_filter_changed(self):
        """Handle filter changes"""
        self.apply_filters()
        
    def apply_filters(self):
        """Apply all filters"""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        status = self.status_filter.currentText()
        
        self.status_label.setText("Applying filters...")
        # In a real implementation, you would pass these filters to the controller
        self.controller.load_customers()
        
    def refresh(self):
        """Refresh the customer list"""
        self.status_label.setText("Refreshing...")
        self.controller.load_customers()
        
    def showEvent(self, event):
        """Called when widget becomes visible"""
        super().showEvent(event)
        self.refresh()