from models.invoice import Invoice
from utils.pdf_generator import PDFGenerator
from controllers.settings_controller import SettingsController
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QDesktopServices
import sys
import os
import sip

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def is_widget_valid(widget):
    """Check if widget exists and hasn't been deleted"""
    return widget is not None and not sip.isdeleted(widget)

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
        if is_widget_valid(self.view):
            self.view.populate_table(invoices)
    
    def create_invoice(self):
        from views.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog()
        if dialog.exec_():
            self.load_invoices()
    
    def view_invoice(self, invoice_id):
        invoice = self.model.get_by_id(invoice_id)
        if invoice:
            from views.invoice_viewer import InvoiceViewer
            viewer = InvoiceViewer(invoice, self.auth_service)
            viewer.exec_()
            self.load_invoices()
    
    def export_pdf(self, invoice_id):
        """Export invoice to PDF with logo and bank details"""
        try:
            invoice = self.model.get_by_id(invoice_id)
            if not invoice:
                if is_widget_valid(self.view):
                    QMessageBox.warning(self.view, "Error", "Invoice not found!")
                return
            
            # Get settings with logo and bank details
            settings = self.settings_controller.get_settings()
            
            # Ask for save location
            parent_widget = self.view if is_widget_valid(self.view) else None
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, 
                "Save PDF", 
                f"Invoice_{invoice['invoice_number']}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Generate PDF with full features
                pdf_gen = PDFGenerator(invoice, settings)
                pdf_gen.generate(file_path)
                
                # Use QTimer to ensure widget is still valid when showing dialogs
                if is_widget_valid(self.view):
                    QTimer.singleShot(0, lambda: self._show_pdf_success(file_path))
                
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            import traceback
            traceback.print_exc()
            if is_widget_valid(self.view):
                QTimer.singleShot(0, lambda: self._show_pdf_error(str(e)))
    
    def _show_pdf_success(self, file_path):
        """Show success message after PDF export"""
        if is_widget_valid(self.view):
            QMessageBox.information(self.view, "Success", f"PDF exported successfully!\nLocation: {file_path}")
            
            # Ask to open PDF
            reply = QMessageBox.question(self.view, "Open PDF", 
                                        "PDF created successfully! Would you like to open it?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
    
    def _show_pdf_error(self, error_msg):
        """Show error message for PDF export"""
        if is_widget_valid(self.view):
            QMessageBox.critical(self.view, "Error", f"Failed to export PDF: {error_msg}")
    
    def delete_invoice(self, invoice_id):
        if not is_widget_valid(self.view):
            return
            
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this invoice?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(invoice_id)
            self.load_invoices()
            QMessageBox.information(self.view, "Success", "Invoice deleted successfully!")
    
    def search_invoices(self, keyword):
        if not is_widget_valid(self.view):
            return
            
        if keyword and keyword.strip():
            invoices = self.model.get_all()
            filtered = [inv for inv in invoices if 
                       keyword.lower() in inv['invoice_number'].lower() or
                       keyword.lower() in inv.get('customer_name', '').lower()]
            self.view.populate_table(filtered)
        else:
            self.load_invoices()