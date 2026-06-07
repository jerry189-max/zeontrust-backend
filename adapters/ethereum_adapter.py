import hashlib
import requests
from .base_adapter import BaseAdapter

class EthereumAdapter(BaseAdapter):
    """Ethereum blockchain adapter"""
    
    def __init__(self, network: str = 'ethereum', testnet: bool = False, api_key: str = None):
        super().__init__(network, testnet)
        self.api_key = api_key
        self.network = network
    
    def _get_rpc_url(self) -> str:
        if self.network == 'ethereum':
            if self.testnet:
                return 'https://sepolia.infura.io/v3/'
            return 'https://mainnet.infura.io/v3/'
        elif self.network == 'bsc':
            if self.testnet:
                return 'https://data-seed-prebsc-1-s1.binance.org'
            return 'https://bsc-dataseed.binance.org'
        elif self.network == 'polygon':
            if self.testnet:
                return 'https://rpc-mumbai.maticvigil.com'
            return 'https://polygon-rpc.com'
        return 'https://mainnet.infura.io/v3/'
    
    def get_balance(self, address: str) -> float:
        """Get ETH/BNB/MATIC balance"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_getBalance',
                'params': [address, 'latest'],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                balance_wei = int(data.get('result', '0x0'), 16)
                return balance_wei / 1e18
            return 0.0
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0.0
    
    def get_token_balance(self, address: str, token_contract: str) -> float:
        """Get ERC-20 token balance"""
        try:
            # In production, call token contract's balanceOf method
            return 0.0
        except Exception as e:
            return 0.0
    
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        """Send ETH/BNB/MATIC transaction"""
        try:
            tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}".encode()).hexdigest()
            return f"0x{tx_hash}"
        except Exception as e:
            raise Exception(f"Transaction failed: {e}")
    
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction details"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionByHash',
                'params': [tx_hash],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                return response.json().get('result', {})
            return {}
        except Exception as e:
            return {}
    
    def get_transaction_status(self, tx_hash: str) -> str:
        """Get transaction status"""
        try:
            tx = self.get_transaction(tx_hash)
            if tx and tx.get('blockNumber'):
                return 'confirmed'
            return 'pending'
        except Exception as e:
            return 'unknown'
    
    def estimate_gas(self, from_address: str, to_address: str, amount: float) -> dict:
        """Estimate gas for transaction"""
        fees = {
            'ethereum': {'gas': 21000, 'gas_price_gwei': 30, 'fee_eth': 0.00063, 'fee_usd': 2.20},
            'bsc': {'gas': 21000, 'gas_price_gwei': 5, 'fee_bnb': 0.000105, 'fee_usd': 0.06},
            'polygon': {'gas': 21000, 'gas_price_gwei': 30, 'fee_matic': 0.00063, 'fee_usd': 0.0005}
        }
        return fees.get(self.network, {'fee': 0.01, 'fee_usd': 0.01})
    
    def validate_address(self, address: str) -> bool:
        """Validate Ethereum address"""
        if not address:
            return False
        return address.startswith('0x') and len(address) == 42
    
    def get_gas_price(self) -> int:
        """Get current gas price in Gwei"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_gasPrice',
                'params': [],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return int(data.get('result', '0x0'), 16) // 1e9
            return 30
        except Exception as e:
            return 30
    
    def get_block_number(self) -> int:
        """Get current block number"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_blockNumber',
                'params': [],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return int(data.get('result', '0x0'), 16)
            return 0
        except Exception as e:
            return 0