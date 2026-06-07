import re

class Validators:
    """Validation utility functions"""
    
    # Address patterns for different networks
    ADDRESS_PATTERNS = {
        'tron': r'^T[A-Za-z0-9]{33}$',
        'ethereum': r'^0x[a-fA-F0-9]{40}$',
        'bsc': r'^0x[a-fA-F0-9]{40}$',
        'polygon': r'^0x[a-fA-F0-9]{40}$',
        'bitcoin': r'^[13][a-km-zA-HJ-NP-Z0-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{39,59}$'
    }
    
    # Transaction hash patterns
    TX_HASH_PATTERNS = {
        'tron': r'^[a-fA-F0-9]{64}$',
        'ethereum': r'^0x[a-fA-F0-9]{64}$',
        'bsc': r'^0x[a-fA-F0-9]{64}$',
        'polygon': r'^0x[a-fA-F0-9]{64}$',
        'bitcoin': r'^[a-fA-F0-9]{64}$'
    }
    
    @classmethod
    def validate_address(cls, address: str, network: str) -> bool:
        """Validate blockchain address"""
        if not address:
            return False
        
        pattern = cls.ADDRESS_PATTERNS.get(network)
        if not pattern:
            return False
        
        return bool(re.match(pattern, address))
    
    @classmethod
    def validate_tx_hash(cls, tx_hash: str, network: str) -> bool:
        """Validate transaction hash"""
        if not tx_hash:
            return False
        
        pattern = cls.TX_HASH_PATTERNS.get(network)
        if not pattern:
            return False
        
        return bool(re.match(pattern, tx_hash))
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_password(cls, password: str) -> tuple:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @classmethod
    def validate_amount(cls, amount: float, min_amount: float = 0, max_amount: float = None) -> tuple:
        """Validate amount"""
        if amount <= 0:
            return False, "Amount must be greater than 0"
        
        if amount < min_amount:
            return False, f"Amount must be at least {min_amount}"
        
        if max_amount and amount > max_amount:
            return False, f"Amount cannot exceed {max_amount}"
        
        return True, "Amount is valid"
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL"""
        if not url:
            return False
        pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
        return bool(re.match(pattern, url))
    
    @classmethod
    def validate_contract_address(cls, contract_address: str, network: str) -> bool:
        """Validate token contract address"""
        return cls.validate_address(contract_address, network)
    
    @classmethod
    def validate_mnemonic(cls, mnemonic: str) -> tuple:
        """Validate mnemonic phrase"""
        if not mnemonic:
            return False, "Mnemonic is required"
        
        words = mnemonic.strip().lower().split()
        if len(words) != 12 and len(words) != 15 and len(words) != 18 and len(words) != 24:
            return False, "Mnemonic must be 12, 15, 18, or 24 words"
        
        return True, "Mnemonic is valid"
    
    @classmethod
    def validate_private_key(cls, private_key: str, network: str) -> bool:
        """Validate private key format"""
        if not private_key:
            return False
        
        if network == 'tron':
            return len(private_key) == 64 or len(private_key) == 128
        else:
            return private_key.startswith('0x') and len(private_key) == 66
    
    @classmethod
    def detect_network(cls, address: str) -> str:
        """Detect network from address"""
        if not address:
            return None
        
        if address.startswith('T') and len(address) == 34:
            return 'tron'
        elif address.startswith('0x') and len(address) == 42:
            return 'ethereum'  # Could be ETH, BSC, or Polygon
        elif address.startswith('1') or address.startswith('3') or address.startswith('bc1'):
            return 'bitcoin'
        
        return None