#!/usr/bin/env python3
"""
Test script to demonstrate the debug functionality for WooCommerce integration.
"""

import requests
import json

def test_debug_connection(store_url):
    """Test the debug connection endpoint."""
    print(f"🔍 Testing debug connection for: {store_url}")
    
    try:
        response = requests.post('http://localhost:3000/api/debug-connection', 
                               json={'store_url': store_url})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Debug test successful!")
            print(f"   Store URL: {result['debug_info']['store_url']}")
            
            connectivity = result['debug_info']['basic_connectivity']
            if connectivity.get('accessible'):
                print(f"   ✅ Store is accessible (Status: {connectivity['status_code']})")
            else:
                print(f"   ❌ Store not accessible: {connectivity.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Debug test failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {str(e)}")

def test_auth_connection(store_url, username, password):
    """Test the authentication connection endpoint."""
    print(f"🔑 Testing authentication for: {store_url}")
    
    try:
        response = requests.post('http://localhost:3000/api/test-connection', 
                               json={
                                   'store_url': store_url,
                                   'username': username,
                                   'password': password
                               })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Authentication test successful!")
            print(f"   Store: {result['store_name']}")
            print(f"   User: {result['user_name']}")
        else:
            result = response.json()
            print(f"❌ Authentication test failed with status {response.status_code}")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            if 'debug_info' in result:
                print(f"   Debug info: {result['debug_info']}")
                
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")

if __name__ == "__main__":
    print("🌐 WooCommerce Integration Debug Tool")
    print("=" * 50)
    
    # Test examples
    test_stores = [
        "https://demo.woothemes.com",  # Example WooCommerce demo
        "https://woocommerce.com",     # Official WooCommerce site
        "https://example.com",         # Non-WordPress site
        "https://nonexistent-site-12345.com",  # Non-existent site
    ]
    
    for store_url in test_stores:
        print(f"\n📍 Testing: {store_url}")
        test_debug_connection(store_url)
        print("-" * 40)
    
    print("\n💡 To test with your own store:")
    print("1. Go to http://localhost:3000/connect")
    print("2. Enter your store URL")
    print("3. Click 'Debug URL' to test basic connectivity")
    print("4. If successful, enter credentials and click 'Test Connection'")
    print("5. If that works, click 'Connect Store' to save the connection") 