from models.invoice import Invoice
from PyQt5.QtWidgets import QMessageBox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InvoiceController:
    def __init__(self, view, auth_service):
        self.view = view
        self.auth_service = auth_service
        self.model = Invoice()
    
    def load_invoices(self):
        invoices = self.model.get_all()
        if invoices is None:
            invoices = []
        self.view.populate_table(invoices)
    
    def create_invoice(self):
        QMessageBox.information(self.view, "Info", "Invoice creation feature coming soon!")
    
    def view_invoice(self, invoice_id):
        QMessageBox.information(self.view, "Info", "Invoice view feature coming soon!")
    
    def search_invoices(self, keyword):
        if keyword and keyword.strip():
            invoices = self.model.get_all()
            filtered = [inv for inv in invoices if 
                       keyword.lower() in inv['invoice_number'].lower() or
                       keyword.lower() in inv.get('customer_name', '').lower()]
            self.view.populate_table(filtered)
        else:
            self.load_invoices()