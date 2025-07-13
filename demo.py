#!/usr/bin/env python3
"""
WooCommerce Integration Demo
============================

This demo script shows how the WooCommerce API integration would work
in practice, including both successful and failed scenarios.

Usage:
    python demo.py
"""

import sys
import time
from database import DatabaseManager
from woocommerce_client import WooCommerceClient

def print_step(step_num, title):
    """Print a formatted step header."""
    print(f"\n{step_num}️⃣ {title}")
    print("-" * (len(title) + 5))

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")

def simulate_delay(seconds=1):
    """Simulate processing time."""
    time.sleep(seconds)

def demo_successful_integration():
    """Demo a successful integration flow."""
    print("🎯 Demo: Successful WooCommerce Integration")
    print("=" * 50)
    
    # Mock data
    store_url = "https://demo-store.com"
    username = "admin"
    password = "secure_password"
    
    print(f"📝 Store URL: {store_url}")
    print(f"📝 Username: {username}")
    print(f"📝 Password: {'*' * len(password)}")
    
    # Initialize database
    db = DatabaseManager()
    
    # Initialize client
    client = WooCommerceClient(store_url, username, password)
    
    # Step 1: Test WordPress Authentication
    print_step(1, "Testing WordPress Authentication")
    simulate_delay()
    
    # In a real scenario, this would make an actual HTTP request
    print_info("Making request to /wp-json/wp/v2/users/me")
    simulate_delay()
    
    auth_result = {
        'success': True,
        'user_data': {
            'id': 1,
            'name': 'Store Admin',
            'email': 'admin@demo-store.com',
            'roles': ['administrator']
        },
        'message': 'Successfully authenticated as Store Admin'
    }
    
    if auth_result['success']:
        print_success(f"Authenticated as: {auth_result['user_data']['name']}")
        print_info(f"User ID: {auth_result['user_data']['id']}")
        print_info(f"Email: {auth_result['user_data']['email']}")
    else:
        print_error(f"Authentication failed: {auth_result['message']}")
        return False
    
    # Step 2: Get Store Information
    print_step(2, "Getting Store Information")
    simulate_delay()
    
    print_info("Fetching store details...")
    simulate_delay()
    
    store_info = {
        'success': True,
        'store_name': 'Demo WooCommerce Store',
        'store_url': store_url,
        'woocommerce_version': '8.0.0',
        'wordpress_version': '6.3.0',
        'currency': 'USD'
    }
    
    if store_info['success']:
        print_success(f"Store: {store_info['store_name']}")
        print_info(f"WooCommerce Version: {store_info['woocommerce_version']}")
        print_info(f"WordPress Version: {store_info['wordpress_version']}")
        print_info(f"Currency: {store_info['currency']}")
    else:
        print_error(f"Failed to get store info: {store_info['message']}")
        return False
    
    # Step 3: Generate API Keys
    print_step(3, "Generating WooCommerce API Keys")
    simulate_delay()
    
    print_info("Generating API keys via REST endpoint...")
    simulate_delay()
    
    api_keys = client.generate_api_keys_via_rest()
    
    if api_keys['success']:
        print_success("API keys generated successfully")
        print_info(f"Consumer Key: {api_keys['consumer_key'][:20]}...")
        print_info(f"Consumer Secret: {api_keys['consumer_secret'][:20]}...")
        print_info(f"Key ID: {api_keys['key_id']}")
        print_info(f"Permissions: {api_keys['permissions']}")
        if api_keys.get('note'):
            print_warning(api_keys['note'])
    else:
        print_error(f"Failed to generate API keys: {api_keys['message']}")
        return False
    
    # Step 4: Test API Keys
    print_step(4, "Testing API Keys")
    simulate_delay()
    
    print_info("Testing API keys with WooCommerce API...")
    simulate_delay()
    
    # For demo purposes, we'll simulate a successful test
    test_result = {
        'success': True,
        'message': 'API keys are working correctly',
        'orders_count': 0
    }
    
    if test_result['success']:
        print_success(test_result['message'])
        print_info(f"Orders accessible: {test_result['orders_count']}")
    else:
        print_warning(f"API key test failed: {test_result['message']}")
        print_info("Proceeding to store credentials anyway...")
    
    # Step 5: Store Credentials
    print_step(5, "Storing Credentials Securely")
    simulate_delay()
    
    print_info("Encrypting and storing credentials...")
    simulate_delay()
    
    try:
        store_id = db.store_credentials(
            store_url=store_url,
            store_name=store_info['store_name'],
            admin_username=username,
            consumer_key=api_keys['consumer_key'],
            consumer_secret=api_keys['consumer_secret'],
            key_id=api_keys['key_id'],
            permissions=api_keys['permissions'],
            description=api_keys['description']
        )
        
        print_success(f"Credentials stored successfully (ID: {store_id})")
        print_info("All sensitive data encrypted in database")
        
    except Exception as e:
        print_error(f"Failed to store credentials: {str(e)}")
        return False
    
    # Step 6: Verify Storage
    print_step(6, "Verifying Stored Credentials")
    simulate_delay()
    
    print_info("Retrieving and decrypting stored credentials...")
    simulate_delay()
    
    stored_credentials = db.get_credentials(store_url)
    
    if stored_credentials:
        print_success("Credentials retrieved and decrypted successfully")
        print_info(f"Store: {stored_credentials['store_name']}")
        print_info(f"Consumer Key: {stored_credentials['consumer_key'][:20]}...")
        print_info(f"Status: {stored_credentials['status']}")
    else:
        print_error("Failed to retrieve stored credentials")
        return False
    
    print("\n🎉 Integration completed successfully!")
    print("=" * 50)
    return True

