import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class PoolModel:
    
    @staticmethod
    def create(network: str, token_a_address: str, token_a_symbol: str, 
               token_b_address: str, token_b_symbol: str, reserve_a: str, 
               reserve_b: str, total_liquidity: str, fee_percent: float = 0.3, 
               created_by: int = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pools 
            (network, token_a_address, token_a_symbol, token_b_address, token_b_symbol, 
             reserve_a, reserve_b, total_liquidity, fee_percent, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (network, token_a_address, token_a_symbol, token_b_address, token_b_symbol,
              reserve_a, reserve_b, total_liquidity, fee_percent, created_by, datetime.now().isoformat()))
        pool_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pool_id
    
    @staticmethod
    def find_by_id(pool_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pools WHERE id = ?', (pool_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'network': row[1],
                'token_a_address': row[2],
                'token_a_symbol': row[3],
                'token_b_address': row[4],
                'token_b_symbol': row[5],
                'reserve_a': row[6],
                'reserve_b': row[7],
                'total_liquidity': row[8],
                'fee_percent': row[9],
                'is_active': bool(row[10]),
                'created_at': row[11],
                'created_by': row[12]
            }
        return None
    
    @staticmethod
    def find_by_tokens(network: str, token_a: str, token_b: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM pools 
            WHERE network = ? AND ((token_a_address = ? AND token_b_address = ?) OR (token_a_address = ? AND token_b_address = ?))
        ''', (network, token_a, token_b, token_b, token_a))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'network': row[1],
                'token_a_address': row[2],
                'token_a_symbol': row[3],
                'token_b_address': row[4],
                'token_b_symbol': row[5],
                'reserve_a': row[6],
                'reserve_b': row[7],
                'total_liquidity': row[8],
                'fee_percent': row[9],
                'is_active': bool(row[10]),
                'created_at': row[11],
                'created_by': row[12]
            }
        return None
    
    @staticmethod
    def get_all_pools(network: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if network:
            cursor.execute('SELECT * FROM pools WHERE network = ? AND is_active = 1 ORDER BY created_at DESC', (network,))
        else:
            cursor.execute('SELECT * FROM pools WHERE is_active = 1 ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        pools = []
        for row in rows:
            pools.append({
                'id': row[0],
                'network': row[1],
                'token_a_address': row[2],
                'token_a_symbol': row[3],
                'token_b_address': row[4],
                'token_b_symbol': row[5],
                'reserve_a': row[6],
                'reserve_b': row[7],
                'total_liquidity': row[8],
                'fee_percent': row[9],
                'is_active': bool(row[10]),
                'created_at': row[11],
                'created_by': row[12]
            })
        return pools
    
    @staticmethod
    def update_reserves(pool_id: int, reserve_a: str, reserve_b: str, total_liquidity: str):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pools 
            SET reserve_a = ?, reserve_b = ?, total_liquidity = ?
            WHERE id = ?
        ''', (reserve_a, reserve_b, total_liquidity, pool_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update_pool_status(pool_id: int, is_active: bool):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE pools SET is_active = ? WHERE id = ?', (1 if is_active else 0, pool_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_pool_count():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM pools WHERE is_active = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def get_total_value_locked():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(CAST(reserve_a AS REAL) + CAST(reserve_b AS REAL)) FROM pools')
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total


class LiquidityPositionModel:
    
    @staticmethod
    def create(pool_id: int, user_id: int, wallet_id: int, lp_token_amount: str, 
               amount_a: str, amount_b: str, lp_token_address: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO liquidity_positions 
            (pool_id, user_id, wallet_id, lp_token_address, lp_token_amount, amount_a, amount_b, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pool_id, user_id, wallet_id, lp_token_address, lp_token_amount, amount_a, amount_b, datetime.now().isoformat()))
        position_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return position_id
    
    @staticmethod
    def find_by_user(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, p.token_a_symbol, p.token_b_symbol, p.network
            FROM liquidity_positions l
            JOIN pools p ON l.pool_id = p.id
            WHERE l.user_id = ?
            ORDER BY l.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'pool_id': row[1],
                'user_id': row[2],
                'wallet_id': row[3],
                'lp_token_address': row[4],
                'lp_token_amount': row[5],
                'amount_a': row[6],
                'amount_b': row[7],
                'created_at': row[8],
                'token_a_symbol': row[9],
                'token_b_symbol': row[10],
                'network': row[11]
            })
        return positions
    
    @staticmethod
    def find_by_pool(pool_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.username
            FROM liquidity_positions l
            JOIN users u ON l.user_id = u.id
            WHERE l.pool_id = ?
            ORDER BY l.created_at DESC
        ''', (pool_id,))
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'pool_id': row[1],
                'user_id': row[2],
                'wallet_id': row[3],
                'lp_token_address': row[4],
                'lp_token_amount': row[5],
                'amount_a': row[6],
                'amount_b': row[7],
                'created_at': row[8],
                'username': row[9]
            })
        return positions
    
    @staticmethod
    def find_by_id(position_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM liquidity_positions WHERE id = ?', (position_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'pool_id': row[1],
                'user_id': row[2],
                'wallet_id': row[3],
                'lp_token_address': row[4],
                'lp_token_amount': row[5],
                'amount_a': row[6],
                'amount_b': row[7],
                'created_at': row[8]
            }
        return None
    
    @staticmethod
    def delete_position(position_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM liquidity_positions WHERE id = ? AND user_id = ?', (position_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class SwapModel:
    
    @staticmethod
    def create(user_id: int, wallet_id: int, pool_id: int, from_token: str, 
               to_token: str, from_amount: str, to_amount: str, fee: str, tx_hash: str = None) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO swaps 
            (user_id, wallet_id, pool_id, from_token, to_token, from_amount, to_amount, fee, tx_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_id, pool_id, from_token, to_token, from_amount, to_amount, fee, tx_hash, datetime.now().isoformat()))
        swap_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return swap_id
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 50):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, p.token_a_symbol, p.token_b_symbol
            FROM swaps s
            JOIN pools p ON s.pool_id = p.id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        swaps = []
        for row in rows:
            swaps.append({
                'id': row[0],
                'user_id': row[1],
                'wallet_id': row[2],
                'pool_id': row[3],
                'from_token': row[4],
                'to_token': row[5],
                'from_amount': row[6],
                'to_amount': row[7],
                'fee': row[8],
                'tx_hash': row[9],
                'created_at': row[10],
                'token_a_symbol': row[11],
                'token_b_symbol': row[12]
            })
        return swaps
    
    @staticmethod
    def get_swap_volume(days: int = 7):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(CAST(from_amount AS REAL)) as volume, DATE(created_at) as date
            FROM swaps
            WHERE created_at >= DATE('now', ?)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''', (f'-{days} days',))
        rows = cursor.fetchall()
        conn.close()
        volume = []
        for row in rows:
            volume.append({
                'date': row[1],
                'volume': row[0] or 0
            })
        return volume