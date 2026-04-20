from models.invoice import Invoice
from utils.pdf_generator import PDFGenerator
from controllers.settings_controller import SettingsController
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import os

class InvoiceController:
    def __init__(self, view):
        self.view = view
        self.model = Invoice()
        self.settings = SettingsController()
    
    def load_invoices(self):
        print("Loading invoices...")
        invoices = self.model.get_all()
        if invoices is None:
            invoices = []
        self.view.populate_table(invoices)
    
    def create_invoice(self):
        print("Create invoice button clicked")
        from views.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog()
        if dialog.exec_():
            data = dialog.get_invoice_data()
            if data:
                print(f"Creating invoice with data: {data}")
                invoice_id = self.model.create(data['customer_id'], data['items'], data['notes'])
                if invoice_id:
                    self.load_invoices()
                    QMessageBox.information(self.view, "Success", f"Invoice created successfully!")
                    reply = QMessageBox.question(self.view, "Export PDF", 
                                                "Would you like to export this invoice as PDF?",
                                                QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.export_pdf(invoice_id)
    
    def view_invoice(self, invoice_id):
        print(f"View invoice: {invoice_id}")
        invoice = self.model.get_by_id(invoice_id)
        if invoice:
            from views.invoice_viewer import InvoiceViewer
            viewer = InvoiceViewer(invoice)
            viewer.exec_()
    
    def export_pdf(self, invoice_id):
        print(f"Export PDF for invoice: {invoice_id}")
        invoice = self.model.get_by_id(invoice_id)
        if not invoice:
            QMessageBox.warning(self.view, "Error", "Invoice not found!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self.view, "Save PDF", 
                                                   f"Invoice_{invoice['invoice_number']}.pdf",
                                                   "PDF Files (*.pdf)")
        if file_path:
            settings = self.settings.get_settings()
            pdf_gen = PDFGenerator(invoice, settings)
            pdf_gen.generate(file_path)
            QMessageBox.information(self.view, "Success", f"PDF exported to {file_path}")
            
            # Option to open PDF
            reply = QMessageBox.question(self.view, "Open PDF", 
                                        "PDF created successfully! Would you like to open it?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
    
    def delete_invoice(self, invoice_id):
        print(f"Delete invoice: {invoice_id}")
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this invoice?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(invoice_id)
            self.load_invoices()
            QMessageBox.information(self.view, "Success", "Invoice deleted successfully!")
    
    def search_invoices(self, keyword):
        print(f"Searching invoices: {keyword}")
        if keyword and keyword.strip():
            invoices = self.model.get_all()
            # Simple search filter
            filtered = [inv for inv in invoices if 
                       keyword.lower() in inv['invoice_number'].lower() or
                       keyword.lower() in inv.get('customer_name', '').lower()]
            self.view.populate_table(filtered)
        else:
            self.load_invoices()