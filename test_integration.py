#!/usr/bin/env python3
"""
Test script for WooCommerce API Integration
==========================================

This script tests the various components of the WooCommerce integration
to ensure everything works correctly.

Usage:
    python test_integration.py
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from woocommerce_client import WooCommerceClient
from config import DATABASE_NAME


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a test database
        self.test_db_name = "test_" + DATABASE_NAME
        
        # Remove existing test database if it exists
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
        
        # Create database manager with test database
        self.db = DatabaseManager(self.test_db_name)
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove test database
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
    
    def test_init_database(self):
        """Test database initialization."""
        # Database should be initialized automatically
        self.assertTrue(os.path.exists(self.test_db_name))
        
        # Check if tables exist
        stores = self.db.list_stores()
        self.assertIsInstance(stores, list)
        self.assertEqual(len(stores), 0)
    
    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption."""
        test_data = "sensitive_information"
        encrypted = self.db.encrypt_data(test_data)
        decrypted = self.db.decrypt_data(encrypted)
        
        self.assertNotEqual(test_data, encrypted)
        self.assertEqual(test_data, decrypted)
    
    def test_store_and_retrieve_credentials(self):
        """Test storing and retrieving credentials."""
        # Test data
        store_url = "https://test-store.com"
        store_name = "Test Store"
        username = "admin"
        consumer_key = "ck_test_key"
        consumer_secret = "cs_test_secret"
        
        # Store credentials
        store_id = self.db.store_credentials(
            store_url=store_url,
            store_name=store_name,
            admin_username=username,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )
        
        self.assertIsInstance(store_id, int)
        self.assertGreater(store_id, 0)
        
        # Retrieve credentials
        credentials = self.db.get_credentials(store_url)
        
        self.assertIsNotNone(credentials)
        self.assertEqual(credentials['store_url'], store_url)
        self.assertEqual(credentials['store_name'], store_name)
        self.assertEqual(credentials['admin_username'], username)
        self.assertEqual(credentials['consumer_key'], consumer_key)
        self.assertEqual(credentials['consumer_secret'], consumer_secret)
    
    def test_list_stores(self):
        """Test listing stores."""
        # Initially empty
        stores = self.db.list_stores()
        self.assertEqual(len(stores), 0)
        
        # Add a store
        self.db.store_credentials(
            store_url="https://test-store.com",
            store_name="Test Store",
            admin_username="admin",
            consumer_key="ck_test",
            consumer_secret="cs_test"
        )
        
        # Should have one store
        stores = self.db.list_stores()
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0]['store_url'], "https://test-store.com")
    
    def test_disconnect_store(self):
        """Test disconnecting a store."""
        store_url = "https://test-store.com"
        
        # Add a store
        self.db.store_credentials(
            store_url=store_url,
            store_name="Test Store",
            admin_username="admin",
            consumer_key="ck_test",
            consumer_secret="cs_test"
        )
        
        # Disconnect the store
        result = self.db.disconnect_store(store_url)
        self.assertTrue(result)
        
        # Should not be in active stores list
        stores = self.db.list_stores()
        self.assertEqual(len(stores), 0)
        
        # Should not be retrievable
        credentials = self.db.get_credentials(store_url)
        self.assertIsNone(credentials)
    
    def test_logging(self):
        """Test action logging."""
        # Get initial log count
        initial_logs = self.db.get_logs(limit=100)
        initial_count = len(initial_logs)
        
        # Log an action
        self.db.log_action(None, "test_action", "success", "Test message")
        
        # Retrieve logs
        logs = self.db.get_logs(limit=100)
        self.assertEqual(len(logs), initial_count + 1)
        
        # Check the most recent log entry
        recent_log = logs[0]  # Logs are ordered by timestamp DESC
        self.assertEqual(recent_log['action'], "test_action")
        self.assertEqual(recent_log['status'], "success")
        self.assertEqual(recent_log['message'], "Test message")


