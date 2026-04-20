from models.invoice import Invoice
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
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
        from views.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog()
        result = dialog.exec_()
        if result:
            self.load_invoices()
            QMessageBox.information(self.view, "Success", "Invoice created successfully!")
    
    def view_invoice(self, invoice_id):
        invoice = self.model.get_by_id(invoice_id)
        if invoice:
            from views.invoice_viewer import InvoiceViewer
            viewer = InvoiceViewer(invoice, self.auth_service)
            viewer.exec_()
    
    def export_pdf(self, invoice_id):
        QMessageBox.information(self.view, "Info", "PDF export feature coming soon!")
    
    def delete_invoice(self, invoice_id):
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this invoice?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(invoice_id)
            self.load_invoices()
            QMessageBox.information(self.view, "Success", "Invoice deleted successfully!")
    
    def search_invoices(self, keyword):
        if keyword and keyword.strip():
            invoices = self.model.get_all()
            filtered = [inv for inv in invoices if 
                       keyword.lower() in inv['invoice_number'].lower() or
                       keyword.lower() in inv.get('customer_name', '').lower()]
            self.view.populate_table(filtered)
        else:
            self.load_invoices()