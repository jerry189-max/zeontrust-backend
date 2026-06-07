from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """Base adapter for all blockchain networks"""
    
    def __init__(self, network: str, testnet: bool = False):
        self.network = network
        self.testnet = testnet
        self.rpc_url = self._get_rpc_url()
    
    @abstractmethod
    def _get_rpc_url(self) -> str:
        """Get RPC URL for the network"""
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> float:
        """Get native balance for an address"""
        pass
    
    @abstractmethod
    def get_token_balance(self, address: str, token_contract: str) -> float:
        """Get token balance for an address"""
        pass
    
    @abstractmethod
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        """Send a transaction"""
        pass
    
    @abstractmethod
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction details"""
        pass
    
    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> str:
        """Get transaction status"""
        pass
    
    @abstractmethod
    def estimate_gas(self, from_address: str, to_address: str, amount: float) -> dict:
        """Estimate gas for transaction"""
        pass
    
    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate blockchain address"""
        pass
    
    def get_network_info(self) -> dict:
        """Get network information"""
        return {
            'network': self.network,
            'testnet': self.testnet,
            'rpc_url': self.rpc_url
        }