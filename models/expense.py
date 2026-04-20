from database.db_manager import DatabaseManager

class Expense:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, expense_date, category, description, amount, payment_method, receipt_number, vendor_name, created_by):
        query = """
            INSERT INTO expenses (expense_date, category, description, amount, 
                                 payment_method, receipt_number, vendor_name, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (expense_date, category, description, amount,
                                            payment_method, receipt_number, vendor_name, created_by))
    
    def update(self, expense_id, expense_date, category, description, amount, payment_method, receipt_number, vendor_name):
        query = """
            UPDATE expenses 
            SET expense_date=?, category=?, description=?, amount=?,
                payment_method=?, receipt_number=?, vendor_name=?
            WHERE id=?
        """
        return self.db.execute_query(query, (expense_date, category, description, amount,
                                            payment_method, receipt_number, vendor_name, expense_id))
    
    def delete(self, expense_id):
        query = "DELETE FROM expenses WHERE id=?"
        return self.db.execute_query(query, (expense_id,))
    
    def get_all(self, limit=100, offset=0):
        query = """
            SELECT e.*, u.username as created_by_name
            FROM expenses e
            LEFT JOIN users u ON e.created_by = u.id
            ORDER BY e.expense_date DESC
            LIMIT ? OFFSET ?
        """
        return self.db.fetch_all(query, (limit, offset))
    
    def get_by_id(self, expense_id):
        query = "SELECT * FROM expenses WHERE id=?"
        return self.db.fetch_one(query, (expense_id,))
    
    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for period"""
        query = "SELECT SUM(amount) as total FROM expenses"
        params = []
        
        if start_date and end_date:
            query += " WHERE expense_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        result = self.db.fetch_one(query, params)
        return result['total'] if result and result['total'] else 0
    
    def get_by_category(self, start_date=None, end_date=None):
        """Get expenses grouped by category"""
        query = """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE expense_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        query += " GROUP BY category ORDER BY total DESC"
        
        return self.db.fetch_all(query, params)