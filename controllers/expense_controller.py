from models.expense import Expense
from PyQt5.QtWidgets import QMessageBox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ExpenseController:
    def __init__(self, view, auth_service):
        self.view = view
        self.auth_service = auth_service
        self.model = Expense()
    
    def load_expenses(self):
        expenses = self.model.get_all()
        if expenses is None:
            expenses = []
        self.view.populate_table(expenses)
    
    def add_expense(self):
        from views.expense_dialog import ExpenseDialog
        dialog = ExpenseDialog()
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                self.model.create(
                    data['expense_date'], data['category'], data['description'],
                    data['amount'], data['payment_method'], data['receipt_number'],
                    data['vendor_name'], self.auth_service.current_user['id']
                )
                self.load_expenses()
                QMessageBox.information(self.view, "Success", "Expense added successfully!")
    
    def edit_expense(self, expense_id):
        expense = self.model.get_by_id(expense_id)
        if expense:
            from views.expense_dialog import ExpenseDialog
            dialog = ExpenseDialog(expense)
            if dialog.exec_():
                data = dialog.get_data()
                if data:
                    self.model.update(
                        expense_id, data['expense_date'], data['category'],
                        data['description'], data['amount'], data['payment_method'],
                        data['receipt_number'], data['vendor_name']
                    )
                    self.load_expenses()
                    QMessageBox.information(self.view, "Success", "Expense updated successfully!")
    
    def delete_expense(self, expense_id):
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this expense?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(expense_id)
            self.load_expenses()
            QMessageBox.information(self.view, "Success", "Expense deleted successfully!")