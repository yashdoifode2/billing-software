from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

class Invoice:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, customer_id, items, notes=""):
        """Create new invoice with items"""
        try:
            # Calculate totals
            subtotal = 0
            tax_total = 0
            
            for item in items:
                item_subtotal = item['quantity'] * item['unit_price']
                subtotal += item_subtotal
                tax_total += item.get('tax_amount', 0)
            
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
                INSERT INTO invoices (invoice_number, customer_id, subtotal, tax_total, grand_total, notes, due_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            invoice_id = self.db.execute_query(query, (
                invoice_number, customer_id, subtotal, tax_total, grand_total, notes, 
                due_date.strftime('%Y-%m-%d %H:%M:%S'), 'pending', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # Create invoice items
            for item in items:
                quantity = item['quantity']
                unit_price = item['unit_price']
                item_subtotal = quantity * unit_price
                
                cgst_rate = item.get('cgst_rate', 0)
                sgst_rate = item.get('sgst_rate', 0)
                igst_rate = item.get('igst_rate', 0)
                cgst_amount = item.get('cgst_amount', 0)
                sgst_amount = item.get('sgst_amount', 0)
                igst_amount = item.get('igst_amount', 0)
                tax_amount = item.get('tax_amount', 0)
                item_total = item_subtotal + tax_amount
                
                item_query = """
                    INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, 
                                             cgst_rate, sgst_rate, igst_rate,
                                             cgst_amount, sgst_amount, igst_amount, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute_query(item_query, (
                    invoice_id, item['product_id'], quantity, unit_price,
                    cgst_rate, sgst_rate, igst_rate,
                    cgst_amount, sgst_amount, igst_amount, item_total
                ))
            
            return invoice_id
            
        except Exception as e:
            print(f"Error creating invoice: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_status(self, invoice_id, status):
        """Update invoice status"""
        query = "UPDATE invoices SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.execute_query(query, (status, invoice_id))
    
    def update_payment_status(self, invoice_id, paid_amount):
        """Update payment status and amount"""
        invoice = self.get_by_id(invoice_id)
        if invoice:
            new_paid = invoice.get('paid_amount', 0) + paid_amount
            payment_status = 'paid' if new_paid >= invoice['grand_total'] else 'partial'
            invoice_status = 'paid' if payment_status == 'paid' else invoice.get('status', 'pending')
            
            query = """
                UPDATE invoices 
                SET paid_amount = ?, payment_status = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            return self.db.execute_query(query, (new_paid, payment_status, invoice_status, invoice_id))
        return None
    
    def get_all(self, limit=100, offset=0):
        query = """
            SELECT i.*, c.name as customer_name, c.phone, c.email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT ? OFFSET ?
        """
        return self.db.fetch_all(query, (limit, offset))
    
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
                SELECT ii.*, p.name as product_name, p.description, p.hsn_code
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
        self.db.execute_query("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        query = "DELETE FROM invoices WHERE id=?"
        return self.db.execute_query(query, (invoice_id,))
    
    def get_dashboard_stats(self):
        total_invoices = self.db.fetch_one("SELECT COUNT(*) as count FROM invoices")
        total_revenue = self.db.fetch_one("SELECT COALESCE(SUM(grand_total), 0) as total FROM invoices WHERE status='paid'")
        pending = self.db.fetch_one("SELECT COALESCE(SUM(grand_total - paid_amount), 0) as pending FROM invoices WHERE status != 'paid'")
        
        recent_invoices = self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC LIMIT 5
        """)
        
        return {
            'total_invoices': total_invoices['count'] if total_invoices else 0,
            'total_revenue': total_revenue['total'] if total_revenue else 0,
            'pending_amount': pending['pending'] if pending else 0,
            'recent_invoices': recent_invoices
        }
    
    def get_recent_invoices(self, limit=10):
        return self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC LIMIT ?
        """, (limit,))