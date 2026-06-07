import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class WalletModel:
    
    @staticmethod
    def create(user_id: int, wallet_name: str, mnemonic_encrypted: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wallets (user_id, wallet_name, mnemonic_encrypted, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, wallet_name, mnemonic_encrypted, datetime.now().isoformat()))
        wallet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return wallet_id
    
    @staticmethod
    def find_by_id(wallet_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, wallet_name, mnemonic_encrypted, is_backed_up, is_active, created_at
            FROM wallets WHERE id = ?
        ''', (wallet_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'wallet_name': row[2],
                'mnemonic_encrypted': row[3],
                'is_backed_up': bool(row[4]),
                'is_active': bool(row[5]),
                'created_at': row[6]
            }
        return None
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, wallet_name, mnemonic_encrypted, is_backed_up, is_active, created_at
            FROM wallets WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        wallets = []
        for row in rows:
            wallets.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_name': row[2],
                'mnemonic_encrypted': row[3],
                'is_backed_up': bool(row[4]),
                'is_active': bool(row[5]),
                'created_at': row[6]
            })
        return wallets
    
    @staticmethod
    def update_backup_status(wallet_id: int, is_backed_up: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE wallets SET is_backed_up = ? WHERE id = ?', (1 if is_backed_up else 0, wallet_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_active_status(wallet_id: int, is_active: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE wallets SET is_active = ? WHERE id = ?', (1 if is_active else 0, wallet_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_mnemonic(wallet_id: int, mnemonic_encrypted: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE wallets SET mnemonic_encrypted = ? WHERE id = ?', (mnemonic_encrypted, wallet_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_wallet(wallet_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wallets WHERE id = ?', (wallet_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_all_wallets(limit: int = 100):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.id, w.user_id, w.wallet_name, w.is_active, w.created_at, u.username, u.email
            FROM wallets w JOIN users u ON w.user_id = u.id
            ORDER BY w.created_at DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        wallets = []
        for row in rows:
            wallets.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_name': row[2],
                'is_active': bool(row[3]),
                'created_at': row[4],
                'username': row[5],
                'email': row[6]
            })
        return wallets
    
    @staticmethod
    def get_wallet_count():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM wallets')
        count = cursor.fetchone()[0]
        conn.close()
        return count


class NetworkAccountModel:
    
    @staticmethod
    def create(wallet_id: int, network: str, address: str, private_key_encrypted: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO network_accounts (wallet_id, network, address, private_key_encrypted, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (wallet_id, network, address, private_key_encrypted, datetime.now().isoformat()))
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    @staticmethod
    def find_by_id(account_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, wallet_id, network, address, private_key_encrypted, created_at
            FROM network_accounts WHERE id = ?
        ''', (account_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'address': row[3],
                'private_key_encrypted': row[4],
                'created_at': row[5]
            }
        return None
    
    @staticmethod
    def find_by_wallet(wallet_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, wallet_id, network, address, private_key_encrypted, created_at
            FROM network_accounts WHERE wallet_id = ?
        ''', (wallet_id,))
        rows = cursor.fetchall()
        conn.close()
        accounts = []
        for row in rows:
            accounts.append({
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'address': row[3],
                'private_key_encrypted': row[4],
                'created_at': row[5]
            })
        return accounts
    
    @staticmethod
    def find_by_wallet_and_network(wallet_id: int, network: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, wallet_id, network, address, private_key_encrypted, created_at
            FROM network_accounts WHERE wallet_id = ? AND network = ?
        ''', (wallet_id, network))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'address': row[3],
                'private_key_encrypted': row[4],
                'created_at': row[5]
            }
        return None
    
    @staticmethod
    def find_by_address(address: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, wallet_id, network, address, private_key_encrypted, created_at
            FROM network_accounts WHERE address = ?
        ''', (address,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'wallet_id': row[1],
                'network': row[2],
                'address': row[3],
                'private_key_encrypted': row[4],
                'created_at': row[5]
            }
        return None
    
    @staticmethod
    def update_private_key(account_id: int, private_key_encrypted: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE network_accounts SET private_key_encrypted = ? WHERE id = ?', (private_key_encrypted, account_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_account(account_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM network_accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()
        return True