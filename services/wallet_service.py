import hashlib
import secrets
from datetime import datetime
from models.wallet_models import WalletModel, NetworkAccountModel

class WalletService:
    
    @staticmethod
    def create_wallet(user_id: int, wallet_name: str, mnemonic: str = None) -> dict:
        if not mnemonic:
            mnemonic = MnemonicService.generate_mnemonic()
        
        wallet_id = WalletModel.create(user_id, wallet_name, mnemonic)
        
        addresses = WalletService.generate_addresses(user_id, wallet_id, wallet_name)
        
        return {
            'wallet_id': wallet_id,
            'wallet_name': wallet_name,
            'mnemonic': mnemonic,
            'addresses': addresses
        }
    
    @staticmethod
    def generate_addresses(user_id: int, wallet_id: int, wallet_name: str) -> dict:
        seed = f"{user_id}{wallet_id}{wallet_name}{datetime.now()}".encode()
        
        addresses = {
            'tron': 'T' + hashlib.sha256(seed).hexdigest()[:33],
            'ethereum': '0x' + hashlib.sha256(seed).hexdigest()[:40],
            'bsc': '0x' + hashlib.sha256(seed).hexdigest()[:40],
            'polygon': '0x' + hashlib.sha256(seed).hexdigest()[:40],
            'bitcoin': '1' + hashlib.sha256(seed).hexdigest()[:33]
        }
        
        for network, address in addresses.items():
            NetworkAccountModel.create(wallet_id, network, address)
        
        return addresses
    
    @staticmethod
    def get_wallet_by_id(wallet_id: int, user_id: int) -> dict:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            return None
        addresses = NetworkAccountModel.find_by_wallet(wallet_id)
        wallet['addresses'] = addresses
        return wallet
    
    @staticmethod
    def get_user_wallets(user_id: int) -> list:
        return WalletModel.find_by_user(user_id)
    
    @staticmethod
    def backup_wallet(wallet_id: int, user_id: int) -> bool:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            return False
        WalletModel.update_backup_status(wallet_id, True)
        return True
    
    @staticmethod
    def delete_wallet(wallet_id: int, user_id: int) -> bool:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            return False
        WalletModel.delete_wallet(wallet_id)
        return True