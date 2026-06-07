import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class MultiSigWalletModel:
    
    @staticmethod
    def create(wallet_id: str, name: str, owners: list, threshold: int, 
               network: str, address: str, created_by: int) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO multisig_wallets 
            (id, name, owners, threshold, network, address, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (wallet_id, name, json.dumps(owners), threshold, network, address, 
              datetime.now().isoformat(), created_by))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def find_by_id(wallet_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM multisig_wallets WHERE id = ?', (wallet_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'owners': json.loads(row[2]),
                'threshold': row[3],
                'network': row[4],
                'address': row[5],
                'status': row[6],
                'created_at': row[7],
                'created_by': row[8]
            }
        return None
    
    @staticmethod
    def find_by_owner(owner_address: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM multisig_wallets WHERE owners LIKE ?', (f'%{owner_address}%',))
        rows = cursor.fetchall()
        conn.close()
        wallets = []
        for row in rows:
            wallets.append({
                'id': row[0],
                'name': row[1],
                'owners': json.loads(row[2]),
                'threshold': row[3],
                'network': row[4],
                'address': row[5],
                'status': row[6],
                'created_at': row[7],
                'created_by': row[8]
            })
        return wallets
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM multisig_wallets WHERE created_by = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        wallets = []
        for row in rows:
            wallets.append({
                'id': row[0],
                'name': row[1],
                'owners': json.loads(row[2]),
                'threshold': row[3],
                'network': row[4],
                'address': row[5],
                'status': row[6],
                'created_at': row[7],
                'created_by': row[8]
            })
        return wallets
    
    @staticmethod
    def get_all_multisig_wallets():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM multisig_wallets ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        wallets = []
        for row in rows:
            wallets.append({
                'id': row[0],
                'name': row[1],
                'owners': json.loads(row[2]),
                'threshold': row[3],
                'network': row[4],
                'address': row[5],
                'status': row[6],
                'created_at': row[7],
                'created_by': row[8]
            })
        return wallets


class ProposalModel:
    
    @staticmethod
    def create(proposal_id: str, multisig_id: str, creator: str, to_address: str, 
               amount: str, description: str = None, token_address: str = None,
               required_signatures: int = 2) -> bool:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO proposals 
            (id, multisig_id, creator, to_address, amount, token_address, description, 
             required_signatures, signatures, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (proposal_id, multisig_id, creator, to_address, amount, token_address, description,
              required_signatures, json.dumps([]), 'pending', datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def find_by_id(proposal_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'multisig_id': row[1],
                'creator': row[2],
                'to_address': row[3],
                'amount': row[4],
                'token_address': row[5],
                'description': row[6],
                'signatures': json.loads(row[7]),
                'required_signatures': row[8],
                'status': row[9],
                'executed_at': row[10],
                'created_at': row[11]
            }
        return None
    
    @staticmethod
    def find_by_multisig(multisig_id: str, status: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM proposals WHERE multisig_id = ? AND status = ? ORDER BY created_at DESC', 
                          (multisig_id, status))
        else:
            cursor.execute('SELECT * FROM proposals WHERE multisig_id = ? ORDER BY created_at DESC', (multisig_id,))
        rows = cursor.fetchall()
        conn.close()
        proposals = []
        for row in rows:
            proposals.append({
                'id': row[0],
                'multisig_id': row[1],
                'creator': row[2],
                'to_address': row[3],
                'amount': row[4],
                'token_address': row[5],
                'description': row[6],
                'signatures': json.loads(row[7]),
                'required_signatures': row[8],
                'status': row[9],
                'executed_at': row[10],
                'created_at': row[11]
            })
        return proposals
    
    @staticmethod
    def add_signature(proposal_id: str, signer: str):
        conn = get_db()
        cursor = conn.cursor()
        proposal = ProposalModel.find_by_id(proposal_id)
        if proposal:
            signatures = proposal['signatures']
            if signer not in signatures:
                signatures.append(signer)
                new_status = 'ready' if len(signatures) >= proposal['required_signatures'] else 'pending'
                cursor.execute('UPDATE proposals SET signatures = ?, status = ? WHERE id = ?',
                              (json.dumps(signatures), new_status, proposal_id))
                conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def execute_proposal(proposal_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE proposals SET status = "executed", executed_at = ? WHERE id = ?',
                      (datetime.now().isoformat(), proposal_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def cancel_proposal(proposal_id: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE proposals SET status = "cancelled" WHERE id = ?', (proposal_id,))
        conn.commit()
        conn.close()
        return True