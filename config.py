import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'Zeontrust-wallet-secret-key-2024')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'Zeontrust-jwt-secret-key-2024')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/Zeontrust_wallet.db')
    
    # TRON Config
    TRONGRID_API_KEY = os.getenv('TRONGRID_API_KEY', '')
    TRON_MAINNET_RPC = 'https://api.trongrid.io'
    TRON_TESTNET_RPC = 'https://api.shasta.trongrid.io'
    
    # Ethereum Config
    INFURA_API_KEY = os.getenv('INFURA_API_KEY', '')
    ETH_MAINNET_RPC = f'https://mainnet.infura.io/v3/{INFURA_API_KEY}' if INFURA_API_KEY else 'https://mainnet.infura.io/v3/demo'
    ETH_TESTNET_RPC = f'https://sepolia.infura.io/v3/{INFURA_API_KEY}' if INFURA_API_KEY else 'https://sepolia.infura.io/v3/demo'
    
    # BNB Chain Config
    BSC_MAINNET_RPC = 'https://bsc-dataseed.binance.org'
    BSC_TESTNET_RPC = 'https://data-seed-prebsc-1-s1.binance.org'
    
    # Polygon Config
    POLYGON_MAINNET_RPC = 'https://polygon-rpc.com'
    POLYGON_TESTNET_RPC = 'https://rpc-mumbai.maticvigil.com'
    
    # Bitcoin Config
    BTC_MAINNET_RPC = 'https://blockstream.info/api'
    BTC_TESTNET_RPC = 'https://blockstream.info/testnet/api'
    
    # Network Settings
    NETWORKS = {
        'tron': {'name': 'TRON', 'symbol': 'TRX', 'decimals': 6, 'chain_id': 1},
        'ethereum': {'name': 'Ethereum', 'symbol': 'ETH', 'decimals': 18, 'chain_id': 1},
        'bsc': {'name': 'BNB Chain', 'symbol': 'BNB', 'decimals': 18, 'chain_id': 56},
        'polygon': {'name': 'Polygon', 'symbol': 'MATIC', 'decimals': 18, 'chain_id': 137},
        'bitcoin': {'name': 'Bitcoin', 'symbol': 'BTC', 'decimals': 8, 'chain_id': 0}
    }
    
    # JWT Settings
    JWT_EXPIRATION_HOURS = 24
    
    # Loan Settings
    MIN_LOAN_AMOUNT = 1
    MAX_LOAN_AMOUNT = 1000000
    MAX_LOAN_DURATION_DAYS = 90
    TRANSFER_FEE_PERCENT = 0.01
    DEFAULT_INTEREST_RATE = 5

config = Config()