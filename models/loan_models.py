import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class LoanModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, network: str, token: str, amount: str, 
               duration_days: int, purpose: str = None, interest_rate: float = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        
        if interest_rate is None:
            cursor.execute('SELECT value FROM settings WHERE key = "default_interest_rate"')
            row = cursor.fetchone()
            interest_rate = float(row[0]) if row else 5.0
        
        total_payable = float(amount) * (1 + interest_rate / 100)
        
        cursor.execute('''
            INSERT INTO loan_requests 
            (user_id, wallet_id, network, token, amount, duration_days, interest_rate, total_payable, purpose, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, network, token, str(amount), duration_days, interest_rate, 
              str(total_payable), purpose, 'pending', datetime.now().isoformat()))
        loan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return loan_id
    
    @staticmethod
    def find_by_id(loan_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.username, u.email
            FROM loan_requests l
            JOIN users u ON l.user_id = u.id
            WHERE l.id = ?
        ''', (loan_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'duration_days': row[6],
                'interest_rate': row[7],
                'total_payable': row[8],
                'purpose': row[9],
                'status': row[10],
                'approved_by': row[11],
                'approved_at': row[12],
                'repaid_amount': row[13],
                'is_repaid': bool(row[14]),
                'created_at': row[15],
                'username': row[16],
                'email': row[17]
            }
        return None
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM loan_requests WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        loans = []
        for row in rows:
            loans.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'duration_days': row[6],
                'interest_rate': row[7],
                'total_payable': row[8],
                'purpose': row[9],
                'status': row[10],
                'approved_by': row[11],
                'approved_at': row[12],
                'repaid_amount': row[13],
                'is_repaid': bool(row[14]),
                'created_at': row[15]
            })
        return loans
    
    @staticmethod
    def find_pending_requests():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.username, u.email
            FROM loan_requests l
            JOIN users u ON l.user_id = u.id
            WHERE l.status = 'pending'
            ORDER BY l.created_at ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        loans = []
        for row in rows:
            loans.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'duration_days': row[6],
                'interest_rate': row[7],
                'total_payable': row[8],
                'purpose': row[9],
                'status': row[10],
                'approved_by': row[11],
                'approved_at': row[12],
                'repaid_amount': row[13],
                'is_repaid': bool(row[14]),
                'created_at': row[15],
                'username': row[16],
                'email': row[17]
            })
        return loans
    
    @staticmethod
    def find_active_loans():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.username, u.email
            FROM loan_requests l
            JOIN users u ON l.user_id = u.id
            WHERE l.status = 'approved' AND l.is_repaid = 0
            ORDER BY l.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        loans = []
        for row in rows:
            loans.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'duration_days': row[6],
                'interest_rate': row[7],
                'total_payable': row[8],
                'purpose': row[9],
                'status': row[10],
                'approved_by': row[11],
                'approved_at': row[12],
                'repaid_amount': row[13],
                'is_repaid': bool(row[14]),
                'created_at': row[15],
                'username': row[16],
                'email': row[17]
            })
        return loans
    
    @staticmethod
    def approve_loan(loan_id: int, admin_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE loan_requests 
            SET status = 'approved', approved_by = ?, approved_at = ?
            WHERE id = ?
        ''', (admin_id, datetime.now().isoformat(), loan_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def reject_loan(loan_id: int, admin_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE loan_requests 
            SET status = 'rejected', approved_by = ?, approved_at = ?
            WHERE id = ?
        ''', (admin_id, datetime.now().isoformat(), loan_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def mark_repaid(loan_id: int, amount: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE loan_requests 
            SET repaid_amount = ?, is_repaid = 1, status = 'repaid'
            WHERE id = ?
        ''', (amount, loan_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_loan_statistics():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM loan_requests')
        total_loans = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(CAST(amount AS REAL)) FROM loan_requests WHERE status = "approved"')
        total_volume = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM loan_requests WHERE status = "approved" AND is_repaid = 0')
        active_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM loan_requests WHERE is_repaid = 1')
        repaid_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM loan_requests WHERE status = "rejected"')
        rejected_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(CAST(interest_rate AS REAL) * CAST(amount AS REAL) / 100) FROM loan_requests WHERE is_repaid = 1')
        total_interest = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_loans': total_loans,
            'total_volume': total_volume,
            'active_count': active_count,
            'repaid_count': repaid_count,
            'rejected_count': rejected_count,
            'total_interest': total_interest
        }


class FlashLoanModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, network: str, token: str, amount: str, fee: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        
        if fee is None:
            fee = str(float(amount) * 0.001)  # 0.1% fee
        
        cursor.execute('''
            INSERT INTO flash_loans 
            (user_id, wallet_id, network, token, amount, fee, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, network, token, str(amount), str(fee), 'pending', datetime.now().isoformat()))
        loan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return loan_id
    
    @staticmethod
    def find_by_id(loan_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, u.username, u.email
            FROM flash_loans f
            JOIN users u ON f.user_id = u.id
            WHERE f.id = ?
        ''', (loan_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'fee': row[6],
                'status': row[7],
                'approved_by': row[8],
                'approved_at': row[9],
                'repaid_at': row[10],
                'tx_hash': row[11],
                'created_at': row[12],
                'username': row[13],
                'email': row[14]
            }
        return None
    
    @staticmethod
    def find_pending_requests():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, u.username, u.email
            FROM flash_loans f
            JOIN users u ON f.user_id = u.id
            WHERE f.status = 'pending'
            ORDER BY f.created_at ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        loans = []
        for row in rows:
            loans.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'token': row[4],
                'amount': row[5],
                'fee': row[6],
                'status': row[7],
                'approved_by': row[8],
                'approved_at': row[9],
                'repaid_at': row[10],
                'tx_hash': row[11],
                'created_at': row[12],
                'username': row[13],
                'email': row[14]
            })
        return loans
    
    @staticmethod
    def approve_flash_loan(loan_id: int, admin_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE flash_loans 
            SET status = 'approved', approved_by = ?, approved_at = ?
            WHERE id = ?
        ''', (admin_id, datetime.now().isoformat(), loan_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def mark_repaid(loan_id: int, tx_hash: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE flash_loans 
            SET status = 'repaid', repaid_at = ?, tx_hash = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), tx_hash, loan_id))
        conn.commit()
        conn.close()
        return True