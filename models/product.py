from database.db_manager import DatabaseManager

class Product:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, name, description, price, tax_rate):
        query = """
            INSERT INTO products (name, description, price, tax_rate)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, description, price, tax_rate))
    
    def update(self, product_id, name, description, price, tax_rate):
        query = """
            UPDATE products 
            SET name=?, description=?, price=?, tax_rate=?
            WHERE id=?
        """
        return self.db.execute_query(query, (name, description, price, tax_rate, product_id))
    
    def delete(self, product_id):
        query = "DELETE FROM products WHERE id=?"
        return self.db.execute_query(query, (product_id,))
    
    def get_all(self):
        query = "SELECT * FROM products ORDER BY name"
        return self.db.fetch_all(query)
    
    def get_by_id(self, product_id):
        query = "SELECT * FROM products WHERE id=?"
        return self.db.fetch_one(query, (product_id,))
    
    def search(self, keyword):
        query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
        keyword = f"%{keyword}%"
        return self.db.fetch_all(query, (keyword, keyword))