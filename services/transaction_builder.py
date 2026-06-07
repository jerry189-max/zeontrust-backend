import time

class TransactionBuilder:
    
    def __init__(self, network: str, testnet: bool = False):
        self.network = network
        self.testnet = testnet
    
    def build_transaction(self, from_address: str, to_address: str, amount: str, 
                         data: str = None, token_contract: str = None) -> dict:
        return {
            'from': from_address,
            'to': to_address,
            'value': amount,
            'data': data,
            'token': token_contract,
            'nonce': int(time.time()),
            'network': self.network,
            'testnet': self.testnet
        }
    
    def estimate_fee(self, from_address: str, to_address: str, amount: str, token_contract: str = None) -> dict:
        fees = {
            'tron': {'fee_trx': 0.5, 'fee_usd': 0.05},
            'ethereum': {'fee_eth': 0.002, 'fee_usd': 7.00},
            'bsc': {'fee_bnb': 0.0005, 'fee_usd': 0.30},
            'polygon': {'fee_matic': 0.001, 'fee_usd': 0.0008},
            'bitcoin': {'fee_btc': 0.0001, 'fee_usd': 6.50}
        }
        return fees.get(self.network, {'fee': 0.01, 'fee_usd': 0.01})