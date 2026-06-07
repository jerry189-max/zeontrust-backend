import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    return sqlite3.connect(DB_PATH)

class AddressBookModel:
    
    @staticmethod
    def create(user_id: int, name: str, address: str, network: str, notes: str = None, favorite: bool = False) -> int:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO address_book (user_id, name, address, network, notes, favorite, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, address, network, notes, 1 if favorite else 0, datetime.now().isoformat()))
        address_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return address_id
    
    @staticmethod
    def find_by_user(user_id: int, network: str = None):
        conn = get_db()
        cursor = conn.cursor()
        if network:
            cursor.execute('''
                SELECT * FROM address_book 
                WHERE user_id = ? AND network = ? 
                ORDER BY favorite DESC, name ASC
            ''', (user_id, network))
        else:
            cursor.execute('''
                SELECT * FROM address_book 
                WHERE user_id = ? 
                ORDER BY favorite DESC, name ASC
            ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        addresses = []
        for row in rows:
            addresses.append({
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'address': row[3],
                'network': row[4],
                'notes': row[5],
                'favorite': bool(row[6]),
                'created_at': row[7]
            })
        return addresses
    
    @staticmethod
    def find_favorites(user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM address_book 
            WHERE user_id = ? AND favorite = 1 
            ORDER BY name ASC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        addresses = []
        for row in rows:
            addresses.append({
                'id': row[0],
                'name': row[2],
                'address': row[3],
                'network': row[4]
            })
        return addresses
    
    @staticmethod
    def find_by_id(address_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM address_book WHERE id = ?', (address_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'address': row[3],
                'network': row[4],
                'notes': row[5],
                'favorite': bool(row[6]),
                'created_at': row[7]
            }
        return None
    
    @staticmethod
    def update(address_id: int, user_id: int, name: str = None, address: str = None, 
               network: str = None, notes: str = None, favorite: bool = None):
        conn = get_db()
        cursor = conn.cursor()
        updates = []
        values = []
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if address is not None:
            updates.append("address = ?")
            values.append(address)
        if network is not None:
            updates.append("network = ?")
            values.append(network)
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
        if favorite is not None:
            updates.append("favorite = ?")
            values.append(1 if favorite else 0)
        
        if updates:
            values.extend([address_id, user_id])
            cursor.execute(f'UPDATE address_book SET {", ".join(updates)} WHERE id = ? AND user_id = ?', values)
            conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(address_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM address_book WHERE id = ? AND user_id = ?', (address_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    @staticmethod
    def toggle_favorite(address_id: int, user_id: int):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT favorite FROM address_book WHERE id = ? AND user_id = ?', (address_id, user_id))
        row = cursor.fetchone()
        if row:
            new_favorite = 0 if row[0] else 1
            cursor.execute('UPDATE address_book SET favorite = ? WHERE id = ? AND user_id = ?', 
                          (new_favorite, address_id, user_id))
            conn.commit()
        conn.close()
        return True