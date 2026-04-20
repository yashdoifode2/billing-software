from database.db_manager import DatabaseManager

class Customer:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, name, phone, email, address, gst_number):
        query = """
            INSERT INTO customers (name, phone, email, address, gst_number)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, phone, email, address, gst_number))
    
    def update(self, customer_id, name, phone, email, address, gst_number):
        query = """
            UPDATE customers 
            SET name=?, phone=?, email=?, address=?, gst_number=?
            WHERE id=?
        """
        return self.db.execute_query(query, (name, phone, email, address, gst_number, customer_id))
    
    def delete(self, customer_id):
        query = "DELETE FROM customers WHERE id=?"
        return self.db.execute_query(query, (customer_id,))
    
    def get_all(self):
        query = "SELECT * FROM customers ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_by_id(self, customer_id):
        query = "SELECT * FROM customers WHERE id=?"
        return self.db.fetch_one(query, (customer_id,))
    
    def search(self, keyword):
        query = "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?"
        keyword = f"%{keyword}%"
        return self.db.fetch_all(query, (keyword, keyword, keyword))