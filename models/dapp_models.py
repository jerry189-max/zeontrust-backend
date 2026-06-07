import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class DAppFavoriteModel:
    
    @staticmethod
    def create(user_id: int, name: str, url: str, network: str, icon: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dapp_favorites (user_id, name, url, network, icon, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, url, network, icon, datetime.now().isoformat()))
        favorite_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return favorite_id
    
    @staticmethod
    def find_by_user(user_id: int, network: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if network:
            cursor.execute('SELECT * FROM dapp_favorites WHERE user_id = ? AND network = ? ORDER BY created_at DESC', 
                          (user_id, network))
        else:
            cursor.execute('SELECT * FROM dapp_favorites WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        favorites = []
        for row in rows:
            favorites.append({
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'url': row[3],
                'network': row[4],
                'icon': row[5],
                'created_at': row[6]
            })
        return favorites
    
    @staticmethod
    def delete(favorite_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM dapp_favorites WHERE id = ? AND user_id = ?', (favorite_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    @staticmethod
    def find_by_url(user_id: int, url: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM dapp_favorites WHERE user_id = ? AND url = ?', (user_id, url))
        row = cursor.fetchone()
        conn.close()
        return row is not None


class ConnectionHistoryModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, dapp_url: str, dapp_name: str, network: str, connection_id: str) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO connection_history 
            (user_id, wallet_id, dapp_url, dapp_name, network, connection_id, connected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, dapp_url, dapp_name, network, connection_id, datetime.now().isoformat()))
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 20):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM connection_history 
            WHERE user_id = ? 
            ORDER BY connected_at DESC 
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
                'dapp_url': row[3],
                'dapp_name': row[4],
                'network': row[5],
                'connection_id': row[6],
                'connected_at': row[7],
                'disconnected_at': row[8]
            })
        return history
    
    @staticmethod
    def find_active_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM connection_history 
            WHERE user_id = ? AND disconnected_at IS NULL
            ORDER BY connected_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        connections = []
        for row in rows:
            connections.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'dapp_url': row[3],
                'dapp_name': row[4],
                'network': row[5],
                'connection_id': row[6],
                'connected_at': row[7],
                'disconnected_at': row[8]
            })
        return connections
    
    @staticmethod
    def disconnect(connection_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE connection_history SET disconnected_at = ? WHERE connection_id = ?', 
                      (datetime.now().isoformat(), connection_id))
        conn.commit()
        conn.close()
        return True