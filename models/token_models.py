import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class TokenModel:
    
    @staticmethod
    def create_verified_token(network: str, contract_address: str, token_name: str, token_symbol: str, 
                               decimals: int, logo_url: str = None, website: str = None, 
                               category: str = None, risk_level: str = 'low') -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO verified_tokens 
            (network, contract_address, token_name, token_symbol, decimals, logo_url, website, category, risk_level, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (network, contract_address, token_name, token_symbol, decimals, logo_url, website, category, risk_level, datetime.now().isoformat()))
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return token_id
    
    @staticmethod
    def find_verified_token(contract_address: str, network: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, network, contract_address, token_name, token_symbol, decimals, logo_url, website, category, risk_level, is_active, verified_at
            FROM verified_tokens WHERE contract_address = ? AND network = ?
        ''', (contract_address, network))
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
                'logo_url': row[6],
                'website': row[7],
                'category': row[8],
                'risk_level': row[9],
                'is_active': bool(row[10]),
                'verified_at': row[11]
            }
        return None
    
    @staticmethod
    def get_all_verified_tokens(network: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if network:
            cursor.execute('''
                SELECT id, network, contract_address, token_name, token_symbol, decimals, logo_url, website, category, risk_level, is_active, verified_at
                FROM verified_tokens WHERE network = ? AND is_active = 1 ORDER BY token_name
            ''', (network,))
        else:
            cursor.execute('''
                SELECT id, network, contract_address, token_name, token_symbol, decimals, logo_url, website, category, risk_level, is_active, verified_at
                FROM verified_tokens WHERE is_active = 1 ORDER BY token_name
            ''')
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
                'logo_url': row[6],
                'website': row[7],
                'category': row[8],
                'risk_level': row[9],
                'is_active': bool(row[10]),
                'verified_at': row[11]
            })
        return tokens
    
    @staticmethod
    def update_verified_token_status(token_id: int, is_active: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE verified_tokens SET is_active = ? WHERE id = ?', (1 if is_active else 0, token_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_verified_token(token_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM verified_tokens WHERE id = ?', (token_id,))
        conn.commit()
        conn.close()
        return True


class CustomTokenModel:
    
    @staticmethod
    def create(user_id: int, network: str, contract_address: str, token_name: str, 
               token_symbol: str, decimals: int, logo_url: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO custom_tokens (user_id, network, contract_address, token_name, token_symbol, decimals, logo_url, added_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, network, contract_address, token_name, token_symbol, decimals, logo_url, datetime.now().isoformat()))
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return token_id
    
    @staticmethod
    def find_by_user(user_id: int, network: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if network:
            cursor.execute('''
                SELECT id, user_id, network, contract_address, token_name, token_symbol, decimals, logo_url, added_at
                FROM custom_tokens WHERE user_id = ? AND network = ? ORDER BY added_at DESC
            ''', (user_id, network))
        else:
            cursor.execute('''
                SELECT id, user_id, network, contract_address, token_name, token_symbol, decimals, logo_url, added_at
                FROM custom_tokens WHERE user_id = ? ORDER BY added_at DESC
            ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        tokens = []
        for row in rows:
            tokens.append({
                'id': row[0],
                'user_id': row[1],
                'network': row[2],
                'contract_address': row[3],
                'token_name': row[4],
                'token_symbol': row[5],
                'decimals': row[6],
                'logo_url': row[7],
                'added_at': row[8]
            })
        return tokens
    
    @staticmethod
    def find_by_contract(user_id: int, contract_address: str, network: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, network, contract_address, token_name, token_symbol, decimals, logo_url, added_at
            FROM custom_tokens WHERE user_id = ? AND contract_address = ? AND network = ?
        ''', (user_id, contract_address, network))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'network': row[2],
                'contract_address': row[3],
                'token_name': row[4],
                'token_symbol': row[5],
                'decimals': row[6],
                'logo_url': row[7],
                'added_at': row[8]
            }
        return None
    
    @staticmethod
    def delete_custom_token(token_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM custom_tokens WHERE id = ? AND user_id = ?', (token_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class TokenVerificationRequestModel:
    
    @staticmethod
    def create(user_id: int, network: str, contract_address: str, token_name: str,
               token_symbol: str, decimals: int, website: str = None, email: str = None,
               twitter: str = None, telegram: str = None, discord: str = None,
               logo_url: str = None, description: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO token_verification_requests 
            (user_id, network, contract_address, token_name, token_symbol, decimals, website, email, twitter, telegram, discord, logo_url, description, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, network, contract_address, token_name, token_symbol, decimals, 
              website, email, twitter, telegram, discord, logo_url, description, datetime.now().isoformat()))
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return request_id
    
    @staticmethod
    def find_pending_requests():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.username, u.email as user_email
            FROM token_verification_requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'pending'
            ORDER BY r.submitted_at ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        requests = []
        for row in rows:
            requests.append({
                'id': row[0],
                'user_id': row[1],
                'network': row[2],
                'contract_address': row[3],
                'token_name': row[4],
                'token_symbol': row[5],
                'decimals': row[6],
                'website': row[7],
                'email': row[8],
                'twitter': row[9],
                'telegram': row[10],
                'discord': row[11],
                'logo_url': row[12],
                'description': row[13],
                'status': row[14],
                'admin_notes': row[15],
                'submitted_at': row[16],
                'reviewed_at': row[17],
                'reviewed_by': row[18],
                'username': row[19],
                'user_email': row[20]
            })
        return requests
    
    @staticmethod
    def find_by_id(request_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.username, u.email as user_email
            FROM token_verification_requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = ?
        ''', (request_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'network': row[2],
                'contract_address': row[3],
                'token_name': row[4],
                'token_symbol': row[5],
                'decimals': row[6],
                'website': row[7],
                'email': row[8],
                'twitter': row[9],
                'telegram': row[10],
                'discord': row[11],
                'logo_url': row[12],
                'description': row[13],
                'status': row[14],
                'admin_notes': row[15],
                'submitted_at': row[16],
                'reviewed_at': row[17],
                'reviewed_by': row[18],
                'username': row[19],
                'user_email': row[20]
            }
        return None
    
    @staticmethod
    def update_status(request_id: int, status: str, admin_id: int, admin_notes: str = None):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE token_verification_requests 
            SET status = ?, reviewed_by = ?, reviewed_at = ?, admin_notes = ?
            WHERE id = ?
        ''', (status, admin_id, datetime.now().isoformat(), admin_notes, request_id))
        conn.commit()
        conn.close()
        return True