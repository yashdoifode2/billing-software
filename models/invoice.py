from database.db_manager import DatabaseManager
from datetime import datetime

class Invoice:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, customer_id, items, notes=""):
        """Create new invoice with items"""
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        tax_total = sum(item['quantity'] * item['unit_price'] * item['tax_rate'] / 100 for item in items)
        grand_total = subtotal + tax_total
        
        # Get next invoice number
        settings = self.get_settings()
        prefix = settings.get('invoice_prefix', 'INV')
        last_invoice = self.get_last_invoice_number()
        if last_invoice:
            num = int(last_invoice.split('-')[-1]) + 1
        else:
            num = 1
        invoice_number = f"{prefix}-{num:04d}"
        
        # Create invoice
        query = """
            INSERT INTO invoices (invoice_number, customer_id, subtotal, tax_total, grand_total, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        invoice_id = self.db.execute_query(query, (invoice_number, customer_id, subtotal, tax_total, grand_total, notes))
        
        # Create invoice items
        for item in items:
            item_query = """
                INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, tax_rate, total)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            item_total = item['quantity'] * item['unit_price'] * (1 + item['tax_rate'] / 100)
            self.db.execute_query(item_query, (invoice_id, item['product_id'], item['quantity'], 
                                              item['unit_price'], item['tax_rate'], item_total))
        
        return invoice_id
    
    def get_all(self):
        query = """
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.invoice_date DESC
        """
        return self.db.fetch_all(query)
    
    def get_by_id(self, invoice_id):
        query = """
            SELECT i.*, c.name as customer_name, c.address, c.gst_number, c.phone, c.email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """
        invoice = self.db.fetch_one(query, (invoice_id,))
        if invoice:
            items_query = """
                SELECT ii.*, p.name as product_name, p.description
                FROM invoice_items ii
                LEFT JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
            """
            invoice['items'] = self.db.fetch_all(items_query, (invoice_id,))
        return invoice
    
    def get_last_invoice_number(self):
        query = "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
        result = self.db.fetch_one(query)
        return result['invoice_number'] if result else None
    
    def get_settings(self):
        query = "SELECT setting_key, setting_value FROM settings"
        results = self.db.fetch_all(query)
        return {item['setting_key']: item['setting_value'] for item in results}
    
    def delete(self, invoice_id):
        query = "DELETE FROM invoices WHERE id=?"
        return self.db.execute_query(query, (invoice_id,))
    
    def get_dashboard_stats(self):
        # Total invoices
        total_invoices = self.db.fetch_one("SELECT COUNT(*) as count FROM invoices")
        
        # Total revenue
        total_revenue = self.db.fetch_one("SELECT SUM(grand_total) as total FROM invoices WHERE status='paid'")
        
        # Recent invoices
        recent_invoices = self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.invoice_date DESC LIMIT 5
        """)
        
        return {
            'total_invoices': total_invoices['count'] if total_invoices else 0,
            'total_revenue': total_revenue['total'] if total_revenue and total_revenue['total'] else 0,
            'recent_invoices': recent_invoices
        }