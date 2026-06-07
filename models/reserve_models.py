import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class ReserveTokenModel:
    
    @staticmethod
    def create(network: str, contract_address: str, token_name: str, token_symbol: str,
               decimals: int, total_supply: str, balance: str, is_mintable: bool = True,
               is_burnable: bool = True, created_by: int = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reserve_tokens 
            (network, contract_address, token_name, token_symbol, decimals, total_supply, balance, 
             is_mintable, is_burnable, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (network, contract_address, token_name, token_symbol, decimals, total_supply, balance,
              1 if is_mintable else 0, 1 if is_burnable else 0, datetime.now().isoformat(), created_by))
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return token_id
    
    @staticmethod
    def find_by_id(token_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reserve_tokens WHERE id = ?', (token_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'network': row[1],
                'contract_address': row[2],
                'token_name': row[3],
                'token_symbol': row[4],
                'decimals': row[5],
                'total_supply': row[6],
                'balance': row[7],
                'is_mintable': bool(row[8]),
                'is_burnable': bool(row[9]),
                'created_at': row[10],
                'created_by': row[11]
            }
        return None
    
    @staticmethod
    def find_by_contract(contract_address: str, network: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reserve_tokens WHERE contract_address = ? AND network = ?', (contract_address, network))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'network': row[1],
                'contract_address': row[2],
                'token_name': row[3],
                'token_symbol': row[4],
                'decimals': row[5],
                'total_supply': row[6],
                'balance': row[7],
                'is_mintable': bool(row[8]),
                'is_burnable': bool(row[9]),
                'created_at': row[10],
                'created_by': row[11]
            }
        return None
    
    @staticmethod
    def get_all_reserve_tokens():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reserve_tokens ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        tokens = []
        for row in rows:
            tokens.append({
                'id': row[0],
                'network': row[1],
                'contract_address': row[2],
                'token_name': row[3],
                'token_symbol': row[4],
                'decimals': row[5],
                'total_supply': row[6],
                'balance': row[7],
                'is_mintable': bool(row[8]),
                'is_burnable': bool(row[9]),
                'created_at': row[10],
                'created_by': row[11]
            })
        return tokens
    
    @staticmethod
    def mint_tokens(token_id: int, amount: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT total_supply, balance FROM reserve_tokens WHERE id = ?', (token_id,))
        row = cursor.fetchone()
        if row:
            new_total_supply = str(float(row[0]) + float(amount))
            new_balance = str(float(row[1]) + float(amount))
            cursor.execute('UPDATE reserve_tokens SET total_supply = ?, balance = ? WHERE id = ?', 
                          (new_total_supply, new_balance, token_id))
            conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def burn_tokens(token_id: int, amount: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT total_supply, balance FROM reserve_tokens WHERE id = ?', (token_id,))
        row = cursor.fetchone()
        if row and float(row[1]) >= float(amount):
            new_total_supply = str(float(row[0]) - float(amount))
            new_balance = str(float(row[1]) - float(amount))
            cursor.execute('UPDATE reserve_tokens SET total_supply = ?, balance = ? WHERE id = ?', 
                          (new_total_supply, new_balance, token_id))
            conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def transfer_tokens(token_id: int, amount: str, to_address: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM reserve_tokens WHERE id = ?', (token_id,))
        row = cursor.fetchone()
        if row and float(row[0]) >= float(amount):
            new_balance = str(float(row[0]) - float(amount))
            cursor.execute('UPDATE reserve_tokens SET balance = ? WHERE id = ?', (new_balance, token_id))
            conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_total_reserve_value():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(CAST(balance AS REAL)) FROM reserve_tokens')
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total


class ReserveTransactionModel:
    
    @staticmethod
    def create(token_id: int, type: str, amount: str, from_address: str = None, 
               to_address: str = None, tx_hash: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reserve_transactions 
            (token_id, type, amount, from_address, to_address, tx_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (token_id, type, amount, from_address, to_address, tx_hash, datetime.now().isoformat()))
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tx_id
    
    @staticmethod
    def find_by_token(token_id: int, limit: int = 50):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reserve_transactions 
            WHERE token_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (token_id, limit))
        rows = cursor.fetchall()
        conn.close()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'token_id': row[1],
                'type': row[2],
                'amount': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'tx_hash': row[6],
                'created_at': row[7]
            })
        return transactions