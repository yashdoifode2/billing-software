from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QTextEdit, QPushButton, QDoubleSpinBox, 
                             QMessageBox, QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate

class ExpenseDialog(QDialog):
    def __init__(self, expense=None, parent=None):
        super().__init__(parent)
        self.expense = expense
        self.setup_ui()
        if expense:
            self.setWindowTitle("Edit Expense")
            self.load_data()
        else:
            self.setWindowTitle("Add Expense")
        self.setModal(True)
        self.resize(500, 500)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Rent", "Utilities", "Salary", "Travel", "Office Supplies",
            "Marketing", "Maintenance", "Insurance", "Taxes", "Other"
        ])
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setDecimals(2)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Bank Transfer", "Cheque", "Credit Card", "UPI"])
        
        self.receipt_input = QLineEdit()
        self.vendor_input = QLineEdit()
        
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("Payment Method:", self.payment_combo)
        form_layout.addRow("Receipt Number:", self.receipt_input)
        form_layout.addRow("Vendor Name:", self.vendor_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Expense")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        self.date_input.setDate(QDate.fromString(self.expense['expense_date'], "yyyy-MM-dd"))
        
        index = self.category_combo.findText(self.expense['category'])
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.description_input.setText(self.expense.get('description', ''))
        self.amount_input.setValue(self.expense['amount'])
        
        index = self.payment_combo.findText(self.expense.get('payment_method', ''))
        if index >= 0:
            self.payment_combo.setCurrentIndex(index)
        
        self.receipt_input.setText(self.expense.get('receipt_number', ''))
        self.vendor_input.setText(self.expense.get('vendor_name', ''))
    
    def get_data(self):
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0!")
            return None
        
        return {
            'expense_date': self.date_input.date().toString("yyyy-MM-dd"),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip(),
            'amount': self.amount_input.value(),
            'payment_method': self.payment_combo.currentText(),
            'receipt_number': self.receipt_input.text().strip(),
            'vendor_name': self.vendor_input.text().strip()
        }
    
    def accept(self):
        if self.get_data():
            super().accept()