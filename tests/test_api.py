import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.user_models import UserModel
from models.wallet_models import WalletModel

class TestAPI(unittest.TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Setup before each test"""
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = f"test_{os.urandom(4).hex()}@test.com"
        self.test_password = "test123456"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_register_user(self):
        """Test user registration"""
        response = self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        self.app.post('/api/auth/register', json={
            'username': 'testuser1',
            'email': self.test_email,
            'password': self.test_password
        })
        
        # Second registration with same email
        response = self.app.post('/api/auth/register', json={
            'username': 'testuser2',
            'email': self.test_email,
            'password': self.test_password
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('already registered', data['error'])
    
    def test_login_success(self):
        """Test successful login"""
        # Register first
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        # Login
        response = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('token', data)
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register first
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        # Login with wrong password
        response = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_login_user_not_found(self):
        """Test login with non-existent user"""
        response = self.app.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_create_wallet(self):
        """Test create wallet endpoint"""
        # Register and login
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        login_res = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        token = json.loads(login_res.data)['token']
        
        # Create wallet
        response = self.app.post('/api/wallets/create', 
            headers={'Authorization': f'Bearer {token}'},
            json={'wallet_name': 'Test Wallet'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('wallet_id', data)
        self.assertIn('addresses', data)
    
    def test_get_wallets(self):
        """Test get wallets endpoint"""
        # Register and login
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        login_res = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        token = json.loads(login_res.data)['token']
        
        # Create wallet
        self.app.post('/api/wallets/create', 
            headers={'Authorization': f'Bearer {token}'},
            json={'wallet_name': 'Test Wallet'})
        
        # Get wallets
        response = self.app.get('/api/wallets', 
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('wallets', data)
    
    def test_get_balance(self):
        """Test get balance endpoint"""
        # Register and login
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        login_res = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        token = json.loads(login_res.data)['token']
        
        # Create wallet
        create_res = self.app.post('/api/wallets/create', 
            headers={'Authorization': f'Bearer {token}'},
            json={'wallet_name': 'Test Wallet'})
        wallet_id = json.loads(create_res.data)['wallet_id']
        
        # Get balance
        response = self.app.get(f'/api/balance/{wallet_id}?network=tron',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('balance', data)
    
    def test_send_transaction(self):
        """Test send transaction endpoint"""
        # Register and login
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        login_res = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        token = json.loads(login_res.data)['token']
        
        # Create wallet
        create_res = self.app.post('/api/wallets/create', 
            headers={'Authorization': f'Bearer {token}'},
            json={'wallet_name': 'Test Wallet'})
        wallet_id = json.loads(create_res.data)['wallet_id']
        
        # Send transaction
        response = self.app.post('/api/transaction/send',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'wallet_id': wallet_id,
                'network': 'tron',
                'to_address': 'TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'amount': 10
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('tx_hash', data)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        response = self.app.get('/api/wallets')
        self.assertEqual(response.status_code, 401)
    
    def test_token_list(self):
        """Test get token list endpoint"""
        # Register and login
        self.app.post('/api/auth/register', json={
            'username': 'testuser',
            'email': self.test_email,
            'password': self.test_password
        })
        
        login_res = self.app.post('/api/auth/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        token = json.loads(login_res.data)['token']
        
        response = self.app.get('/api/tokens/list?network=tron',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('tokens', data)

if __name__ == '__main__':
    unittest.main()