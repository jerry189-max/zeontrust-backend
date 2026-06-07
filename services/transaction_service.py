import hashlib
import time
from models.transaction_models import TransactionModel
from models.wallet_models import WalletModel, NetworkAccountModel

class TransactionService:
    
    @staticmethod
    def create_transaction(wallet_id: int, network: str, to_address: str, amount: str, 
                          token_address: str = None, fee: str = None) -> dict:
        account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
        if not account:
            raise ValueError(f'Network {network} not found')
        
        from_address = account['address']
        tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}{time.time()}".encode()).hexdigest()
        
        tx_id = TransactionModel.create(wallet_id, network, tx_hash, from_address, to_address, amount, token_address, fee=fee)
        
        return {'tx_id': tx_id, 'tx_hash': tx_hash, 'from_address': from_address, 'to_address': to_address, 'amount': amount}
    
    @staticmethod
    def get_transaction(tx_hash: str) -> dict:
        return TransactionModel.find_by_hash(tx_hash)
    
    @staticmethod
    def get_wallet_transactions(wallet_id: int, limit: int = 50) -> list:
        return TransactionModel.find_by_wallet(wallet_id, limit)
    
    @staticmethod
    def get_user_transactions(user_id: int, limit: int = 50) -> list:
        return TransactionModel.find_by_user(user_id, limit)
    
    @staticmethod
    def update_transaction_status(tx_hash: str, status: str, block_number: int = None) -> bool:
        return TransactionModel.update_status(tx_hash, status, block_number)
    
    @staticmethod
    def estimate_fee(network: str, from_address: str, to_address: str, amount: str) -> dict:
        fees = {
            'tron': {'fee': 0.5, 'symbol': 'TRX'},
            'ethereum': {'fee': 0.002, 'symbol': 'ETH'},
            'bsc': {'fee': 0.0005, 'symbol': 'BNB'},
            'polygon': {'fee': 0.001, 'symbol': 'MATIC'},
            'bitcoin': {'fee': 0.0001, 'symbol': 'BTC'}
        }
        return fees.get(network, {'fee': 0.01, 'symbol': 'TOKEN'})