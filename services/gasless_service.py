import hashlib
import time

class GaslessService:
    
    @staticmethod
    def send_gasless_transaction(user_id: int, from_address: str, to_address: str, amount: str) -> dict:
        tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}{time.time()}".encode()).hexdigest()
        
        return {
            'success': True,
            'tx_hash': tx_hash,
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'gas_saved': 0.5,
            'message': 'GasFree transaction sent successfully!'
        }
    
    @staticmethod
    def get_remaining_free_transactions(user_id: int) -> int:
        return 10
    
    @staticmethod
    def get_total_gas_saved(user_id: int) -> float:
        return 2.5