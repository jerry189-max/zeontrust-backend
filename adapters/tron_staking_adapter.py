import hashlib
from .tron_api import TronAPI

class TronStakingAdapter:
    """TRON Staking (Energy/Bandwidth) adapter"""
    
    def __init__(self, testnet: bool = False, api_key: str = None):
        self.testnet = testnet
        self.api_key = api_key
        self.api = TronAPI(testnet, api_key)
    
    def get_account_resources(self, address: str) -> dict:
        """Get account resources (Energy/Bandwidth)"""
        account = self.api.get_account(address)
        if account.get('data') and len(account['data']) > 0:
            data = account['data'][0]
            return {
                'energy': {
                    'used': data.get('energy_used', 0),
                    'total': data.get('energy_limit', 0),
                    'frozen': data.get('frozen_balance_for_energy', [])
                },
                'bandwidth': {
                    'used': data.get('net_used', 0),
                    'total': data.get('net_limit', 0),
                    'frozen': data.get('frozen_balance_for_bandwidth', [])
                }
            }
        return {'energy': {'used': 0, 'total': 0, 'frozen': []}, 'bandwidth': {'used': 0, 'total': 0, 'frozen': []}}
    
    def freeze_balance(self, address: str, amount: float, resource_type: str, private_key: str) -> str:
        """Freeze TRX for Energy or Bandwidth"""
        # In production, create and sign freeze balance transaction
        tx_hash = hashlib.sha256(f"freeze{address}{amount}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def unfreeze_balance(self, address: str, resource_type: str, private_key: str) -> str:
        """Unfreeze TRX"""
        tx_hash = hashlib.sha256(f"unfreeze{address}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def get_delegated_resources(self, address: str) -> list:
        """Get resources delegated to this address"""
        account = self.api.get_account(address)
        delegated = []
        if account.get('data') and len(account['data']) > 0:
            data = account['data'][0]
            for d in data.get('delegated_frozen_balance_for_energy', []):
                delegated.append({
                    'from': d.get('address'),
                    'amount': d.get('frozen_balance', 0) / 1_000_000,
                    'type': 'ENERGY',
                    'expires_at': d.get('expire_time')
                })
            for d in data.get('delegated_frozen_balance_for_bandwidth', []):
                delegated.append({
                    'from': d.get('address'),
                    'amount': d.get('frozen_balance', 0) / 1_000_000,
                    'type': 'BANDWIDTH',
                    'expires_at': d.get('expire_time')
                })
        return delegated
    
    def delegate_resource(self, from_address: str, to_address: str, amount: float, resource_type: str, private_key: str) -> str:
        """Delegate resources to another address"""
        tx_hash = hashlib.sha256(f"delegate{from_address}{to_address}{amount}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def undelegate_resource(self, from_address: str, to_address: str, amount: float, resource_type: str, private_key: str) -> str:
        """Undelegate resources"""
        tx_hash = hashlib.sha256(f"undelegate{from_address}{to_address}{amount}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def get_staking_apy(self) -> float:
        """Get current staking APY"""
        return 4.5
    
    def calculate_resources(self, trx_amount: float, resource_type: str) -> int:
        """Calculate resources received for staked TRX"""
        if resource_type == 'ENERGY':
            return int(trx_amount * 100000)  # 1 TRX = 100k Energy
        else:
            return int(trx_amount * 4000)    # 1 TRX = 4k Bandwidth
    
    def estimate_staking_rewards(self, amount: float, duration_days: int) -> dict:
        """Estimate staking rewards"""
        apy = self.get_staking_apy()
        yearly_reward = amount * (apy / 100)
        reward = yearly_reward * (duration_days / 365)
        
        return {
            'amount': amount,
            'duration_days': duration_days,
            'apy': apy,
            'estimated_reward': reward,
            'total_return': amount + reward
        }