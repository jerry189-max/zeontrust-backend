import hashlib

class TransactionSigner:
    
    def __init__(self, network: str):
        self.network = network
    
    def sign_transaction(self, raw_transaction: dict, private_key: str) -> dict:
        tx_string = f"{raw_transaction}{private_key}"
        signature = hashlib.sha256(tx_string.encode()).hexdigest()
        
        return {
            'raw': raw_transaction,
            'signature': signature,
            'signed_transaction': {
                'from': raw_transaction.get('from'),
                'to': raw_transaction.get('to'),
                'value': raw_transaction.get('value'),
                'signature': signature
            }
        }