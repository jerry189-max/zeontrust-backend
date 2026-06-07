import random

class BalanceService:
    
    PRICES = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000, 'USDT': 1.00}
    
    def __init__(self, network: str, testnet: bool = False):
        self.network = network
        self.testnet = testnet
        self.symbols = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
    
    def get_native_balance(self, address: str) -> float:
        return round(random.uniform(10, 1000), 2)
    
    def get_token_balance(self, address: str, token_contract: str) -> float:
        return round(random.uniform(0, 100), 2)
    
    def get_usd_value(self, balance: float, symbol: str) -> float:
        return balance * self.PRICES.get(symbol, 1)
    
    def get_all_balances(self, address: str, tokens: list) -> list:
        balances = []
        native_balance = self.get_native_balance(address)
        symbol = self.symbols.get(self.network, 'TOKEN')
        balances.append({
            'symbol': symbol,
            'name': self.network.capitalize(),
            'balance': native_balance,
            'usd_value': self.get_usd_value(native_balance, symbol),
            'is_native': True
        })
        
        for token in tokens:
            token_balance = self.get_token_balance(address, token.get('contract_address', ''))
            balances.append({
                'symbol': token.get('token_symbol', 'TOKEN'),
                'name': token.get('token_name', 'Token'),
                'balance': token_balance,
                'usd_value': self.get_usd_value(token_balance, token.get('token_symbol', 'TOKEN')),
                'is_native': False
            })
        
        return balances