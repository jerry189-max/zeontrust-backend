import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class ChainPreferenceModel:
    
    @staticmethod
    def set_preference(user_id: int, chain_id: str, is_testnet: bool = False):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO chain_preferences (user_id, chain_id, is_testnet, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, chain_id, 1 if is_testnet else 0, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_preference(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT chain_id, is_testnet FROM chain_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'chain_id': row[0], 'is_testnet': bool(row[1])}
        return {'chain_id': 'tron', 'is_testnet': False}
    
    @staticmethod
    def set_all_chains_testnet(user_id: int, is_testnet: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO chain_preferences (user_id, chain_id, is_testnet, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'all_chains', 1 if is_testnet else 0, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_all_chains_testnet(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT is_testnet FROM chain_preferences WHERE user_id = ? AND chain_id = ?', (user_id, 'all_chains'))
        row = cursor.fetchone()
        conn.close()
        if row:
            return bool(row[0])
        return False


class CrossChainTransactionModel:
    
    @staticmethod
    def create(user_id: int, from_chain: str, to_chain: str, from_address: str,
               to_address: str, amount: float, token: str, tx_hash: str, status: str = 'pending') -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cross_chain_transactions 
            (user_id, from_chain, to_chain, from_address, to_address, amount, token, tx_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, from_chain, to_chain, from_address, to_address, amount, token, tx_hash, status, datetime.now().isoformat()))
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tx_id
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 20):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM cross_chain_transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'user_id': row[1],
                'from_chain': row[2],
                'to_chain': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token': row[7],
                'tx_hash': row[8],
                'status': row[9],
                'created_at': row[10]
            })
        return transactions
    
    @staticmethod
    def update_status(tx_hash: str, status: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE cross_chain_transactions SET status = ? WHERE tx_hash = ?', (status, tx_hash))
        conn.commit()
        conn.close()
        return True