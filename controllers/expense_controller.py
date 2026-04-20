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
        QMessageBox.information(self.view, "Info", "Add expense feature coming soon!")
    
    def edit_expense(self, expense_id):
        QMessageBox.information(self.view, "Info", "Edit expense feature coming soon!")
    
    def delete_expense(self, expense_id):
        QMessageBox.information(self.view, "Info", "Delete expense feature coming soon!")