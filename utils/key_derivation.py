import hashlib
import hmac
import secrets

class KeyDerivationUtils:
    """Utility functions for key derivation (BIP32, BIP39, BIP44)"""
    
    # BIP44 coin types
    COIN_TYPES = {
        'bitcoin': 0,
        'ethereum': 60,
        'bsc': 60,
        'polygon': 60,
        'tron': 195
    }
    
    @classmethod
    def mnemonic_to_seed(cls, mnemonic: str, passphrase: str = '') -> bytes:
        """Convert mnemonic to seed (BIP39)"""
        normalized_mnemonic = mnemonic.strip().lower()
        return hashlib.pbkdf2_hmac(
            'sha512',
            normalized_mnemonic.encode(),
            f'mnemonic{passphrase}'.encode(),
            2048
        )
    
    @classmethod
    def seed_to_master_key(cls, seed: bytes) -> tuple:
        """Derive master key from seed"""
        h = hmac.new(b'ed25519 seed', seed, hashlib.sha512).digest()
        master_key = h[:32]
        chain_code = h[32:]
        return master_key, chain_code
    
    @classmethod
    def derive_child_key(cls, parent_key: bytes, parent_chain: bytes, index: int, hardened: bool = False) -> tuple:
        """Derive child key (BIP32)"""
        if hardened:
            index += 0x80000000
        data = parent_key + index.to_bytes(4, 'big')
        h = hmac.new(parent_chain, data, hashlib.sha512).digest()
        child_key = h[:32]
        child_chain = h[32:]
        return child_key, child_chain
    
    @classmethod
    def derive_path(cls, master_key: bytes, chain_code: bytes, path: str) -> tuple:
        """Derive key from BIP44 path"""
        key = master_key
        cc = chain_code
        
        parts = path.split('/')
        for part in parts:
            if part == 'm':
                continue
            hardened = part.endswith("'")
            index = int(part.replace("'", ""))
            key, cc = cls.derive_child_key(key, cc, index, hardened)
        
        return key, cc
    
    @classmethod
    def get_bip44_path(cls, coin_type: str, account: int = 0, change: int = 0, address_index: int = 0) -> str:
        """Get BIP44 derivation path"""
        coin = cls.COIN_TYPES.get(coin_type, 60)
        return f"m/44'/{coin}'/{account}'/{change}/{address_index}"
    
    @classmethod
    def private_key_to_address(cls, private_key: str, network: str) -> str:
        """Convert private key to address"""
        # Mock implementation - in production use proper cryptography
        if network == 'tron':
            return 'T' + hashlib.sha256(private_key.encode()).hexdigest()[:33]
        else:
            return '0x' + hashlib.sha256(private_key.encode()).hexdigest()[:40]
    
    @classmethod
    def generate_master_key_from_seed(cls, seed: bytes) -> dict:
        """Generate master key from seed"""
        master_key, chain_code = cls.seed_to_master_key(seed)
        return {
            'master_key': master_key.hex(),
            'chain_code': chain_code.hex()
        }
    
    @classmethod
    def derive_wallet_keys(cls, mnemonic: str, passphrase: str = '', networks: list = None) -> dict:
        """Derive wallet keys for all networks"""
        if networks is None:
            networks = ['tron', 'ethereum', 'bsc', 'polygon', 'bitcoin']
        
        seed = cls.mnemonic_to_seed(mnemonic, passphrase)
        master_key, chain_code = cls.seed_to_master_key(seed)
        
        wallet_keys = {}
        for network in networks:
            path = cls.get_bip44_path(network)
            key, _ = cls.derive_path(master_key, chain_code, path)
            address = cls.private_key_to_address(key.hex(), network)
            wallet_keys[network] = {
                'path': path,
                'private_key': key.hex(),
                'address': address
            }
        
        return wallet_keys