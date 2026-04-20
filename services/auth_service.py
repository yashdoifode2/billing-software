import bcrypt
from database.db_manager import DatabaseManager

class AuthService:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        self.ensure_admin_user()
    
    def ensure_admin_user(self):
        """Ensure admin user exists"""
        try:
            admin = self.db.fetch_one("SELECT * FROM users WHERE username = 'admin'")
            if not admin:
                # Create admin user (password: Admin@123)
                password_hash = self.hash_password("Admin@123")
                query = """
                    INSERT INTO users (username, password_hash, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.db.execute_query(query, ("admin", password_hash, "Administrator", "admin", 1))
                print("Admin user created successfully")
        except Exception as e:
            print(f"Error creating admin user: {e}")
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def authenticate(self, username, password):
        """Authenticate user"""
        try:
            query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
            user = self.db.fetch_one(query, (username,))
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # Update last login
                update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
                self.db.execute_query(update_query, (user['id'],))
                
                self.current_user = user
                return user
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def has_permission(self, permission_name):
        """Check if current user has specific permission"""
        if not self.current_user:
            return False
        
        if self.current_user['role'] == 'admin':
            return True
        return False  # Simplified for now
    
    def logout(self):
        """Logout current user"""
        self.current_user = None