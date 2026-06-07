import random
from models.wallet_models import NetworkAccountModel

class PortfolioService:
    
    PRICES = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
    SYMBOLS = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
    
    @staticmethod
    def get_total_portfolio(wallet_id: int) -> dict:
        accounts = NetworkAccountModel.find_by_wallet(wallet_id)
        
        total_value = 0
        assets = []
        
        for account in accounts:
            symbol = PortfolioService.SYMBOLS.get(account['network'], 'TOKEN')
            balance = random.uniform(10, 1000)
            price = PortfolioService.PRICES.get(symbol, 1)
            usd_value = balance * price
            total_value += usd_value
            
            assets.append({
                'network': account['network'],
                'address': account['address'],
                'symbol': symbol,
                'balance': balance,
                'price': price,
                'usd_value': usd_value
            })
        
        return {'total_value': total_value, 'assets': assets}
    
    @staticmethod
    def get_portfolio_history(wallet_id: int, days: int = 30) -> list:
        history = []
        for i in range(days):
            history.append({
                'date': f'2024-01-{i+1}',
                'value': random.uniform(100, 1000)
            })
        return history