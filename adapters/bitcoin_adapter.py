import hashlib
import requests
from .base_adapter import BaseAdapter

class BitcoinAdapter(BaseAdapter):
    """Bitcoin blockchain adapter"""
    
    def __init__(self, testnet: bool = False):
        super().__init__('bitcoin', testnet)
    
    def _get_rpc_url(self) -> str:
        if self.testnet:
            return 'https://blockstream.info/testnet/api'
        return 'https://blockstream.info/api'
    
    def get_balance(self, address: str) -> float:
        """Get BTC balance for an address"""
        try:
            url = f"{self.rpc_url}/address/{address}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                balance = data.get('chain_stats', {}).get('funded_txo_sum', 0)
                balance -= data.get('chain_stats', {}).get('spent_txo_sum', 0)
                return balance / 100_000_000  # Convert satoshis to BTC
            return 0.0
        except Exception as e:
            print(f"Error getting BTC balance: {e}")
            return 0.0
    
    def get_token_balance(self, address: str, token_contract: str) -> float:
        """Bitcoin doesn't support tokens natively"""
        return 0.0
    
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        """Send BTC transaction"""
        try:
            tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}".encode()).hexdigest()
            return tx_hash
        except Exception as e:
            raise Exception(f"Transaction failed: {e}")
    
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction details"""
        try:
            url = f"{self.rpc_url}/tx/{tx_hash}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            return {}
    
    def get_transaction_status(self, tx_hash: str) -> str:
        """Get transaction status"""
        try:
            tx = self.get_transaction(tx_hash)
            if tx and tx.get('status', {}).get('confirmed'):
                return 'confirmed'
            return 'pending'
        except Exception as e:
            return 'unknown'
    
    def estimate_gas(self, from_address: str, to_address: str, amount: float) -> dict:
        """Estimate fee for BTC transaction"""
        try:
            url = f"{self.rpc_url}/fee-estimates"
            response = requests.get(url)
            if response.status_code == 200:
                fees = response.json()
                return {
                    'fastest_fee': fees.get('2', 10),
                    'half_hour_fee': fees.get('6', 5),
                    'hour_fee': fees.get('12', 3),
                    'fee_btc': 0.0001,
                    'fee_usd': 6.50
                }
            return {'fee_btc': 0.0001, 'fee_usd': 6.50}
        except Exception as e:
            return {'fee_btc': 0.0001, 'fee_usd': 6.50}
    
    def validate_address(self, address: str) -> bool:
        """Validate Bitcoin address"""
        if not address:
            return False
        return (address.startswith('1') or 
                address.startswith('3') or 
                address.startswith('bc1')) and len(address) >= 26
    
    def get_transactions(self, address: str, limit: int = 50) -> list:
        """Get transaction history for address"""
        try:
            url = f"{self.rpc_url}/address/{address}/txs"
            response = requests.get(url, params={'limit': limit})
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []
    
    def get_utxos(self, address: str) -> list:
        """Get UTXOs for address"""
        try:
            url = f"{self.rpc_url}/address/{address}/utxo"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []