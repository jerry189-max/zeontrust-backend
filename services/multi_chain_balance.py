import random
from models.wallet_models import NetworkAccountModel

class MultiChainBalance:
    
    PRICES = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
    SYMBOLS = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
    NAMES = {'tron': 'TRON', 'ethereum': 'Ethereum', 'bsc': 'BNB Chain', 'polygon': 'Polygon', 'bitcoin': 'Bitcoin'}
    
    @staticmethod
    def get_chain_summary(wallet_id: int) -> dict:
        accounts = NetworkAccountModel.find_by_wallet(wallet_id)
        
        chains = []
        total_usd = 0
        
        for account in accounts:
            symbol = MultiChainBalance.SYMBOLS.get(account['network'], 'TOKEN')
            balance = random.uniform(10, 1000)
            usd_value = balance * MultiChainBalance.PRICES.get(symbol, 1)
            total_usd += usd_value
            
            chains.append({
                'chain_id': account['network'],
                'chain_name': MultiChainBalance.NAMES.get(account['network'], account['network']),
                'address': account['address'],
                'balance': balance,
                'symbol': symbol,
                'usd_value': usd_value
            })
        
        return {'chains': chains, 'total_usd': total_usd}