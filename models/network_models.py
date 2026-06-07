import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class NetworkConfigModel:
    
    @staticmethod
    def create(network_id: str, name: str, symbol: str, rpc_url: str, 
               explorer_url: str, chain_id: int, is_active: bool = True) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO network_configs (network_id, name, symbol, rpc_url, explorer_url, chain_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (network_id, name, symbol, rpc_url, explorer_url, chain_id, 1 if is_active else 0))
        network_id_result = cursor.lastrowid
        conn.commit()
        conn.close()
        return network_id_result
    
    @staticmethod
    def find_by_id(network_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM network_configs WHERE network_id = ?', (network_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'network_id': row[1],
                'name': row[2],
                'symbol': row[3],
                'rpc_url': row[4],
                'explorer_url': row[5],
                'chain_id': row[6],
                'is_active': bool(row[7]),
                'created_at': row[8]
            }
        return None
    
    @staticmethod
    def find_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM network_configs WHERE is_active = 1')
        rows = cursor.fetchall()
        conn.close()
        networks = []
        for row in rows:
            networks.append({
                'id': row[0],
                'network_id': row[1],
                'name': row[2],
                'symbol': row[3],
                'rpc_url': row[4],
                'explorer_url': row[5],
                'chain_id': row[6],
                'is_active': bool(row[7])
            })
        return networks
    
    @staticmethod
    def update_status(network_id: str, is_active: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE network_configs SET is_active = ? WHERE network_id = ?', (1 if is_active else 0, network_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_rpc(network_id: str, rpc_url: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE network_configs SET rpc_url = ? WHERE network_id = ?', (rpc_url, network_id))
        conn.commit()
        conn.close()
        return True


class UserNetworkPreference:
    
    @staticmethod
    def set_preference(user_id: int, network_id: str, is_testnet: bool = False):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_network_preferences (user_id, network_id, is_testnet, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, network_id, 1 if is_testnet else 0, datetime.now()))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_preference(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT network_id, is_testnet FROM user_network_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'network_id': row[0], 'is_testnet': bool(row[1])}
        return {'network_id': 'tron', 'is_testnet': False}