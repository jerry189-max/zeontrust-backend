import secrets
import hashlib

class MnemonicService:
    
    WORDLIST = [
        'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract', 'absurd', 'accuse',
        'achieve', 'acid', 'acoustic', 'acquire', 'across', 'actress', 'actual', 'adapt', 'addict', 'address',
        'adjust', 'admit', 'adult', 'advance', 'advice', 'aerobic', 'affair', 'afford', 'afraid', 'africa',
        'agree', 'ahead', 'airport', 'album', 'alcohol', 'alien', 'alike', 'alive', 'allow', 'almost',
        'alone', 'along', 'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among', 'amount'
    ]
    
    @staticmethod
    def generate_mnemonic(strength: int = 128) -> str:
        words = []
        for _ in range(12):
            words.append(secrets.choice(MnemonicService.WORDLIST))
        return ' '.join(words)
    
    @staticmethod
    def validate_mnemonic(mnemonic: str) -> bool:
        words = mnemonic.strip().lower().split()
        if len(words) != 12:
            return False
        for word in words:
            if word not in MnemonicService.WORDLIST:
                return False
        return True
    
    @staticmethod
    def mnemonic_to_seed(mnemonic: str, passphrase: str = '') -> bytes:
        normalized_mnemonic = mnemonic.strip().lower()
        seed = hashlib.pbkdf2_hmac('sha512', normalized_mnemonic.encode(), f'mnemonic{passphrase}'.encode(), 2048)
        return seed