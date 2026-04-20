from services.report_service import ReportService
from PyQt5.QtWidgets import QMessageBox
import json

class ReportController:
    def __init__(self, view, auth_service):
        self.view = view
        self.auth_service = auth_service
        self.report_service = ReportService()
        self.current_report_data = None
        self.current_report_type = None
    
    def get_revenue_report(self, start_date, end_date):
        data = self.report_service.get_daily_revenue()
        self.current_report_data = data
        self.current_report_type = 'revenue'
        return data
    
    def get_outstanding_report(self):
        data = self.report_service.get_outstanding_report()
        self.current_report_data = data
        self.current_report_type = 'outstanding'
        return data
    
    def get_tax_report(self, start_date, end_date):
        data = self.report_service.get_tax_collection(start_date, end_date)
        self.current_report_data = [data] if data else []
        self.current_report_type = 'tax'
        return data if data else {}
    
    def get_profit_loss(self, start_date, end_date):
        data = self.report_service.get_profit_loss(start_date, end_date)
        self.current_report_data = [data]
        self.current_report_type = 'profit_loss'
        return data
    
    def get_expense_report(self, start_date, end_date):
        data = self.report_service.get_by_category(start_date, end_date)
        self.current_report_data = data
        self.current_report_type = 'expense'
        return data
    
    def export_current_report(self, file_path, format_type):
        if not self.current_report_data:
            QMessageBox.warning(self.view, "No Data", "No report data to export!")
            return False
        
        try:
            if format_type == 'csv':
                headers = list(self.current_report_data[0].keys()) if self.current_report_data else []
                self.report_service.export_to_csv(self.current_report_data, file_path, headers)
            else:
                self.report_service.export_to_excel(self.current_report_data, file_path, 
                                                   f"{self.current_report_type}_report")
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False