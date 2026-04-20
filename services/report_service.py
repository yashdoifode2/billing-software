from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import csv
from openpyxl import Workbook

class ReportService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_dashboard_stats(self):
        """Get complete dashboard statistics"""
        # Customer count
        customers = self.db.fetch_one("SELECT COUNT(*) as count FROM customers")
        
        # Product count
        products = self.db.fetch_one("SELECT COUNT(*) as count FROM products")
        
        # Invoice stats
        total_invoices = self.db.fetch_one("SELECT COUNT(*) as count FROM invoices")
        total_revenue = self.db.fetch_one("SELECT COALESCE(SUM(grand_total), 0) as total FROM invoices WHERE status='paid'")
        pending_amount = self.db.fetch_one("SELECT COALESCE(SUM(grand_total - paid_amount), 0) as pending FROM invoices WHERE status != 'paid'")
        
        # Expense total
        total_expenses = self.db.fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM expenses")
        
        # Recent activity
        recent_invoices = self.db.fetch_all("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC LIMIT 5
        """)
        
        # Monthly revenue for chart
        monthly_revenue = self.get_monthly_revenue()
        
        return {
            'total_customers': customers['count'] if customers else 0,
            'total_products': products['count'] if products else 0,
            'total_invoices': total_invoices['count'] if total_invoices else 0,
            'total_revenue': total_revenue['total'] if total_revenue else 0,
            'pending_amount': pending_amount['pending'] if pending_amount else 0,
            'total_expenses': total_expenses['total'] if total_expenses else 0,
            'recent_invoices': recent_invoices,
            'monthly_revenue': monthly_revenue
        }
    
    def get_monthly_revenue(self, months=6):
        """Get monthly revenue for last N months"""
        query = """
            SELECT strftime('%Y-%m', invoice_date) as month,
                   strftime('%b %Y', invoice_date) as month_name,
                   COALESCE(SUM(grand_total), 0) as total,
                   COUNT(*) as invoice_count
            FROM invoices
            WHERE status = 'paid'
            AND invoice_date >= date('now', ?)
            GROUP BY strftime('%Y-%m', invoice_date)
            ORDER BY month DESC
        """
        results = self.db.fetch_all(query, (f'-{months} months',))
        return list(reversed(results))
    
    def get_daily_revenue(self, days=30):
        """Get daily revenue for last N days"""
        query = """
            SELECT date(invoice_date) as day,
                   COALESCE(SUM(grand_total), 0) as total,
                   COUNT(*) as invoice_count
            FROM invoices
            WHERE status = 'paid'
            AND invoice_date >= date('now', ?)
            GROUP BY date(invoice_date)
            ORDER BY day DESC
        """
        return self.db.fetch_all(query, (f'-{days} days',))
    
    def get_tax_collection(self, start_date=None, end_date=None):
        """Get tax collection report"""
        query = """
            SELECT COALESCE(SUM(cgst_total), 0) as total_cgst,
                   COALESCE(SUM(sgst_total), 0) as total_sgst,
                   COALESCE(SUM(igst_total), 0) as total_igst,
                   COALESCE(SUM(tax_total), 0) as total_tax
            FROM invoices
            WHERE status = 'paid'
        """
        params = []
        
        if start_date and end_date:
            query += " AND invoice_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        result = self.db.fetch_one(query, params if params else None)
        return result if result else {'total_cgst': 0, 'total_sgst': 0, 'total_igst': 0, 'total_tax': 0}
    
    def get_outstanding_report(self):
        """Get outstanding invoices report"""
        query = """
            SELECT i.*, c.name as customer_name, c.phone, c.email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.status != 'paid' AND i.grand_total > i.paid_amount
            ORDER BY i.due_date ASC
        """
        return self.db.fetch_all(query)
    
    def get_profit_loss(self, start_date=None, end_date=None):
        """Get profit/loss statement"""
        # Revenue
        revenue_query = """
            SELECT COALESCE(SUM(grand_total), 0) as total_revenue
            FROM invoices
            WHERE status = 'paid'
        """
        # Expenses
        expense_query = """
            SELECT COALESCE(SUM(amount), 0) as total_expenses
            FROM expenses
        """
        params = []
        
        if start_date and end_date:
            revenue_query += " AND invoice_date BETWEEN ? AND ?"
            expense_query += " AND expense_date BETWEEN ? AND ?"
            params = [start_date, end_date, start_date, end_date]
        
        revenue = self.db.fetch_one(revenue_query, params[:2] if params else None)
        expenses = self.db.fetch_one(expense_query, params[2:] if params else None)
        
        revenue_total = revenue['total_revenue'] if revenue else 0
        expenses_total = expenses['total_expenses'] if expenses else 0
        
        return {
            'total_revenue': revenue_total,
            'total_expenses': expenses_total,
            'net_profit': revenue_total - expenses_total
        }
    
    def get_expense_by_category(self, start_date=None, end_date=None):
        """Get expenses grouped by category"""
        query = """
            SELECT category, 
                   COUNT(*) as count, 
                   COALESCE(SUM(amount), 0) as total
            FROM expenses
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE expense_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        query += " GROUP BY category ORDER BY total DESC"
        
        return self.db.fetch_all(query, params if params else None)
    
    def export_to_csv(self, data, filename, headers):
        """Export data to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        return filename
    
    def export_to_excel(self, data, filename, sheet_name="Report"):
        """Export data to Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            
            for row in data:
                ws.append(list(row.values()))
        
        wb.save(filename)
        return filename