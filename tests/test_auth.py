import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from models.user_models import UserModel
from models.security_models import SecuritySettingsModel

class TestAuthService(unittest.TestCase):
    """Test authentication service"""
    
    def setUp(self):
        self.test_email = f"auth_test_{os.urandom(4).hex()}@test.com"
        self.test_password = "Test123456"
    
    def test_hash_password(self):
        """Test password hashing"""
        hashed = AuthService.hash_password(self.test_password)
        self.assertIsNotNone(hashed)
        self.assertNotEqual(hashed, self.test_password)
    
    def test_verify_password(self):
        """Test password verification"""
        hashed = AuthService.hash_password(self.test_password)
        self.assertTrue(AuthService.verify_password(self.test_password, hashed))
        self.assertFalse(AuthService.verify_password('wrongpassword', hashed))
    
    def test_create_session(self):
        """Test session creation"""
        # Create a test user first
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser', self.test_email, password_hash)
        
        token = AuthService.generate_token(user_id)
        session = AuthService.create_session(user_id, token)
        
        self.assertIsNotNone(session)
        self.assertIn('session_id', session)
        self.assertIn('token', session)
    
    def test_validate_session(self):
        """Test session validation"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser2', self.test_email, password_hash)
        
        token = AuthService.generate_token(user_id)
        AuthService.create_session(user_id, token)
        
        session = AuthService.validate_session(token)
        self.assertIsNotNone(session)
        self.assertEqual(session['user_id'], user_id)
    
    def test_invalid_session(self):
        """Test invalid session validation"""
        session = AuthService.validate_session('invalid_token')
        self.assertIsNone(session)
    
    def test_set_pin(self):
        """Test PIN code setting"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser3', self.test_email, password_hash)
        
        result = AuthService.set_pin_code(user_id, '123456')
        self.assertTrue(result)
        
        settings = SecuritySettingsModel.find_by_user(user_id)
        self.assertTrue(settings['pin_enabled'])
    
    def test_verify_pin(self):
        """Test PIN code verification"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser4', self.test_email, password_hash)
        
        AuthService.set_pin_code(user_id, '123456')
        
        self.assertTrue(AuthService.verify_pin(user_id, '123456'))
        self.assertFalse(AuthService.verify_pin(user_id, '000000'))
    
    def test_change_password(self):
        """Test password change"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser5', self.test_email, password_hash)
        
        new_password = 'NewPassword789'
        result = AuthService.change_password(user_id, self.test_password, new_password)
        self.assertTrue(result)
        
        user = UserModel.find_by_id(user_id)
        self.assertTrue(AuthService.verify_password(new_password, user['password_hash']))
    
    def test_change_password_wrong_old(self):
        """Test password change with wrong old password"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser6', self.test_email, password_hash)
        
        with self.assertRaises(ValueError):
            AuthService.change_password(user_id, 'wrongpassword', 'NewPassword789')
    
    def test_enable_2fa(self):
        """Test 2FA enable"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser7', self.test_email, password_hash)
        
        result = AuthService.enable_2fa(user_id)
        self.assertIsNotNone(result)
        self.assertIn('secret', result)
        self.assertIn('qr_url', result)
    
    def test_verify_2fa(self):
        """Test 2FA verification"""
        password_hash = AuthService.hash_password(self.test_password)
        user_id = UserModel.create('testuser8', self.test_email, password_hash)
        
        AuthService.enable_2fa(user_id)
        # Test with mock code
        self.assertTrue(AuthService.verify_2fa(user_id, '123456'))

if __name__ == '__main__':
    unittest.main()