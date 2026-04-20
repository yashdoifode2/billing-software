from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import csv
import json
from openpyxl import Workbook

class ReportService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_monthly_revenue(self, months=12):
        """Get monthly revenue for last N months"""
        query = """
            SELECT strftime('%Y-%m', invoice_date) as month,
                   SUM(grand_total) as total,
                   COUNT(*) as invoice_count
            FROM invoices
            WHERE status = 'paid'
            AND invoice_date >= date('now', ?)
            GROUP BY strftime('%Y-%m', invoice_date)
            ORDER BY month DESC
            LIMIT ?
        """
        results = self.db.fetch_all(query, (f'-{months} months', months))
        return list(reversed(results))
    
    def get_daily_revenue(self, days=30):
        """Get daily revenue for last N days"""
        query = """
            SELECT date(invoice_date) as day,
                   SUM(grand_total) as total,
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
            SELECT SUM(cgst_total) as total_cgst,
                   SUM(sgst_total) as total_sgst,
                   SUM(igst_total) as total_igst,
                   SUM(tax_total) as total_tax
            FROM invoices
            WHERE status = 'paid'
        """
        params = []
        
        if start_date and end_date:
            query += " AND invoice_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        return self.db.fetch_one(query, params)
    
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
            SELECT SUM(grand_total) as total_revenue
            FROM invoices
            WHERE status = 'paid'
        """
        # Expenses
        expense_query = """
            SELECT SUM(amount) as total_expenses
            FROM expenses
        """
        params = []
        
        if start_date and end_date:
            revenue_query += " AND invoice_date BETWEEN ? AND ?"
            expense_query += " AND expense_date BETWEEN ? AND ?"
            params = [start_date, end_date, start_date, end_date]
        
        revenue = self.db.fetch_one(revenue_query, params[:2] if params else None)
        expenses = self.db.fetch_one(expense_query, params[2:] if params else None)
        
        revenue_total = revenue['total_revenue'] if revenue and revenue['total_revenue'] else 0
        expenses_total = expenses['total_expenses'] if expenses and expenses['total_expenses'] else 0
        
        return {
            'total_revenue': revenue_total,
            'total_expenses': expenses_total,
            'net_profit': revenue_total - expenses_total
        }
    
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
            # Write headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Write data
            for row in data:
                ws.append(list(row.values()))
        
        wb.save(filename)
        return filename