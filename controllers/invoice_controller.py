from models.invoice import Invoice
from utils.pdf_generator import PDFGenerator
from controllers.settings_controller import SettingsController
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
        self.settings_controller = SettingsController()
    
    def load_invoices(self):
        invoices = self.model.get_all()
        if invoices is None:
            invoices = []
        self.view.populate_table(invoices)
    
    def create_invoice(self):
        from views.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog()
        if dialog.exec_():
            self.load_invoices()
            # Success message is already shown in the dialog, so don't show duplicate
            # QMessageBox.information(self.view, "Success", "Invoice created successfully!")
    
    def view_invoice(self, invoice_id):
        invoice = self.model.get_by_id(invoice_id)
        if invoice:
            from views.invoice_viewer import InvoiceViewer
            viewer = InvoiceViewer(invoice, self.auth_service)
            viewer.exec_()
            self.load_invoices()  # Refresh after potential status changes
    
    def export_pdf(self, invoice_id):
        try:
            invoice = self.model.get_by_id(invoice_id)
            if not invoice:
                QMessageBox.warning(self.view, "Error", "Invoice not found!")
                return
            
            settings = self.settings_controller.get_settings()
            
            file_path, _ = QFileDialog.getSaveFileName(
                self.view, 
                "Save PDF", 
                f"Invoice_{invoice['invoice_number']}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                pdf_gen = PDFGenerator(invoice, settings)
                pdf_gen.generate(file_path)
                
                QMessageBox.information(self.view, "Success", f"PDF exported successfully!\nLocation: {file_path}")
                
                reply = QMessageBox.question(self.view, "Open PDF", 
                                            "PDF created successfully! Would you like to open it?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to export PDF: {str(e)}")
    
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