from models.customer import Customer
from PyQt5.QtWidgets import QMessageBox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CustomerController:
    def __init__(self, view, auth_service):
        self.view = view
        self.auth_service = auth_service
        self.model = Customer()
    
    def load_customers(self):
        customers = self.model.get_all()
        if customers is None:
            customers = []
        self.view.populate_table(customers)
    
    def add_customer(self):
        from views.customer_dialog import CustomerDialog
        dialog = CustomerDialog()
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                self.model.create(data['name'], data['phone'], data['email'], 
                                data['address'], data.get('gst_number', ''))
                self.load_customers()
                QMessageBox.information(self.view, "Success", "Customer added successfully!")
    
    def edit_customer(self, customer_id):
        customer = self.model.get_by_id(customer_id)
        if customer:
            from views.customer_dialog import CustomerDialog
            dialog = CustomerDialog(customer)
            if dialog.exec_():
                data = dialog.get_data()
                if data:
                    self.model.update(customer_id, data['name'], data['phone'], 
                                    data['email'], data['address'], data.get('gst_number', ''))
                    self.load_customers()
                    QMessageBox.information(self.view, "Success", "Customer updated successfully!")
    
    def delete_customer(self, customer_id):
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this customer?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(customer_id)
            self.load_customers()
            QMessageBox.information(self.view, "Success", "Customer deleted successfully!")
    
    def search_customers(self, keyword):
        if keyword and keyword.strip():
            customers = self.model.search(keyword)
        else:
            customers = self.model.get_all()
        if customers is None:
            customers = []
        self.view.populate_table(customers)