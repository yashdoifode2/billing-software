import sqlite3
import os
from contextlib import contextmanager
from config import Config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        if not os.path.exists(self.db_path):
            with self.get_connection() as conn:
                cursor = conn.cursor()
                schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        cursor.executescript(f.read())
                conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a single query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def fetch_all(self, query, params=None):
        """Fetch all results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def fetch_one(self, query, params=None):
        """Fetch single result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_many(self, query, params_list):
        """Execute many queries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount