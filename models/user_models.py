import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class UserModel:
    
    @staticmethod
    def create(username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, 1 if is_admin else 0, datetime.now().isoformat()))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    @staticmethod
    def find_by_id(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, password_hash, is_active, is_admin, created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3],
                'is_active': bool(row[4]),
                'is_admin': bool(row[5]),
                'created_at': row[6],
                'last_login': row[7]
            }
        return None
    
    @staticmethod
    def find_by_email(email: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, password_hash, is_active, is_admin, created_at, last_login
            FROM users WHERE email = ?
        ''', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3],
                'is_active': bool(row[4]),
                'is_admin': bool(row[5]),
                'created_at': row[6],
                'last_login': row[7]
            }
        return None
    
    @staticmethod
    def find_by_username(username: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'username': row[1], 'email': row[2]}
        return None
    
    @staticmethod
    def update_last_login(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_password(user_id: int, new_password_hash: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def set_active_status(user_id: int, is_active: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (1 if is_active else 0, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_all_users(limit: int = 100, offset: int = 0):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, is_active, is_admin, created_at, last_login
            FROM users ORDER BY id DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'is_active': bool(row[3]),
                'is_admin': bool(row[4]),
                'created_at': row[5],
                'last_login': row[6]
            })
        return users
    
    @staticmethod
    def get_user_count():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def delete_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def search_users(query: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, is_active, is_admin, created_at
            FROM users WHERE username LIKE ? OR email LIKE ?
            LIMIT 50
        ''', (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        conn.close()
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'is_active': bool(row[3]),
                'is_admin': bool(row[4]),
                'created_at': row[5]
            })
        return users