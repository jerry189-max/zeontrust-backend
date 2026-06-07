import hashlib
import hmac

class KeyDerivationService:
    
    @staticmethod
    def derive_master_key(seed: bytes) -> tuple:
        master_key = hashlib.pbkdf2_hmac('sha512', seed, b'ed25519 seed', 2048)
        return master_key[:32], master_key[32:]
    
    @staticmethod
    def derive_path(master_key: bytes, path: str) -> bytes:
        key = master_key
        for segment in path.split('/'):
            if segment == 'm':
                continue
            key = KeyDerivationService.derive_child_key(key, int(segment))
        return key
    
    @staticmethod
    def derive_child_key(parent_key: bytes, index: int) -> bytes:
        data = parent_key + index.to_bytes(4, 'big')
        child_key = hashlib.sha256(data).digest()
        return child_key
    
    @staticmethod
    def get_derivation_path(network: str) -> str:
        paths = {
            'tron': "m/44'/195'/0'/0/0",
            'ethereum': "m/44'/60'/0'/0/0",
            'bsc': "m/44'/60'/0'/0/0",
            'polygon': "m/44'/60'/0'/0/0",
            'bitcoin': "m/44'/0'/0'/0/0"
        }
        return paths.get(network, "m/44'/0'/0'/0/0")
    
    @staticmethod
    def private_key_to_address(private_key: str, network: str) -> str:
        # Mock address generation
        if network == 'tron':
            return 'T' + hashlib.sha256(private_key.encode()).hexdigest()[:33]
        else:
            return '0x' + hashlib.sha256(private_key.encode()).hexdigest()[:40]