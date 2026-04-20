from database.db_manager import DatabaseManager
import socket

class AuditService:
    def __init__(self, auth_service):
        self.db = DatabaseManager()
        self.auth_service = auth_service
    
    def log_action(self, action, table_name=None, record_id=None, old_value=None, new_value=None):
        """Log user action"""
        if not self.auth_service.current_user:
            return
        
        # Get IP address (simplified)
        ip_address = socket.gethostbyname(socket.gethostname())
        
        query = """
            INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (
            self.auth_service.current_user['id'],
            action,
            table_name,
            record_id,
            old_value,
            new_value,
            ip_address
        ))
    
    def get_audit_logs(self, limit=100):
        """Get recent audit logs"""
        query = """
            SELECT al.*, u.username, u.full_name
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (limit,))
    
    def get_user_activity(self, user_id, days=30):
        """Get user activity for last N days"""
        query = """
            SELECT action, COUNT(*) as count
            FROM audit_logs
            WHERE user_id = ? AND timestamp >= datetime('now', ?)
            GROUP BY action
        """
        return self.db.fetch_all(query, (user_id, f'-{days} days'))