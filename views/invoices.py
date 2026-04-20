from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                             QHeaderView, QMessageBox, QScrollArea, QFrame,
                             QComboBox, QDateEdit, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.invoice_controller import InvoiceController

class ModernButton(QPushButton):
    """Custom styled button for consistent UI"""
    def __init__(self, text, color="#3498db", icon="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.2)};
            }}
        """)
    
    def darken_color(self, color, factor=0.1):
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#e74c3c": "#c0392b",
            "#f39c12": "#e67e22",
            "#9b59b6": "#8e44ad"
        }
        return color_map.get(color, color)

class StatsCard(QFrame):
    """Card widget for displaying statistics"""
    def __init__(self, title, value, icon="📊", color="#3498db"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value label
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
        """)
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        if self and self.value_label and not self.value_label.isHidden():
            try:
                self.value_label.setText(str(value))
            except RuntimeError:
                pass

class InvoicesWidget(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.is_closing = False
        self.controller = InvoiceController(self, auth_service)
        self.setup_ui()
        self.controller.load_invoices()
        self.setup_styles()
    
    def closeEvent(self, event):
        """Handle cleanup when widget is closed"""
        self.is_closing = True
        if hasattr(self, 'controller'):
            self.controller = None
        event.accept()
    
    def isWidgetValid(self):
        """Check if widget is still valid"""
        try:
            return not self.is_closing and self and not self.isHidden()
        except:
            return False
    
    def setup_styles(self):
        """Set global styles for the widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db20;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                font-weight: 600;
                border: none;
                border-bottom: 2px solid #9b59b6;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px 12px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
                min-height: 35px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #9b59b6;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #bdc3c7;
                border-radius: 5px;
                min-width: 20px;
            }
        """)
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_layout = QHBoxLayout()
        title = QLabel("📄 Invoice Management")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Quick stats info
        stats_info = QLabel("Real-time Analytics")
        stats_info.setStyleSheet("color: #9b59b6; font-size: 12px; font-weight: 500;")
        header_layout.addWidget(stats_info)
        
        main_layout.addLayout(header_layout)
        
        # Statistics Cards Section
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_revenue_card = StatsCard("Total Revenue", "₹0", "💰", "#9b59b6")
        self.paid_amount_card = StatsCard("Paid Amount", "₹0", "✅", "#27ae60")
        self.pending_amount_card = StatsCard("Pending Amount", "₹0", "⏳", "#f39c12")
        self.total_invoices_card = StatsCard("Total Invoices", "0", "📊", "#3498db")
        self.overdue_card = StatsCard("Overdue", "0", "⚠️", "#e74c3c")
        
        stats_layout.addWidget(self.total_revenue_card)
        stats_layout.addWidget(self.paid_amount_card)
        stats_layout.addWidget(self.pending_amount_card)
        stats_layout.addWidget(self.total_invoices_card)
        stats_layout.addWidget(self.overdue_card)
        
        main_layout.addLayout(stats_layout)
        
        # Search and Filter Section
        filter_container = QFrame()
        filter_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setSpacing(15)
        
        # Search box
        search_container = QHBoxLayout()
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 16px;")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by invoice #, customer name...")
        self.search_box.setMinimumWidth(250)
        self.search_box.textChanged.connect(self.on_search)
        search_container.addWidget(search_label)
        search_container.addWidget(self.search_box)
        filter_layout.addLayout(search_container)
        
        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Paid", "Pending", "Overdue"])
        self.status_filter.setMinimumWidth(120)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        
        # Date range filter
        date_label = QLabel("Date:")
        date_label.setStyleSheet("font-weight: 500; color: #2c3e50;")
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("to"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_container)
        
        # Action Buttons Section
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.create_btn = ModernButton("➕ Create Invoice", "#27ae60")
        self.create_btn.clicked.connect(self.safe_create_invoice)
        action_layout.addWidget(self.create_btn)
        
        self.refresh_btn = ModernButton("🔄 Refresh", "#3498db")
        self.refresh_btn.clicked.connect(self.refresh)
        action_layout.addWidget(self.refresh_btn)
        
        self.export_btn = ModernButton("📥 Export Data", "#9b59b6")
        self.export_btn.clicked.connect(self.export_data)
        action_layout.addWidget(self.export_btn)
        
        self.summary_btn = ModernButton("📊 Summary Report", "#f39c12")
        self.summary_btn.clicked.connect(self.show_summary)
        action_layout.addWidget(self.summary_btn)
        
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # Table with Scroll Area
        table_container = QFrame()
        table_container.setFrameStyle(QFrame.NoFrame)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Invoice #", "Customer", "Date", "Due Date", "Status", "Total", "Actions"])
        
        # Configure table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 130)  # Invoice #
        self.table.setColumnWidth(2, 180)  # Customer
        self.table.setColumnWidth(3, 100)  # Date
        self.table.setColumnWidth(4, 100)  # Due Date
        self.table.setColumnWidth(5, 100)  # Status
        self.table.setColumnWidth(6, 120)  # Total
        self.table.setColumnWidth(7, 180)  # Actions
        
        # Enable horizontal scrolling if needed
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        scroll_area.setWidget(self.table)
        table_layout.addWidget(scroll_area)
        
        main_layout.addWidget(table_container, stretch=1)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: #7f8c8d;
            padding: 8px;
            font-size: 12px;
            background-color: white;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_label)
    
    def safe_create_invoice(self):
        """Safely create invoice"""
        if self.is_closing:
            return
        if self.controller:
            self.controller.create_invoice()
    
    def update_statistics(self, invoices):
        """Update statistics cards with current data"""
        if self.is_closing:
            return
            
        if not invoices:
            self.total_revenue_card.update_value("₹0")
            self.paid_amount_card.update_value("₹0")
            self.pending_amount_card.update_value("₹0")
            self.total_invoices_card.update_value("0")
            self.overdue_card.update_value("0")
            return
        
        total_revenue = sum(inv.get('grand_total', 0) for inv in invoices)
        paid_amount = sum(inv.get('grand_total', 0) for inv in invoices if inv.get('status') == 'paid')
        pending_amount = sum(inv.get('grand_total', 0) for inv in invoices if inv.get('status') == 'pending')
        overdue_count = sum(1 for inv in invoices if inv.get('status') == 'overdue')
        
        self.total_revenue_card.update_value(f"₹{total_revenue:,.2f}")
        self.paid_amount_card.update_value(f"₹{paid_amount:,.2f}")
        self.pending_amount_card.update_value(f"₹{pending_amount:,.2f}")
        self.total_invoices_card.update_value(str(len(invoices)))
        self.overdue_card.update_value(str(overdue_count))
    
    def populate_table(self, invoices):
        """Populate table with invoice data and apply filters"""
        if self.is_closing:
            return
            
        # Apply filters
        filtered_invoices = self.filter_invoices(invoices)
        
        # Update statistics with filtered data
        self.update_statistics(filtered_invoices)
        
        # Populate table
        self.table.setRowCount(len(filtered_invoices))
        self.table.setSortingEnabled(False)  # Disable sorting during population
        
        for row, invoice in enumerate(filtered_invoices):
            # ID
            id_item = QTableWidgetItem(str(invoice['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Invoice Number
            inv_item = QTableWidgetItem(invoice.get('invoice_number', 'N/A'))
            inv_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 1, inv_item)
            
            # Customer Name
            customer_item = QTableWidgetItem(invoice.get('customer_name', 'N/A'))
            self.table.setItem(row, 2, customer_item)
            
            # Invoice Date
            date_str = invoice.get('invoice_date', '')[:10] if invoice.get('invoice_date') else 'N/A'
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, date_item)
            
            # Due Date
            due_date = invoice.get('due_date', '')[:10] if invoice.get('due_date') else 'N/A'
            due_item = QTableWidgetItem(due_date)
            due_item.setTextAlignment(Qt.AlignCenter)
            # Highlight if overdue
            if invoice.get('status') == 'overdue':
                due_item.setForeground(QColor("#e74c3c"))
                due_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 4, due_item)
            
            # Status with colored badge
            status = invoice.get('status', 'pending').lower()
            status_item = QTableWidgetItem(status.upper())
            status_item.setTextAlignment(Qt.AlignCenter)
            
            status_colors = {
                'paid': '#27ae60',
                'pending': '#f39c12',
                'overdue': '#e74c3c',
                'cancelled': '#95a5a6'
            }
            status_item.setForeground(QColor(status_colors.get(status, '#7f8c8d')))
            status_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.table.setItem(row, 5, status_item)
            
            # Total Amount
            total = invoice.get('grand_total', 0)
            total_item = QTableWidgetItem(f"₹{total:,.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if total > 10000:
                total_item.setForeground(QColor("#e74c3c"))
            elif total > 5000:
                total_item.setForeground(QColor("#f39c12"))
            else:
                total_item.setForeground(QColor("#27ae60"))
            self.table.setItem(row, 6, total_item)
            
            # Action buttons
            actions_widget = self.create_action_buttons(invoice['id'])
            self.table.setCellWidget(row, 7, actions_widget)
        
        self.table.setSortingEnabled(True)
        self.update_status(f"Showing {len(filtered_invoices)} of {len(invoices)} invoices")
    
    def create_action_buttons(self, invoice_id):
        """Create action buttons for table row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setFixedSize(35, 35)
        view_btn.setToolTip("View Invoice Details")
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        view_btn.clicked.connect(lambda checked, iid=invoice_id: self.safe_view_invoice(iid))
        
        # PDF button
        # pdf_btn = QPushButton("📄")
        # pdf_btn.setFixedSize(35, 35)
        # pdf_btn.setToolTip("Export as PDF")
        # pdf_btn.setCursor(Qt.PointingHandCursor)
        # pdf_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #27ae60;
        #         color: white;
        #         border: none;
        #         border-radius: 5px;
        #         font-size: 14px;
        #     }
        #     QPushButton:hover {
        #         background-color: #229954;
        #     }
        # """)
        # pdf_btn.clicked.connect(lambda checked, iid=invoice_id: self.export_pdf_direct(iid))
        
        # Email button
        email_btn = QPushButton("📧")
        email_btn.setFixedSize(35, 35)
        email_btn.setToolTip("Send via Email")
        email_btn.setCursor(Qt.PointingHandCursor)
        email_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        email_btn.clicked.connect(lambda checked, iid=invoice_id: self.safe_send_invoice_email(iid))
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(35, 35)
        delete_btn.setToolTip("Delete Invoice")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda checked, iid=invoice_id: self.safe_delete_invoice(iid))
        
        layout.addWidget(view_btn)
        # layout.addWidget(pdf_btn)
        layout.addWidget(email_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        
        return widget
    
    def safe_view_invoice(self, invoice_id):
        """Safely view invoice"""
        if self.is_closing:
            return
        if self.controller:
            self.controller.view_invoice(invoice_id)
    
    def safe_delete_invoice(self, invoice_id):
        """Safely delete invoice"""
        if self.is_closing:
            return
        if self.controller:
            self.controller.delete_invoice(invoice_id)
    
    def export_pdf_direct(self, invoice_id):
        """Direct PDF export with safety checks"""
        if self.is_closing:
            return
        
        # Disable the PDF button temporarily to prevent multiple clicks
        sender = self.sender()
        if sender:
            sender.setEnabled(False)
        
        try:
            self.update_status("Generating PDF...")
            QApplication.processEvents()  # Allow UI to update
            
            # Call the controller's export method directly
            if self.controller:
                self.controller.export_pdf(invoice_id)
            
            # Only update status if widget is still valid
            if self.isWidgetValid():
                self.update_status("PDF exported successfully")
                QMessageBox.information(self, "Success", "PDF exported successfully!")
        except Exception as e:
            # Only show error if widget is still valid
            if self.isWidgetValid():
                self.update_status(f"PDF export failed: {str(e)}")
                QMessageBox.warning(self, "Export Failed", f"Failed to export PDF: {str(e)}")
        finally:
            # Re-enable the button if it exists and widget is valid
            if sender and self.isWidgetValid():
                sender.setEnabled(True)
    
    def safe_send_invoice_email(self, invoice_id):
        """Safely send invoice email"""
        if self.is_closing:
            return
        
        if not self.controller:
            return
            
        # Find invoice details
        invoices = self.controller.model.get_all()
        invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
        
        if invoice and invoice.get('customer_email'):
            reply = QMessageBox.question(self, "Send Email", 
                                        f"Send invoice to {invoice.get('customer_email')}?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    from views.invoice_viewer import InvoiceViewer
                    viewer = InvoiceViewer(invoice, self.auth_service, self)
                    viewer.send_email_dialog()
                    self.update_status("Email sent successfully")
                except Exception as e:
                    self.update_status(f"Failed to send email: {str(e)}")
                    QMessageBox.warning(self, "Email Failed", f"Failed to send email: {str(e)}")
        else:
            QMessageBox.warning(self, "No Email", "Customer email not available")
    
    def filter_invoices(self, invoices):
        """Apply all filters to invoices"""
        if self.is_closing:
            return invoices
            
        filtered = invoices.copy()
        
        # Apply search filter
        search_text = self.search_box.text().lower()
        if search_text:
            filtered = [inv for inv in filtered if 
                       search_text in inv.get('invoice_number', '').lower() or
                       search_text in inv.get('customer_name', '').lower() or
                       search_text in inv.get('customer_email', '').lower()]
        
        # Apply status filter
        status = self.status_filter.currentText().lower()
        if status != "all":
            filtered = [inv for inv in filtered if inv.get('status', '').lower() == status]
        
        # Apply date range filter
        from_date = self.date_from.date().toPyDate()
        to_date = self.date_to.date().toPyDate()
        
        def parse_date(date_value):
            """Parse date from various formats"""
            if isinstance(date_value, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        return datetime.strptime(date_value[:10], fmt).date()
                    except:
                        continue
                return None
            elif hasattr(date_value, 'date'):  # datetime object
                return date_value.date() if hasattr(date_value, 'date') else date_value
            elif isinstance(date_value, QDate):
                return date_value.toPyDate()
            return None
        
        filtered_invoices = []
        for inv in filtered:
            inv_date = inv.get('invoice_date')
            if inv_date:
                parsed_date = parse_date(inv_date)
                if parsed_date and from_date <= parsed_date <= to_date:
                    filtered_invoices.append(inv)
            else:
                # If no date, include by default
                filtered_invoices.append(inv)
        
        return filtered_invoices
    
    def on_search(self, text):
        """Handle search text change"""
        if self.is_closing:
            return
        if self.controller and hasattr(self.controller, 'model'):
            invoices = self.controller.model.get_all()
            if invoices:
                self.populate_table(invoices)
    
    def on_filter_changed(self):
        """Handle filter changes"""
        if self.is_closing:
            return
        if self.controller and hasattr(self.controller, 'model'):
            invoices = self.controller.model.get_all()
            if invoices:
                self.populate_table(invoices)
    
    def export_data(self):
        """Export invoice data to CSV"""
        if self.is_closing:
            return
        
        if not self.controller:
            return
            
        invoices = self.controller.model.get_all()
        
        if not invoices:
            QMessageBox.warning(self, "No Data", "No invoices to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Invoices", 
                                                   f"invoices_{datetime.now().strftime('%Y%m%d')}.csv", 
                                                   "CSV Files (*.csv)")
        if file_path:
            try:
                filtered_invoices = self.filter_invoices(invoices)
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['id', 'invoice_number', 'customer_name', 'customer_email', 
                                'invoice_date', 'due_date', 'status', 'subtotal', 'tax', 'grand_total']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for invoice in filtered_invoices:
                        writer.writerow({
                            'id': invoice['id'],
                            'invoice_number': invoice.get('invoice_number', ''),
                            'customer_name': invoice.get('customer_name', ''),
                            'customer_email': invoice.get('customer_email', ''),
                            'invoice_date': invoice.get('invoice_date', ''),
                            'due_date': invoice.get('due_date', ''),
                            'status': invoice.get('status', ''),
                            'subtotal': invoice.get('subtotal', 0),
                            'tax': invoice.get('tax_total', 0),
                            'grand_total': invoice.get('grand_total', 0)
                        })
                QMessageBox.information(self, "Success", f"Exported {len(filtered_invoices)} invoices to {file_path}")
                self.update_status(f"Exported {len(filtered_invoices)} invoices")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def show_summary(self):
        """Show summary report dialog"""
        if self.is_closing:
            return
        
        if not self.controller:
            return
            
        invoices = self.controller.model.get_all()
        
        if not invoices:
            QMessageBox.warning(self, "No Data", "No invoice data available!")
            return
        
        filtered = self.filter_invoices(invoices)
        total = sum(inv.get('grand_total', 0) for inv in filtered)
        paid = sum(inv.get('grand_total', 0) for inv in filtered if inv.get('status') == 'paid')
        pending = sum(inv.get('grand_total', 0) for inv in filtered if inv.get('status') == 'pending')
        
        summary_text = f"""
        <div style="font-family: 'Segoe UI'; padding: 20px;">
            <h2 style="color: #9b59b6;">Invoice Summary Report</h2>
            <hr>
            <table style="width: 100%; font-size: 14px;">
                <tr><td><b>Total Invoices:</b></td><td style="color: #2c3e50;">{len(filtered)}</td></tr>
                <tr><td><b>Total Revenue:</b></td><td style="color: #27ae60;">₹{total:,.2f}</td></tr>
                <tr><td><b>Paid Amount:</b></td><td style="color: #27ae60;">₹{paid:,.2f}</td></tr>
                <tr><td><b>Pending Amount:</b></td><td style="color: #f39c12;">₹{pending:,.2f}</td></tr>
                <tr><td><b>Collection Rate:</b></td><td style="color: #3498db;">{ (paid/total*100) if total > 0 else 0:.1f}%</td></tr>
            </table>
        </div>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Invoice Summary")
        msg.setTextFormat(Qt.RichText)
        msg.setText(summary_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def update_status(self, message):
        """Update status bar message with safety check"""
        try:
            if not self.is_closing and self.status_label and not self.status_label.isHidden():
                self.status_label.setText(message)
                QApplication.processEvents()
        except (RuntimeError, AttributeError):
            # Widget has been deleted, ignore
            pass
    
    def refresh(self):
        """Refresh the invoice list"""
        if self.is_closing:
            return
        self.update_status("Refreshing invoices...")
        if self.controller:
            self.controller.load_invoices()
        self.update_status("Invoices refreshed successfully")