import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class StakingPositionModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, network: str, amount: str, 
               resource_type: str = 'ENERGY', duration_days: int = 90, tx_hash: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        unlocked_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        cursor.execute('''
            INSERT INTO staking_positions 
            (user_id, wallet_id, network, amount, resource_type, duration_days, tx_hash, status, created_at, unlocked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, network, amount, resource_type, duration_days, tx_hash, 'active', 
              datetime.now().isoformat(), unlocked_at))
        position_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return position_id
    
    @staticmethod
    def find_by_id(position_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staking_positions WHERE id = ?', (position_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'amount': row[4],
                'resource_type': row[5],
                'duration_days': row[6],
                'tx_hash': row[7],
                'status': row[8],
                'created_at': row[9],
                'unlocked_at': row[10]
            }
        return None
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staking_positions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'amount': row[4],
                'resource_type': row[5],
                'duration_days': row[6],
                'tx_hash': row[7],
                'status': row[8],
                'created_at': row[9],
                'unlocked_at': row[10]
            })
        return positions
    
    @staticmethod
    def find_by_wallet(wallet_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staking_positions WHERE wallet_id = ? ORDER BY created_at DESC', (wallet_id,))
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'amount': row[4],
                'resource_type': row[5],
                'duration_days': row[6],
                'tx_hash': row[7],
                'status': row[8],
                'created_at': row[9],
                'unlocked_at': row[10]
            })
        return positions
    
    @staticmethod
    def find_active_positions(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM staking_positions 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'network': row[3],
                'amount': row[4],
                'resource_type': row[5],
                'duration_days': row[6],
                'tx_hash': row[7],
                'status': row[8],
                'created_at': row[9],
                'unlocked_at': row[10]
            })
        return positions
    
    @staticmethod
    def unstake_position(position_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE staking_positions SET status = "unstaked" WHERE id = ?', (position_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_total_staked(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(CAST(amount AS REAL)) FROM staking_positions WHERE user_id = ? AND status = "active"', (user_id,))
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    @staticmethod
    def get_staking_apy():
        return 4.5  # 4.5% APY