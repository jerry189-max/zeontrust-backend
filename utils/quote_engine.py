import random

class QuoteEngine:
    """Quote engine for swap prices and calculations"""
    
    # Mock prices - in production fetch from oracles
    PRICES = {
        'TRX': 0.10,
        'USDT': 1.00,
        'USDC': 1.00,
        'ETH': 3500,
        'BNB': 600,
        'MATIC': 0.80,
        'BTC': 65000,
        'DAI': 1.00,
        'BUSD': 1.00
    }
    
    @classmethod
    def get_price(cls, token: str) -> float:
        """Get token price in USD"""
        return cls.PRICES.get(token.upper(), 0)
    
    @classmethod
    def get_quote(cls, from_token: str, to_token: str, amount: float, slippage: float = 0.5) -> dict:
        """Get swap quote"""
        from_price = cls.get_price(from_token)
        to_price = cls.get_price(to_token)
        
        if from_price == 0 or to_price == 0:
            return None
        
        # Calculate expected output
        expected_output = (amount * from_price) / to_price
        
        # Add slippage
        min_output = expected_output * (1 - slippage / 100)
        
        # Estimate fee
        fee = amount * 0.003  # 0.3% fee
        fee_usd = fee * from_price
        
        return {
            'from_token': from_token.upper(),
            'to_token': to_token.upper(),
            'from_amount': amount,
            'to_amount': expected_output,
            'min_received': min_output,
            'price': from_price / to_price if to_price > 0 else 0,
            'price_usd': to_price,
            'fee': fee,
            'fee_usd': fee_usd,
            'fee_percent': 0.3,
            'slippage': slippage,
            'provider': 'ZeontrustSwap'
        }
    
    @classmethod
    def get_route(cls, from_token: str, to_token: str, amount: float) -> list:
        """Get best swap route"""
        # Simple direct route - in production use multi-hop routing
        return [
            {
                'from': from_token.upper(),
                'to': to_token.upper(),
                'amount_in': amount,
                'amount_out': amount * cls.get_price(from_token) / cls.get_price(to_token),
                'pool': f"{from_token.upper()}/{to_token.upper()}"
            }
        ]
    
    @classmethod
    def get_liquidity(cls, token: str) -> float:
        """Get liquidity for token"""
        # Mock liquidity data
        liquidity = {
            'TRX': 10000000,
            'USDT': 5000000,
            'ETH': 10000,
            'BNB': 50000,
            'MATIC': 2000000
        }
        return liquidity.get(token.upper(), 100000)
    
    @classmethod
    def calculate_price_impact(cls, from_token: str, to_token: str, amount: float) -> float:
        """Calculate price impact for swap"""
        liquidity = cls.get_liquidity(from_token)
        if liquidity == 0:
            return 100
        
        impact = (amount / liquidity) * 100
        return min(impact, 50)
    
    @classmethod
    def get_market_depth(cls, token: str) -> dict:
        """Get market depth for token"""
        return {
            'token': token.upper(),
            'bid': cls.get_price(token) * 0.99,
            'ask': cls.get_price(token) * 1.01,
            'depth': cls.get_liquidity(token) * cls.get_price(token)
        }