def demo_failed_integration():
    """Demo a failed integration flow."""
    print("\n🚨 Demo: Failed WooCommerce Integration")
    print("=" * 50)
    
    # Mock data with invalid credentials
    store_url = "https://invalid-store.com"
    username = "wrong_user"
    password = "wrong_password"
    
    print(f"📝 Store URL: {store_url}")
    print(f"📝 Username: {username}")
    print(f"📝 Password: {'*' * len(password)}")
    
    # Initialize client
    client = WooCommerceClient(store_url, username, password)
    
    # Step 1: Test WordPress Authentication (fails)
    print_step(1, "Testing WordPress Authentication")
    simulate_delay()
    
    print_info("Making request to /wp-json/wp/v2/users/me")
    simulate_delay()
    
    # Simulate authentication failure
    auth_result = {
        'success': False,
        'error': 'HTTP 401: Unauthorized',
        'message': 'Failed to authenticate with WordPress'
    }
    
    print_error(f"Authentication failed: {auth_result['message']}")
    print_info(f"Error: {auth_result['error']}")
    print_info("Please check your credentials and try again.")
    
    print("\n❌ Integration failed at authentication step")
    print("=" * 50)
    return False

def demo_database_operations():
    """Demo database operations."""
    print("\n💾 Demo: Database Operations")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # List stores
    print_step(1, "Listing Connected Stores")
    stores = db.list_stores()
    
    if stores:
        print_success(f"Found {len(stores)} connected store(s):")
        for i, store in enumerate(stores, 1):
            print(f"  {i}. {store['store_name']} - {store['store_url']}")
            print(f"     Status: {store['status']}")
            print(f"     Connected: {store['created_at']}")
    else:
        print_info("No stores connected yet")
    
    # Show logs
    print_step(2, "Viewing Connection Logs")
    logs = db.get_logs(limit=5)
    
    if logs:
        print_success(f"Showing last {len(logs)} log entries:")
        for log in logs:
            status_icon = "✅" if log['status'] == 'success' else "❌"
            print(f"  {status_icon} {log['timestamp']} - {log['action']}")
            print(f"     Message: {log['message']}")
    else:
        print_info("No logs found")
    
    print("\n📊 Database operations completed")
    print("=" * 50)

def main():
    """Main demo function."""
    print("🚀 WooCommerce API Integration - Demo")
    print("=" * 50)
    
    try:
        # Run successful integration demo
        success = demo_successful_integration()
        
        if success:
            # Show database operations
            demo_database_operations()
            
            # Run failed integration demo
            demo_failed_integration()
        
        print("\n🎬 Demo completed!")
        print("=" * 50)
        print("💡 Key Points:")
        print("- WordPress authentication is the first step")
        print("- API keys are generated programmatically")
        print("- All sensitive data is encrypted before storage")
        print("- Connection logs track all activities")
        print("- Error handling provides clear feedback")
        print("\n🔧 For production use:")
        print("- Install helper_plugin.php on target WooCommerce stores")
        print("- Use proper authentication (OAuth, Application passwords)")
        print("- Implement comprehensive error handling")
        print("- Add monitoring and alerting")
        print("- Use production-grade database (PostgreSQL/MySQL)")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 