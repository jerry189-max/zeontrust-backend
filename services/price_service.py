import requests

class PriceService:
    
    PRICES = {
        'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000,
        'USDT': 1.00, 'USDC': 1.00, 'DAI': 1.00, 'BUSD': 1.00
    }
    
    @staticmethod
    def get_price(token: str, source: str = 'auto') -> float:
        return PriceService.PRICES.get(token.upper(), 0)
    
    @staticmethod
    def get_all_prices() -> dict:
        return PriceService.PRICES.copy()
    
    @staticmethod
    def get_historical_coingecko(token: str, days: int = 7) -> list:
        history = []
        base_price = PriceService.PRICES.get(token.upper(), 0.10)
        for i in range(days):
            history.append({
                'date': f'2024-01-{i+1}',
                'price': round(base_price * (1 + (i * 0.01)), 4)
            })
        return history