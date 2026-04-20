import shutil
import os
from datetime import datetime

class BackupRestore:
    def __init__(self, db_path="invoice_app.db"):
        self.db_path = db_path
    
    def backup(self, backup_path):
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False
    
    def restore(self, backup_path):
        try:
            # Create backup of current before restore
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_backup = f"backup_before_restore_{timestamp}.db"
            shutil.copy2(self.db_path, auto_backup)
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False