import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class NotificationModel:
    
    @staticmethod
    def create(user_id: int, type: str, title: str, message: str, data: dict = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, type, title, message, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, type, title, message, json.dumps(data) if data else None, datetime.now().isoformat()))
        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return notif_id
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 20, unread_only: bool = False):
        conn = get_db()
        cursor = conn.cursor()
        if unread_only:
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = 0 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        notifications = []
        for row in rows:
            notifications.append({
                'id': row[0],
                'user_id': row[1],
                'type': row[2],
                'title': row[3],
                'message': row[4],
                'data': json.loads(row[5]) if row[5] else {},
                'is_read': bool(row[6]),
                'created_at': row[7]
            })
        return notifications
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', (notification_id, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def mark_all_read(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(notification_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notifications WHERE id = ? AND user_id = ?', (notification_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    @staticmethod
    def get_unread_count(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def create_transaction_notification(user_id: int, tx_hash: str, amount: str, status: str):
        title = f"Transaction {status}"
        message = f"Transaction {tx_hash[:10]}... of {amount} is {status}"
        return NotificationModel.create(user_id, 'transaction', title, message, {'tx_hash': tx_hash, 'amount': amount, 'status': status})
    
    @staticmethod
    def create_token_approval_notification(user_id: int, token_name: str, status: str, notes: str = None):
        title = f"Token {status}"
        message = f"Your token {token_name} has been {status}"
        if notes:
            message += f". Notes: {notes}"
        return NotificationModel.create(user_id, 'token', title, message, {'token_name': token_name, 'status': status})
    
    @staticmethod
    def create_loan_notification(user_id: int, loan_id: int, amount: str, status: str):
        title = f"Loan {status}"
        message = f"Your loan of {amount} has been {status}"
        return NotificationModel.create(user_id, 'loan', title, message, {'loan_id': loan_id, 'amount': amount, 'status': status})