import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.wallet_service import WalletService
from models.user_models import UserModel
from models.wallet_models import WalletModel, NetworkAccountModel

class TestWalletService(unittest.TestCase):
    """Test wallet service"""
    
    def setUp(self):
        self.test_email = f"wallet_test_{os.urandom(4).hex()}@test.com"
        self.test_password = "Test123456"
        
        # Create test user
        password_hash = AuthService.hash_password(self.test_password)
        self.user_id = UserModel.create('testuser', self.test_email, password_hash)
    
    def test_create_wallet(self):
        """Test wallet creation"""
        wallet = WalletService.create_wallet(self.user_id, 'Test Wallet')
        
        self.assertIsNotNone(wallet)
        self.assertEqual(wallet['wallet_name'], 'Test Wallet')
        self.assertIn('wallet_id', wallet)
        self.assertIn('mnemonic', wallet)
        self.assertIn('addresses', wallet)
    
    def test_create_wallet_with_mnemonic(self):
        """Test wallet creation with custom mnemonic"""
        custom_mnemonic = "abandon ability able about above absent absorb abstract absurd accuse achieve acid"
        wallet = WalletService.create_wallet(self.user_id, 'Test Wallet 2', custom_mnemonic)
        
        self.assertEqual(wallet['mnemonic'], custom_mnemonic)
    
    def test_get_wallet_by_id(self):
        """Test get wallet by ID"""
        created = WalletService.create_wallet(self.user_id, 'Test Wallet')
        wallet = WalletService.get_wallet_by_id(created['wallet_id'], self.user_id)
        
        self.assertIsNotNone(wallet)
        self.assertEqual(wallet['wallet_name'], 'Test Wallet')
        self.assertIn('addresses', wallet)
    
    def test_get_wallet_not_found(self):
        """Test get non-existent wallet"""
        wallet = WalletService.get_wallet_by_id(99999, self.user_id)
        self.assertIsNone(wallet)
    
    def test_get_user_wallets(self):
        """Test get user wallets"""
        WalletService.create_wallet(self.user_id, 'Wallet 1')
        WalletService.create_wallet(self.user_id, 'Wallet 2')
        
        wallets = WalletService.get_user_wallets(self.user_id)
        self.assertEqual(len(wallets), 2)
    
    def test_backup_wallet(self):
        """Test wallet backup"""
        created = WalletService.create_wallet(self.user_id, 'Test Wallet')
        result = WalletService.backup_wallet(created['wallet_id'], self.user_id)
        
        self.assertTrue(result)
        
        wallet = WalletModel.find_by_id(created['wallet_id'])
        self.assertTrue(wallet['is_backed_up'])
    
    def test_backup_wallet_wrong_user(self):
        """Test backup wallet with wrong user"""
        created = WalletService.create_wallet(self.user_id, 'Test Wallet')
        
        # Create another user
        other_email = f"other_{os.urandom(4).hex()}@test.com"
        other_password_hash = AuthService.hash_password('otherpass')
        other_user_id = UserModel.create('otheruser', other_email, other_password_hash)
        
        result = WalletService.backup_wallet(created['wallet_id'], other_user_id)
        self.assertFalse(result)
    
    def test_delete_wallet(self):
        """Test wallet deletion"""
        created = WalletService.create_wallet(self.user_id, 'Test Wallet')
        result = WalletService.delete_wallet(created['wallet_id'], self.user_id)
        
        self.assertTrue(result)
        
        wallet = WalletModel.find_by_id(created['wallet_id'])
        self.assertIsNone(wallet)
    
    def test_generate_addresses(self):
        """Test address generation for all networks"""
        addresses = WalletService.generate_addresses(self.user_id, 1, 'Test')
        
        networks = ['tron', 'ethereum', 'bsc', 'polygon', 'bitcoin']
        for network in networks:
            self.assertIn(network, addresses)
            self.assertIsNotNone(addresses[network])
    
    def test_address_format(self):
        """Test address format for each network"""
        addresses = WalletService.generate_addresses(self.user_id, 1, 'Test')
        
        # TRON address should start with T and be 34 chars
        self.assertTrue(addresses['tron'].startswith('T'))
        self.assertEqual(len(addresses['tron']), 34)
        
        # ETH/BSC/Polygon addresses should start with 0x and be 42 chars
        self.assertTrue(addresses['ethereum'].startswith('0x'))
        self.assertEqual(len(addresses['ethereum']), 42)
        
        self.assertTrue(addresses['bsc'].startswith('0x'))
        self.assertEqual(len(addresses['bsc']), 42)
        
        self.assertTrue(addresses['polygon'].startswith('0x'))
        self.assertEqual(len(addresses['polygon']), 42)
        
        # Bitcoin address should start with 1
        self.assertTrue(addresses['bitcoin'].startswith('1'))
    
    def test_network_accounts_created(self):
        """Test network accounts are created in database"""
        created = WalletService.create_wallet(self.user_id, 'Test Wallet')
        
        accounts = NetworkAccountModel.find_by_wallet(created['wallet_id'])
        self.assertEqual(len(accounts), 5)  # 5 networks
        
        networks = [a['network'] for a in accounts]
        self.assertIn('tron', networks)
        self.assertIn('ethereum', networks)
        self.assertIn('bsc', networks)
        self.assertIn('polygon', networks)
        self.assertIn('bitcoin', networks)

if __name__ == '__main__':
    unittest.main()