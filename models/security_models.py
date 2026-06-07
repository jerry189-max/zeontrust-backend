import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class SecuritySettingsModel:
    
    @staticmethod
    def create_or_update(user_id: int, settings: dict):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO security_settings 
            (user_id, password_lock_enabled, session_timeout_minutes, two_factor_enabled, pin_enabled, pin_hash, two_factor_secret, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            1 if settings.get('password_lock_enabled', True) else 0,
            settings.get('session_timeout_minutes', 1440),
            1 if settings.get('two_factor_enabled', False) else 0,
            1 if settings.get('pin_enabled', False) else 0,
            settings.get('pin_hash'),
            settings.get('two_factor_secret'),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM security_settings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'user_id': row[0],
                'password_lock_enabled': bool(row[1]),
                'session_timeout_minutes': row[2],
                'two_factor_enabled': bool(row[3]),
                'pin_enabled': bool(row[4]),
                'pin_hash': row[5],
                'two_factor_secret': row[6],
                'updated_at': row[7]
            }
        return {
            'user_id': user_id,
            'password_lock_enabled': True,
            'session_timeout_minutes': 1440,
            'two_factor_enabled': False,
            'pin_enabled': False,
            'pin_hash': None,
            'two_factor_secret': None
        }
    
    @staticmethod
    def update_pin(user_id: int, pin_hash: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE security_settings SET pin_hash = ?, pin_enabled = 1, updated_at = ? WHERE user_id = ?',
                      (pin_hash, datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def disable_pin(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE security_settings SET pin_hash = NULL, pin_enabled = 0, updated_at = ? WHERE user_id = ?',
                      (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def enable_2fa(user_id: int, secret: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE security_settings SET two_factor_secret = ?, two_factor_enabled = 1, updated_at = ? WHERE user_id = ?',
                      (secret, datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def disable_2fa(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE security_settings SET two_factor_secret = NULL, two_factor_enabled = 0, updated_at = ? WHERE user_id = ?',
                      (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        return True


class SessionModel:
    
    @staticmethod
    def create(user_id: int, token: str, expires_at: datetime):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (user_id, token, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, token, expires_at.isoformat(), datetime.now().isoformat()))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    @staticmethod
    def find_by_token(token: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE token = ?', (token,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'token': row[2],
                'expires_at': row[3],
                'created_at': row[4]
            }
        return None
    
    @staticmethod
    def delete_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_expired():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_user_sessions(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        sessions = []
        for row in rows:
            sessions.append({
                'id': row[0],
                'user_id': row[1],
                'token': row[2],
                'expires_at': row[3],
                'created_at': row[4]
            })
        return sessions


class BackupHistoryModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, backup_type: str, backup_hash: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO backup_history (user_id, wallet_id, backup_type, backup_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, backup_type, backup_hash, datetime.now().isoformat()))
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 10):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM backup_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'backup_type': row[3],
                'backup_hash': row[4],
                'created_at': row[5]
            })
        return history
    
    @staticmethod
    def get_last_backup(user_id: int, wallet_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM backup_history 
            WHERE user_id = ? AND wallet_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id, wallet_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'backup_type': row[3],
                'backup_hash': row[4],
                'created_at': row[5]
            }
        return None