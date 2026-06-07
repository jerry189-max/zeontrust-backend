from models.token_models import CustomTokenModel, VerifiedTokenModel, TokenVerificationRequestModel
from models.user_models import UserModel
from models.wallet_models import NetworkAccountModel
from services.balance_service import BalanceService
import requests
import json
import hashlib
from datetime import datetime

class TokenService:
    
    # ==================== TOKEN LISTING ====================
    
    @staticmethod
    def get_all_tokens(network: str = None, user_id: int = None):
        """Get all tokens (native + verified + custom)"""
        tokens = []
        
        # Native tokens
        native_tokens = {
            'tron': {'symbol': 'TRX', 'name': 'TRON', 'is_native': True, 'decimals': 6, 'icon': '🌐'},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'is_native': True, 'decimals': 18, 'icon': '💎'},
            'bsc': {'symbol': 'BNB', 'name': 'BNB Chain', 'is_native': True, 'decimals': 18, 'icon': '🔶'},
            'polygon': {'symbol': 'MATIC', 'name': 'Polygon', 'is_native': True, 'decimals': 18, 'icon': '🟣'},
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'is_native': True, 'decimals': 8, 'icon': '🟠'}
        }
        
        if network and network in native_tokens:
            tokens.append(native_tokens[network])
        
        # Verified tokens
        verified_tokens = VerifiedTokenModel.get_all_verified_tokens(network)
        for token in verified_tokens:
            token['is_native'] = False
            token['is_verified'] = True
            tokens.append(token)
        
        # Custom tokens (if user_id provided)
        if user_id:
            custom_tokens = CustomTokenModel.find_by_user(user_id, network)
            for token in custom_tokens:
                token['is_native'] = False
                token['is_verified'] = False
                tokens.append(token)
        
        return tokens
    
    @staticmethod
    def get_verified_tokens(network: str = None):
        """Get only verified tokens"""
        return VerifiedTokenModel.get_all_verified_tokens(network)
    
    @staticmethod
    def get_custom_tokens(user_id: int, network: str = None):
        """Get user's custom tokens"""
        return CustomTokenModel.find_by_user(user_id, network)
    
    # ==================== CUSTOM TOKEN MANAGEMENT ====================
    
    @staticmethod
    def add_custom_token(user_id: int, network: str, contract_address: str, 
                         token_name: str, token_symbol: str, decimals: int, 
                         logo_url: str = None) -> int:
        """Add custom token for user"""
        # Check if token already added
        existing = CustomTokenModel.find_by_contract(user_id, contract_address, network)
        if existing:
            raise ValueError('Token already added')
        
        # Check if token is verified
        verified = VerifiedTokenModel.find_verified_token(contract_address, network)
        if verified:
            raise ValueError('Token is already verified in the system')
        
        token_id = CustomTokenModel.create(
            user_id, network, contract_address, token_name, token_symbol, decimals, logo_url
        )
        
        return token_id
    
    @staticmethod
    def remove_custom_token(token_id: int, user_id: int) -> bool:
        """Remove custom token for user"""
        return CustomTokenModel.delete_custom_token(token_id, user_id)
    
    @staticmethod
    def update_custom_token(token_id: int, user_id: int, data: dict) -> bool:
        """Update custom token details"""
        # First verify token belongs to user
        # Implementation depends on your models
        return True
    
    # ==================== TOKEN METADATA FETCHING ====================
    
    @staticmethod
    def fetch_token_metadata(contract_address: str, network: str) -> dict:
        """Fetch token metadata from blockchain"""
        metadata = {
            'name': None,
            'symbol': None,
            'decimals': 18,
            'contract_address': contract_address,
            'network': network
        }
        
        try:
            if network == 'tron':
                metadata = TokenService._fetch_tron_token_metadata(contract_address)
            elif network in ['ethereum', 'bsc', 'polygon']:
                metadata = TokenService._fetch_evm_token_metadata(contract_address, network)
            else:
                raise ValueError(f'Unsupported network: {network}')
        except Exception as e:
            # Return default metadata if fetching fails
            metadata['name'] = f'Unknown Token on {network.upper()}'
            metadata['symbol'] = 'UNKNOWN'
            metadata['decimals'] = 18
        
        return metadata
    
    @staticmethod
    def _fetch_tron_token_metadata(contract_address: str) -> dict:
        """Fetch TRC-20 token metadata from TRON blockchain"""
        try:
            # TRONGrid API endpoint
            url = f"https://api.trongrid.io/v1/contracts/{contract_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    contract_data = data['data'][0]
                    return {
                        'name': contract_data.get('name', 'Unknown Token'),
                        'symbol': contract_data.get('symbol', 'UNKNOWN'),
                        'decimals': contract_data.get('decimals', 18),
                        'contract_address': contract_address,
                        'network': 'tron'
                    }
        except Exception as e:
            print(f"Error fetching TRON token metadata: {e}")
        
        return {
            'name': 'Custom TRC20 Token',
            'symbol': 'CTOKEN',
            'decimals': 18,
            'contract_address': contract_address,
            'network': 'tron'
        }
    
    @staticmethod
    def _fetch_evm_token_metadata(contract_address: str, network: str) -> dict:
        """Fetch ERC-20/BEP-20 token metadata from EVM blockchain"""
        explorers = {
            'ethereum': 'https://api.etherscan.io/api',
            'bsc': 'https://api.bscscan.com/api',
            'polygon': 'https://api.polygonscan.com/api'
        }
        
        base_url = explorers.get(network)
        if not base_url:
            raise ValueError(f'Unsupported EVM network: {network}')
        
        try:
            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': contract_address,
                'apikey': ''  # Add API key if available
            }
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    token_info = data['result'][0]
                    return {
                        'name': token_info.get('name', 'Unknown Token'),
                        'symbol': token_info.get('symbol', 'UNKNOWN'),
                        'decimals': int(token_info.get('decimals', 18)),
                        'contract_address': contract_address,
                        'network': network
                    }
        except Exception as e:
            print(f"Error fetching EVM token metadata: {e}")
        
        return {
            'name': f'Custom {network.upper()} Token',
            'symbol': 'CTOKEN',
            'decimals': 18,
            'contract_address': contract_address,
            'network': network
        }
    
    # ==================== TOKEN APPROVAL REQUEST ====================
    
    @staticmethod
    def request_token_approval(user_id: int, network: str, contract_address: str, 
                               token_name: str, token_symbol: str, decimals: int,
                               website: str = None, email: str = None, twitter: str = None,
                               telegram: str = None, discord: str = None, logo_url: str = None,
                               description: str = None) -> int:
        """Submit token for admin approval"""
        # Check if token already verified
        existing_verified = VerifiedTokenModel.find_verified_token(contract_address, network)
        if existing_verified:
            raise ValueError('Token is already verified')
        
        # Check if request already pending
        pending_requests = TokenVerificationRequestModel.find_pending_requests()
        for req in pending_requests:
            if req['contract_address'] == contract_address and req['network'] == network:
                raise ValueError('Approval request already pending')
        
        request_id = TokenVerificationRequestModel.create(
            user_id, network, contract_address, token_name, token_symbol, decimals,
            website, email, twitter, telegram, discord, logo_url, description
        )
        
        return request_id
    
    @staticmethod
    def get_pending_requests():
        """Get all pending token approval requests (admin)"""
        return TokenVerificationRequestModel.find_pending_requests()
    
    @staticmethod
    def get_user_requests(user_id: int):
        """Get user's token approval requests"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM token_verification_requests 
            WHERE user_id = ? 
            ORDER BY submitted_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            requests.append({
                'id': row[0],
                'network': row[2],
                'contract_address': row[3],
                'token_name': row[4],
                'token_symbol': row[5],
                'status': row[13],
                'admin_notes': row[14],
                'submitted_at': row[15]
            })
        return requests
    
    # ==================== TOKEN APPROVAL (ADMIN) ====================
    
    @staticmethod
    def approve_token(request_id: int, admin_id: int, category: str = 'DeFi', 
                      risk_level: str = 'low', notes: str = None) -> bool:
        """Admin approves token request"""
        token_request = TokenVerificationRequestModel.find_by_id(request_id)
        if not token_request:
            raise ValueError('Request not found')
        
        # Add to verified tokens
        VerifiedTokenModel.create_verified_token(
            network=token_request['network'],
            contract_address=token_request['contract_address'],
            token_name=token_request['token_name'],
            token_symbol=token_request['token_symbol'],
            decimals=token_request['decimals'],
            logo_url=token_request.get('logo_url'),
            website=token_request.get('website'),
            category=category,
            risk_level=risk_level
        )
        
        # Update request status
        TokenVerificationRequestModel.update_status(request_id, 'approved', admin_id, notes)
        
        return True
    
    @staticmethod
    def reject_token(request_id: int, admin_id: int, reason: str = None) -> bool:
        """Admin rejects token request"""
        TokenVerificationRequestModel.update_status(request_id, 'rejected', admin_id, reason)
        return True
    
    # ==================== VERIFIED TOKEN MANAGEMENT (ADMIN) ====================
    
    @staticmethod
    def add_verified_token(network: str, contract_address: str, token_name: str,
                          token_symbol: str, decimals: int, logo_url: str = None,
                          website: str = None, category: str = 'DeFi') -> int:
        """Admin manually adds verified token"""
        existing = VerifiedTokenModel.find_verified_token(contract_address, network)
        if existing:
            raise ValueError('Token already verified')
        
        return VerifiedTokenModel.create_verified_token(
            network, contract_address, token_name, token_symbol, decimals,
            logo_url, website, category
        )
    
    @staticmethod
    def remove_verified_token(token_id: int) -> bool:
        """Admin removes verified token"""
        return VerifiedTokenModel.delete_verified_token(token_id)
    
    @staticmethod
    def update_verified_token_status(token_id: int, is_active: bool) -> bool:
        """Admin updates token status"""
        return VerifiedTokenModel.update_verified_token_status(token_id, is_active)
    
    @staticmethod
    def get_token_by_address(contract_address: str, network: str) -> dict:
        """Get token by contract address"""
        token = VerifiedTokenModel.find_verified_token(contract_address, network)
        if not token:
            # Check in custom tokens? (would need user_id)
            pass
        return token
    
    # ==================== TOKEN BALANCE ====================
    
    @staticmethod
    def get_token_balance(wallet_id: int, network: str, token_address: str = None) -> float:
        """Get token balance for wallet"""
        from models.wallet_models import NetworkAccountModel
        
        account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
        if not account:
            return 0.0
        
        balance_service = BalanceService(network, False)
        
        if token_address:
            return balance_service.get_token_balance(account['address'], token_address)
        else:
            return balance_service.get_native_balance(account['address'])
    
    @staticmethod
    def get_all_token_balances(wallet_id: int, network: str) -> list:
        """Get balances for all tokens on network"""
        from models.wallet_models import NetworkAccountModel
        
        account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
        if not account:
            return []
        
        tokens = TokenService.get_all_tokens(network)
        balance_service = BalanceService(network, False)
        
        results = []
        for token in tokens:
            if token.get('is_native'):
                balance = balance_service.get_native_balance(account['address'])
            else:
                balance = balance_service.get_token_balance(
                    account['address'], 
                    token.get('contract_address')
                )
            
            results.append({
                'token': token,
                'balance': balance,
                'usd_value': balance * TokenService._get_token_price(token.get('symbol', 'TOKEN'))
            })
        
        return results
    
    @staticmethod
    def _get_token_price(symbol: str) -> float:
        """Get token price in USD (mock)"""
        prices = {
            'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80,
            'BTC': 65000, 'USDT': 1.00, 'USDC': 1.00, 'DAI': 1.00
        }
        return prices.get(symbol.upper(), 0)
    
    # ==================== TOKEN SEARCH ====================
    
    @staticmethod
    def search_tokens(query: str, network: str = None) -> list:
        """Search for tokens by name or symbol"""
        from models.token_models import VerifiedTokenModel
        
        conn = get_db()
        cursor = conn.cursor()
        
        if network:
            cursor.execute('''
                SELECT * FROM verified_tokens 
                WHERE network = ? AND (token_name LIKE ? OR token_symbol LIKE ?)
                LIMIT 20
            ''', (network, f'%{query}%', f'%{query}%'))
        else:
            cursor.execute('''
                SELECT * FROM verified_tokens 
                WHERE token_name LIKE ? OR token_symbol LIKE ?
                LIMIT 20
            ''', (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        tokens = []
        for row in rows:
            tokens.append({
                'id': row[0],
                'network': row[1],
                'contract_address': row[2],
                'token_name': row[3],
                'token_symbol': row[4],
                'decimals': row[5],
                'logo_url': row[6],
                'category': row[8]
            })
        
        return tokens
    
    # ==================== TOKEN CATEGORIES ====================
    
    @staticmethod
    def get_token_categories() -> list:
        """Get all token categories"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM token_categories ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        categories = []
        for row in rows:
            categories.append({
                'id': row[0],
                'name': row[1],
                'icon': row[2],
                'created_at': row[3]
            })
        return categories
    
    @staticmethod
    def add_category(name: str, icon: str = None) -> int:
        """Add new token category (admin)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO token_categories (name, icon) VALUES (?, ?)', (name, icon))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    
    # ==================== TOKEN STATISTICS ====================
    
    @staticmethod
    def get_token_statistics() -> dict:
        """Get token statistics for admin dashboard"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM verified_tokens')
        total_verified = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM token_verification_requests WHERE status = "pending"')
        pending_approvals = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM custom_tokens')
        total_custom = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT network, COUNT(*) FROM verified_tokens GROUP BY network')
        by_network = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_verified': total_verified,
            'pending_approvals': pending_approvals,
            'total_custom': total_custom,
            'by_network': [{'network': row[0], 'count': row[1]} for row in by_network]
        }


# Helper function
def get_db():
    import sqlite3
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn