from models.product import Product
from PyQt5.QtWidgets import QMessageBox

class ProductController:
    def __init__(self, view):
        self.view = view
        self.model = Product()
    
    def load_products(self):
        print("Loading products...")
        products = self.model.get_all()
        if products is None:
            products = []
        self.view.populate_table(products)
    
    def add_product(self):
        print("Add product button clicked")
        from views.product_dialog import ProductDialog
        dialog = ProductDialog()
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                print(f"Creating product: {data}")
                self.model.create(data['name'], data['description'], data['price'], data['tax_rate'])
                self.load_products()
                QMessageBox.information(self.view, "Success", "Product added successfully!")
    
    def edit_product(self, product_id):
        print(f"Edit product: {product_id}")
        product = self.model.get_by_id(product_id)
        if product:
            from views.product_dialog import ProductDialog
            dialog = ProductDialog(product)
            if dialog.exec_():
                data = dialog.get_data()
                if data:
                    self.model.update(product_id, data['name'], data['description'], data['price'], data['tax_rate'])
                    self.load_products()
                    QMessageBox.information(self.view, "Success", "Product updated successfully!")
    
    def delete_product(self, product_id):
        print(f"Delete product: {product_id}")
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this product?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(product_id)
            self.load_products()
            QMessageBox.information(self.view, "Success", "Product deleted successfully!")
    
    def search_products(self, keyword):
        print(f"Searching products: {keyword}")
        if keyword and keyword.strip():
            products = self.model.search(keyword)
        else:
            products = self.model.get_all()
        if products is None:
            products = []
        self.view.populate_table(products)