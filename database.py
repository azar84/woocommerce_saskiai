import sqlite3
import json
from datetime import datetime
from cryptography.fernet import Fernet
from config import DATABASE_NAME, ENCRYPTION_KEY

class DatabaseManager:
    def __init__(self, db_name=None):
        self.db_name = db_name or DATABASE_NAME
        self.cipher_suite = Fernet(ENCRYPTION_KEY)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Create stores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_url TEXT UNIQUE NOT NULL,
                    store_name TEXT,
                    admin_username TEXT NOT NULL,
                    admin_password TEXT NOT NULL,
                    permissions TEXT DEFAULT 'read_write',
                    description TEXT DEFAULT 'Application Password Authentication',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create connection logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connection_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id INTEGER,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (store_id) REFERENCES stores (id)
                )
            ''')
            
            conn.commit()
    
    def encrypt_data(self, data):
        """Encrypt sensitive data."""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data."""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def store_credentials(self, store_url, store_name, admin_username, admin_password, 
                         permissions='read_write', description='Application Password Authentication'):
        """Store WooCommerce Application Password credentials securely."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Encrypt sensitive data
            encrypted_username = self.encrypt_data(admin_username)
            encrypted_password = self.encrypt_data(admin_password)
            
            cursor.execute('''
                INSERT OR REPLACE INTO stores 
                (store_url, store_name, admin_username, admin_password, 
                 permissions, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                store_url, store_name, encrypted_username, encrypted_password,
                permissions, description, datetime.now()
            ))
            
            store_id = cursor.lastrowid
            conn.commit()
            
            # Log the action
            self.log_action(store_id, "store_credentials", "success", 
                          f"Application Password credentials stored for {store_url}")
            
            return store_id
    
    def get_credentials(self, store_url):
        """Retrieve decrypted credentials for a store."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, store_url, store_name, admin_username, admin_password,
                       permissions, description, created_at, status
                FROM stores WHERE store_url = ? AND status = 'active'
            ''', (store_url,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'store_url': row[1],
                    'store_name': row[2],
                    'admin_username': self.decrypt_data(row[3]),
                    'admin_password': self.decrypt_data(row[4]),
                    'permissions': row[5],
                    'description': row[6],
                    'created_at': row[7],
                    'status': row[8]
                }
            return None
    
    def list_stores(self):
        """List all connected stores."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, store_url, store_name, permissions, 
                       created_at, status
                FROM stores WHERE status = 'active'
                ORDER BY created_at DESC
            ''')
            
            return [
                {
                    'id': row[0],
                    'store_url': row[1],
                    'store_name': row[2],
                    'permissions': row[3],
                    'created_at': row[4],
                    'status': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    def disconnect_store(self, store_url):
        """Disconnect a store by marking it as inactive."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE stores SET status = 'inactive', updated_at = ?
                WHERE store_url = ?
            ''', (datetime.now(), store_url))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.log_action(None, "disconnect_store", "success", 
                              f"Store {store_url} disconnected")
                return True
            return False
    
    def log_action(self, store_id, action, status, message):
        """Log an action to the connection logs."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO connection_logs (store_id, action, status, message)
                VALUES (?, ?, ?, ?)
            ''', (store_id, action, status, message))
            conn.commit()
    
    def get_logs(self, store_id=None, limit=50):
        """Get connection logs."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            if store_id:
                cursor.execute('''
                    SELECT cl.*, s.store_url 
                    FROM connection_logs cl
                    LEFT JOIN stores s ON cl.store_id = s.id
                    WHERE cl.store_id = ?
                    ORDER BY cl.timestamp DESC
                    LIMIT ?
                ''', (store_id, limit))
            else:
                cursor.execute('''
                    SELECT cl.*, s.store_url 
                    FROM connection_logs cl
                    LEFT JOIN stores s ON cl.store_id = s.id
                    ORDER BY cl.timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            return [
                {
                    'id': row[0],
                    'store_id': row[1],
                    'action': row[2],
                    'status': row[3],
                    'message': row[4],
                    'timestamp': row[5],
                    'store_url': row[6]
                }
                for row in cursor.fetchall()
            ] 