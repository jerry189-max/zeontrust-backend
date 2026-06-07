import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.token_service import TokenService
from models.token_models import VerifiedTokenModel, TokenVerificationRequestModel
from models.user_models import UserModel
from services.auth_service import AuthService

class TestContracts(unittest.TestCase):
    """Test smart contract interactions and token management"""
    
    def setUp(self):
        self.test_email = f"contract_test_{os.urandom(4).hex()}@test.com"
        self.test_password = "Test123456"
        
        # Create test user
        password_hash = AuthService.hash_password(self.test_password)
        self.user_id = UserModel.create('testuser', self.test_email, password_hash)
        
        # Create admin user
        admin_email = f"admin_{os.urandom(4).hex()}@test.com"
        admin_password_hash = AuthService.hash_password('admin123')
        self.admin_id = UserModel.create('admin', admin_email, admin_password_hash, is_admin=True)
    
    def test_fetch_token_metadata(self):
        """Test fetching token metadata from blockchain"""
        metadata = TokenService.fetch_token_metadata(
            contract_address='0x1234567890123456789012345678901234567890',
            network='ethereum'
        )
        
        self.assertIsNotNone(metadata)
        self.assertIn('name', metadata)
        self.assertIn('symbol', metadata)
        self.assertIn('decimals', metadata)
    
    def test_add_custom_token(self):
        """Test adding custom token"""
        token_id = TokenService.add_custom_token(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18
        )
        
        self.assertIsNotNone(token_id)
    
    def test_add_duplicate_custom_token(self):
        """Test adding duplicate custom token"""
        contract = 'TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        
        # Add first token
        TokenService.add_custom_token(
            user_id=self.user_id,
            network='tron',
            contract_address=contract,
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18
        )
        
        # Add duplicate
        with self.assertRaises(ValueError):
            TokenService.add_custom_token(
                user_id=self.user_id,
                network='tron',
                contract_address=contract,
                token_name='Test Token 2',
                token_symbol='TEST2',
                decimals=18
            )
    
    def test_request_token_approval(self):
        """Test requesting token approval"""
        request_id = TokenService.request_token_approval(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18,
            website='https://testtoken.com',
            email='contact@testtoken.com',
            twitter='@testtoken',
            description='This is a test token'
        )
        
        self.assertIsNotNone(request_id)
    
    def test_get_pending_requests(self):
        """Test getting pending token approval requests"""
        TokenService.request_token_approval(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18
        )
        
        requests = TokenService.get_pending_requests()
        self.assertGreaterEqual(len(requests), 1)
    
    def test_approve_token(self):
        """Test admin approving token"""
        request_id = TokenService.request_token_approval(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18
        )
        
        result = TokenService.approve_token(request_id, self.admin_id, 'DeFi')
        self.assertTrue(result)
        
        # Check token is now verified
        tokens = VerifiedTokenModel.get_all_verified_tokens('tron')
        token_found = any(t['token_symbol'] == 'TEST' for t in tokens)
        self.assertTrue(token_found)
    
    def test_reject_token(self):
        """Test admin rejecting token"""
        request_id = TokenService.request_token_approval(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Test Token',
            token_symbol='TEST',
            decimals=18
        )
        
        result = TokenService.reject_token(request_id, self.admin_id, 'Invalid contract')
        self.assertTrue(result)
    
    def test_get_verified_tokens(self):
        """Test getting verified tokens"""
        # Create a verified token
        VerifiedTokenModel.create_verified_token(
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Verified Token',
            token_symbol='VER',
            decimals=18
        )
        
        tokens = TokenService.get_verified_tokens('tron')
        self.assertGreaterEqual(len(tokens), 1)
    
    def test_get_custom_tokens(self):
        """Test getting custom tokens for user"""
        TokenService.add_custom_token(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Custom Token',
            token_symbol='CUST',
            decimals=18
        )
        
        tokens = TokenService.get_custom_tokens(self.user_id, 'tron')
        self.assertGreaterEqual(len(tokens), 1)
    
    def test_remove_custom_token(self):
        """Test removing custom token"""
        token_id = TokenService.add_custom_token(
            user_id=self.user_id,
            network='tron',
            contract_address='TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            token_name='Custom Token',
            token_symbol='CUST',
            decimals=18
        )
        
        result = TokenService.remove_custom_token(token_id, self.user_id)
        self.assertTrue(result)
    
    def test_token_metadata_cache(self):
        """Test token metadata is cached"""
        contract = '0x1234567890123456789012345678901234567890'
        
        # First fetch
        metadata1 = TokenService.fetch_token_metadata(contract, 'ethereum')
        
        # Second fetch (should be cached)
        metadata2 = TokenService.fetch_token_metadata(contract, 'ethereum')
        
        self.assertEqual(metadata1['name'], metadata2['name'])
    
    def test_invalid_contract_address(self):
        """Test invalid contract address handling"""
        with self.assertRaises(Exception):
            TokenService.fetch_token_metadata('invalid', 'ethereum')

if __name__ == '__main__':
    unittest.main()