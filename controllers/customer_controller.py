from models.customer import Customer
from PyQt5.QtWidgets import QMessageBox

class CustomerController:
    def __init__(self, view):
        self.view = view
        self.model = Customer()
        # Don't load customers here, let the view call it
    
    def load_customers(self):
        print("Loading customers...")
        customers = self.model.get_all()
        if customers is None:
            customers = []
        self.view.populate_table(customers)
    
    def add_customer(self):
        print("Add customer button clicked")
        from views.customer_dialog import CustomerDialog
        dialog = CustomerDialog()
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                print(f"Creating customer: {data}")
                self.model.create(data['name'], data['phone'], data['email'], 
                                data['address'], data['gst_number'])
                self.load_customers()
                QMessageBox.information(self.view, "Success", "Customer added successfully!")
    
    def edit_customer(self, customer_id):
        print(f"Edit customer: {customer_id}")
        customer = self.model.get_by_id(customer_id)
        if customer:
            from views.customer_dialog import CustomerDialog
            dialog = CustomerDialog(customer)
            if dialog.exec_():
                data = dialog.get_data()
                if data:
                    self.model.update(customer_id, data['name'], data['phone'], 
                                    data['email'], data['address'], data['gst_number'])
                    self.load_customers()
                    QMessageBox.information(self.view, "Success", "Customer updated successfully!")
    
    def delete_customer(self, customer_id):
        print(f"Delete customer: {customer_id}")
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this customer?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(customer_id)
            self.load_customers()
            QMessageBox.information(self.view, "Success", "Customer deleted successfully!")
    
    def search_customers(self, keyword):
        print(f"Searching customers: {keyword}")
        if keyword and keyword.strip():
            customers = self.model.search(keyword)
        else:
            customers = self.model.get_all()
        if customers is None:
            customers = []
        self.view.populate_table(customers)