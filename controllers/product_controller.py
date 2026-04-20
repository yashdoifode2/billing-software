from models.product import Product
from PyQt5.QtWidgets import QMessageBox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProductController:
    def __init__(self, view, auth_service):
        self.view = view
        self.auth_service = auth_service
        self.model = Product()
    
    def load_products(self):
        products = self.model.get_all()
        if products is None:
            products = []
        self.view.populate_table(products)
    
    def add_product(self):
        from views.product_dialog import ProductDialog
        dialog = ProductDialog()
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                self.model.create(
                    data['name'], data['description'], data['price'], 
                    data.get('cost_price', 0), data.get('hsn_code', ''),
                    data.get('tax_rate_cgst', 0), data.get('tax_rate_sgst', 0),
                    data.get('tax_rate_igst', 0), data.get('unit', 'pcs'),
                    data.get('stock_quantity', 0)
                )
                self.load_products()
                QMessageBox.information(self.view, "Success", "Product added successfully!")
    
    def edit_product(self, product_id):
        product = self.model.get_by_id(product_id)
        if product:
            from views.product_dialog import ProductDialog
            dialog = ProductDialog(product)
            if dialog.exec_():
                data = dialog.get_data()
                if data:
                    self.model.update(
                        product_id, data['name'], data['description'], data['price'],
                        data.get('cost_price', 0), data.get('hsn_code', ''),
                        data.get('tax_rate_cgst', 0), data.get('tax_rate_sgst', 0),
                        data.get('tax_rate_igst', 0), data.get('unit', 'pcs'),
                        data.get('stock_quantity', 0)
                    )
                    self.load_products()
                    QMessageBox.information(self.view, "Success", "Product updated successfully!")
    
    def delete_product(self, product_id):
        reply = QMessageBox.question(self.view, "Confirm Delete", 
                                    "Are you sure you want to delete this product?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete(product_id)
            self.load_products()
            QMessageBox.information(self.view, "Success", "Product deleted successfully!")
    
    def search_products(self, keyword):
        if keyword and keyword.strip():
            products = self.model.search(keyword)
        else:
            products = self.model.get_all()
        if products is None:
            products = []
        self.view.populate_table(products)