class TestWooCommerceClient(unittest.TestCase):
    """Test cases for WooCommerceClient class."""
    
    def setUp(self):
        """Set up test environment."""
        self.store_url = "https://test-store.com"
        self.username = "admin"
        self.password = "password"
        self.client = WooCommerceClient(self.store_url, self.username, self.password)
    
    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.store_url, self.store_url)
        self.assertEqual(self.client.username, self.username)
        self.assertEqual(self.client.password, self.password)
        self.assertIsNotNone(self.client.session)
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = self.client._make_request('GET', '/test-endpoint')
        
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_make_request_failure(self, mock_request):
        """Test failed API request."""
        # Mock failed response
        mock_request.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception) as context:
            self.client._make_request('GET', '/test-endpoint')
        
        # The exception message should contain either "Request failed" or "Network error"
        exception_message = str(context.exception)
        self.assertTrue(
            "Request failed" in exception_message or "Network error" in exception_message,
            f"Expected 'Request failed' or 'Network error' in '{exception_message}'"
        )
    
    @patch('woocommerce_client.WooCommerceClient._make_request')
    def test_test_wordpress_connection_success(self, mock_make_request):
        """Test successful WordPress authentication."""
        # Mock successful response
        mock_make_request.return_value = {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com"
        }
        
        result = self.client.test_wordpress_connection()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user_data']['name'], "Admin User")
    
    @patch('woocommerce_client.WooCommerceClient._make_request')
    def test_test_wordpress_connection_failure(self, mock_make_request):
        """Test failed WordPress authentication."""
        # Mock failed response
        mock_make_request.side_effect = Exception("Authentication failed")
        
        result = self.client.test_wordpress_connection()
        
        self.assertFalse(result['success'])
        self.assertIn("Failed to authenticate", result['message'])
    
    @patch('woocommerce_client.WooCommerceClient._make_request')
    def test_get_store_info_success(self, mock_make_request):
        """Test successful store info retrieval."""
        # Mock successful response
        mock_make_request.return_value = {
            "name": "Test Store",
            "description": "A test store",
            "url": "https://test-store.com"
        }
        
        result = self.client.get_store_info()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['store_name'], "Test Store")
    
    def test_generate_api_keys_simulation(self):
        """Test API key generation (simulated)."""
        result = self.client.generate_api_keys_via_rest()
        
        self.assertTrue(result['success'])
        self.assertIn('consumer_key', result)
        self.assertIn('consumer_secret', result)
        self.assertIn('key_id', result)
        self.assertIn('note', result)  # Should mention it's simulated
    
    @patch('requests.Session.get')
    def test_test_api_keys_success(self, mock_get):
        """Test successful API key validation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.content = b'[]'
        mock_get.return_value = mock_response
        
        result = self.client.test_api_keys("ck_test", "cs_test")
        
        self.assertTrue(result['success'])
        self.assertIn("working correctly", result['message'])
    
    @patch('requests.Session.get')
    def test_test_api_keys_failure(self, mock_get):
        """Test failed API key validation."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        result = self.client.test_api_keys("ck_test", "cs_test")
        
        self.assertFalse(result['success'])
        self.assertIn("test failed", result['message'])


class TestIntegrationFlow(unittest.TestCase):
    """Test cases for the complete integration flow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_db_name = "test_integration_" + DATABASE_NAME
        
        # Remove existing test database if it exists
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
        
        # Create database manager with test database
        self.db = DatabaseManager(self.test_db_name)
        
        self.store_url = "https://test-store.com"
        self.username = "admin"
        self.password = "password"
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
    
    @patch('woocommerce_client.WooCommerceClient.test_wordpress_connection')
    @patch('woocommerce_client.WooCommerceClient.get_store_info')
    @patch('woocommerce_client.WooCommerceClient.generate_api_keys_via_rest')
    def test_complete_integration_flow(self, mock_generate_keys, mock_store_info, mock_auth):
        """Test the complete integration flow."""
        # Mock successful authentication
        mock_auth.return_value = {
            'success': True,
            'user_data': {'name': 'Admin User'},
            'message': 'Successfully authenticated'
        }
        
        # Mock successful store info
        mock_store_info.return_value = {
            'success': True,
            'store_name': 'Test Store',
            'store_url': self.store_url
        }
        
        # Mock successful API key generation
        mock_generate_keys.return_value = {
            'success': True,
            'consumer_key': 'ck_test_key',
            'consumer_secret': 'cs_test_secret',
            'key_id': 'key_123',
            'permissions': 'read_write',
            'description': 'Test API Key'
        }
        
        # Create client
        client = WooCommerceClient(self.store_url, self.username, self.password)
        
        # Step 1: Test authentication
        auth_result = client.test_wordpress_connection()
        self.assertTrue(auth_result['success'])
        
        # Step 2: Get store info
        store_info = client.get_store_info()
        self.assertTrue(store_info['success'])
        
        # Step 3: Generate API keys
        api_keys = client.generate_api_keys_via_rest()
        self.assertTrue(api_keys['success'])
        
        # Step 4: Store credentials
        store_id = self.db.store_credentials(
            store_url=self.store_url,
            store_name=store_info['store_name'],
            admin_username=self.username,
            consumer_key=api_keys['consumer_key'],
            consumer_secret=api_keys['consumer_secret'],
            key_id=api_keys['key_id'],
            permissions=api_keys['permissions'],
            description=api_keys['description']
        )
        
        self.assertIsInstance(store_id, int)
        self.assertGreater(store_id, 0)
        
        # Step 5: Verify stored credentials
        stored_credentials = self.db.get_credentials(self.store_url)
        self.assertIsNotNone(stored_credentials)
        self.assertEqual(stored_credentials['consumer_key'], api_keys['consumer_key'])
        self.assertEqual(stored_credentials['consumer_secret'], api_keys['consumer_secret'])
        
        # Step 6: Verify store is listed
        stores = self.db.list_stores()
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0]['store_url'], self.store_url)


def run_tests():
    """Run all tests."""
    print("🧪 Running WooCommerce Integration Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDatabaseManager))
    test_suite.addTest(unittest.makeSuite(TestWooCommerceClient))
    test_suite.addTest(unittest.makeSuite(TestIntegrationFlow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nResult: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 