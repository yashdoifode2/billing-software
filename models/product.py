from database.db_manager import DatabaseManager

class Product:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, name, description, price, cost_price, hsn_code, 
               tax_rate_cgst, tax_rate_sgst, tax_rate_igst, unit, stock_quantity):
        query = """
            INSERT INTO products (name, description, price, cost_price, hsn_code, 
                                 tax_rate_cgst, tax_rate_sgst, tax_rate_igst, unit, stock_quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, description, price, cost_price, hsn_code,
                                            tax_rate_cgst, tax_rate_sgst, tax_rate_igst, unit, stock_quantity))
    
    def update(self, product_id, name, description, price, cost_price, hsn_code,
               tax_rate_cgst, tax_rate_sgst, tax_rate_igst, unit, stock_quantity):
        query = """
            UPDATE products 
            SET name=?, description=?, price=?, cost_price=?, hsn_code=?,
                tax_rate_cgst=?, tax_rate_sgst=?, tax_rate_igst=?, unit=?, stock_quantity=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        return self.db.execute_query(query, (name, description, price, cost_price, hsn_code,
                                            tax_rate_cgst, tax_rate_sgst, tax_rate_igst, unit, 
                                            stock_quantity, product_id))
    
    def delete(self, product_id):
        query = "DELETE FROM products WHERE id=?"
        return self.db.execute_query(query, (product_id,))
    
    def get_all(self, limit=100, offset=0):
        query = "SELECT * FROM products ORDER BY name LIMIT ? OFFSET ?"
        return self.db.fetch_all(query, (limit, offset))
    
    def get_by_id(self, product_id):
        query = "SELECT * FROM products WHERE id=?"
        return self.db.fetch_one(query, (product_id,))
    
    def search(self, keyword):
        query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? OR hsn_code LIKE ?"
        keyword = f"%{keyword}%"
        return self.db.fetch_all(query, (keyword, keyword, keyword))
    
    def update_stock(self, product_id, quantity):
        """Update product stock quantity"""
        query = "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id=?"
        return self.db.execute_query(query, (quantity, product_id))