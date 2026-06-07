import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class TransactionModel:
    
    @staticmethod
    def create(wallet_id: int, network: str, tx_hash: str, from_address: str, 
               to_address: str, amount: str, token_address: str = None, 
               token_symbol: str = None, fee: str = None, status: str = 'pending') -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions 
            (wallet_id, network, tx_hash, from_address, to_address, amount, token_address, token_symbol, fee, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (wallet_id, network, tx_hash, from_address, to_address, amount, 
              token_address, token_symbol, fee, status, datetime.now().isoformat()))
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tx_id
    
    @staticmethod
    def find_by_id(tx_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (tx_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            }
        return None
    
    @staticmethod
    def find_by_hash(tx_hash: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE tx_hash = ?', (tx_hash,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            }
        return None
    
    @staticmethod
    def find_by_wallet(wallet_id: int, limit: int = 50, offset: int = 0):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE wallet_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (wallet_id, limit, offset))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            })
        return transactions
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 50):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.* FROM transactions t
            JOIN wallets w ON t.wallet_id = w.id
            WHERE w.user_id = ?
            ORDER BY t.timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            })
        return transactions
    
    @staticmethod
    def update_status(tx_hash: str, status: str, block_number: int = None):
        conn = get_db()
        cursor = conn.cursor()
        if block_number:
            cursor.execute('UPDATE transactions SET status = ?, block_number = ? WHERE tx_hash = ?', 
                          (status, block_number, tx_hash))
        else:
            cursor.execute('UPDATE transactions SET status = ? WHERE tx_hash = ?', (status, tx_hash))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_fee(tx_hash: str, fee: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE transactions SET fee = ? WHERE tx_hash = ?', (fee, tx_hash))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_transaction_count(wallet_id: int = None):
        conn = get_db()
        cursor = conn.cursor()
        if wallet_id:
            cursor.execute('SELECT COUNT(*) FROM transactions WHERE wallet_id = ?', (wallet_id,))
        else:
            cursor.execute('SELECT COUNT(*) FROM transactions')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def get_transactions_by_network(network: str, limit: int = 100):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE network = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (network, limit))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            })
        return transactions
    
    @staticmethod
    def get_transactions_by_date_range(wallet_id: int, start_date: str, end_date: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE wallet_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (wallet_id, start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'token_address': row[7],
                'token_symbol': row[8],
                'fee': row[9],
                'status': row[10],
                'block_number': row[11],
                'timestamp': row[12]
            })
        return transactions