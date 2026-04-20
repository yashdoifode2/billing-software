from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
from services.tax_service import TaxService

class Invoice:
    def __init__(self):
        self.db = DatabaseManager()
        self.tax_service = TaxService()
    
    def create(self, customer_id, items, notes="", terms=""):
        """Create new invoice with items"""
        subtotal = sum(item['subtotal'] for item in items)
        cgst_total = sum(item.get('cgst_amount', 0) for item in items)
        sgst_total = sum(item.get('sgst_amount', 0) for item in items)
        igst_total = sum(item.get('igst_amount', 0) for item in items)
        tax_total = cgst_total + sgst_total + igst_total
        grand_total = subtotal + tax_total
        
        # Get next invoice number
        settings = self.get_settings()
        prefix = settings.get('invoice_prefix', 'INV')
        last_invoice = self.get_last_invoice_number()
        if last_invoice:
            try:
                num = int(last_invoice.split('-')[-1]) + 1
            except:
                num = 1
        else:
            num = 1
        invoice_number = f"{prefix}-{num:04d}"
        
        # Due date (default 30 days)
        due_date = datetime.now() + timedelta(days=30)
        
        # Create invoice
        query = """
            INSERT INTO invoices (invoice_number, customer_id, subtotal, cgst_total, sgst_total, 
                                 igst_total, tax_total, grand_total, notes, terms, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        invoice_id = self.db.execute_query(query, (
            invoice_number, customer_id, subtotal, cgst_total, sgst_total, 
            igst_total, tax_total, grand_total, notes, terms, due_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Create invoice items
        for item in items:
            item_query = """
                INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, 
                                         cgst_rate, sgst_rate, igst_rate,
                                         cgst_amount, sgst_amount, igst_amount, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute_query(item_query, (
                invoice_id, item['product_id'], item['quantity'], item['unit_price'],
                item.get('cgst_rate', 0), item.get('sgst_rate', 0), item.get('igst_rate', 0),
                item.get('cgst_amount', 0), item.get('sgst_amount', 0), item.get('igst_amount', 0),
                item['total']
            ))
        
        return invoice_id
    
    def get_all(self, limit=100, offset=0):
        """Get all invoices with pagination"""
        query = """
            SELECT i.*, c.name as customer_name, c.phone, c.email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.invoice_date DESC
            LIMIT ? OFFSET ?
        """
        return self.db.fetch_all(query, (limit, offset))
    
    def get_by_id(self, invoice_id):
        """Get invoice by ID with items"""
        query = """
            SELECT i.*, c.name as customer_name, c.address, c.gst_number, c.pan_number, c.phone, c.email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """
        invoice = self.db.fetch_one(query, (invoice_id,))
        if invoice:
            items_query = """
                SELECT ii.*, p.name as product_name, p.description, p.hsn_code
                FROM invoice_items ii
                LEFT JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
            """
            invoice['items'] = self.db.fetch_all(items_query, (invoice_id,))
            
            # Get payments
            payments_query = "SELECT * FROM invoice_payments WHERE invoice_id = ? ORDER BY payment_date DESC"
            invoice['payments'] = self.db.fetch_all(payments_query, (invoice_id,))
        return invoice
    
    def get_last_invoice_number(self):
        """Get last invoice number"""
        query = "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
        result = self.db.fetch_one(query)
        return result['invoice_number'] if result else None
    
    def get_settings(self):
        """Get system settings"""
        query = "SELECT setting_key, setting_value FROM settings"
        results = self.db.fetch_all(query)
        return {item['setting_key']: item['setting_value'] for item in results}
    
    def delete(self, invoice_id):
        """Delete invoice"""
        # First delete items
        self.db.execute_query("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        # Then delete invoice
        query = "DELETE FROM invoices WHERE id=?"
        return self.db.execute_query(query, (invoice_id,))
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        # Total invoices
        total_invoices = self.db.fetch_one("SELECT COUNT(*) as count FROM invoices")
        
        # Total revenue (paid invoices)
        total_revenue = self.db.fetch_one("SELECT SUM(grand_total) as total FROM invoices WHERE status='paid'")
        
        # Pending amount
        pending = self.db.fetch_one("SELECT SUM(grand_total - paid_amount) as pending FROM invoices WHERE status != 'paid'")
        
        # Recent invoices
        recent_invoices = self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.invoice_date DESC LIMIT 10
        """)
        
        return {
            'total_invoices': total_invoices['count'] if total_invoices else 0,
            'total_revenue': total_revenue['total'] if total_revenue and total_revenue['total'] else 0,
            'pending_amount': pending['pending'] if pending and pending['pending'] else 0,
            'recent_invoices': recent_invoices
        }
    
    def get_recent_invoices(self, limit=10):
        """Get recent invoices"""
        return self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.invoice_date DESC LIMIT ?
        """, (limit,))
    
    def record_payment(self, invoice_id, amount, payment_method, reference_number="", notes=""):
        """Record payment for invoice"""
        # Get current invoice
        invoice = self.get_by_id(invoice_id)
        if not invoice:
            return False
        
        new_paid = invoice['paid_amount'] + amount
        status = 'paid' if new_paid >= invoice['grand_total'] else 'partial'
        
        # Record payment
        query = """
            INSERT INTO invoice_payments (invoice_id, amount, payment_method, reference_number, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (invoice_id, amount, payment_method, reference_number, notes))
        
        # Update invoice
        update_query = """
            UPDATE invoices 
            SET paid_amount = ?, status = ?, payment_status = ?
            WHERE id = ?
        """
        self.db.execute_query(update_query, (new_paid, status, 'partial' if status == 'partial' else 'paid', invoice_id))
        
        return True