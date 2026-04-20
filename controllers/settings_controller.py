from database.db_manager import DatabaseManager

class SettingsController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_settings(self):
        query = "SELECT setting_key, setting_value FROM settings"
        results = self.db.fetch_all(query)
        return {item['setting_key']: item['setting_value'] for item in results}
    
    def update_setting(self, key, value):
        query = """
            UPDATE settings 
            SET setting_value=?, updated_at=CURRENT_TIMESTAMP
            WHERE setting_key=?
        """
        self.db.execute_query(query, (value, key))
    
    def save_logo(self, logo_path):
        with open(logo_path, 'rb') as f:
            import base64
            logo_data = base64.b64encode(f.read()).decode('utf-8')
            self.update_setting('company_logo', logo_data)