"""
User Database Management for X12 Quantum Server
"""

import sqlite3
import bcrypt
from datetime import datetime

class UserDatabase:
    def __init__(self, db_path='quantum_users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    quantum_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create user_sessions table for tracking active sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def user_exists(self, username, email):
        """Check if a user with given username or email exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            )
            return cursor.fetchone() is not None
    
    def create_user(self, username, email, password, quantum_key):
        """Create a new user with hashed password"""
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, email, password_hash, quantum_key)
                   VALUES (?, ?, ?, ?)''',
                (username, email, password_hash, quantum_key)
            )
            conn.commit()
            return cursor.lastrowid
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, username, email, password_hash FROM users WHERE username = ? AND is_active = TRUE',
                (username,)
            )
            user = cursor.fetchone()
            
            if user:
                user_id, username, email, password_hash = user
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    return {
                        'id': user_id,
                        'username': username,
                        'email': email
                    }
            
            return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, username, email, created_at FROM users WHERE id = ? AND is_active = TRUE',
                (user_id,)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'created_at': user[3]
                }
            
            return None
    
    def update_last_login(self, user_id):
        """Update the last login timestamp for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user_id,)
            )
            conn.commit()
    
    def add_session(self, user_id, token, expires_at):
        """Add a user session to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO user_sessions (user_id, token, expires_at)
                   VALUES (?, ?, ?)''',
                (user_id, token, expires_at)
            )
            conn.commit()
    
    def invalidate_session(self, token):
        """Invalidate a user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM user_sessions WHERE token = ?',
                (token,)
            )
            conn.commit()
    
    def is_valid_session(self, token):
        """Check if a session token is valid"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT id FROM user_sessions 
                   WHERE token = ? AND expires_at > datetime('now')''',
                (token,)
            )
            return cursor.fetchone() is not None

# For testing
if __name__ == '__main__':
    db = UserDatabase()
    print("Database initialized successfully")
