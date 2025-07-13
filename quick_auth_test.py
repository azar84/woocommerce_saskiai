#!/usr/bin/env python3
"""
Quick interactive authentication test for WooCommerce integration.
This script prompts for credentials and tests authentication immediately.
"""

import requests
import getpass
import sys

def quick_auth_test():
    """Quick interactive authentication test."""
    print("🔐 Quick WordPress Authentication Test")
    print("=" * 50)
    
    # Get credentials interactively
    store_url = input("Enter your store URL (e.g., https://yourstore.com): ").strip()
    username = input("Enter your WordPress admin USERNAME (not email): ").strip()
    password = getpass.getpass("Enter your WordPress admin password: ")
    
    if not store_url or not username or not password:
        print("❌ All fields are required!")
        return
    
    # Normalize URL
    if not store_url.startswith(('http://', 'https://')):
        store_url = 'https://' + store_url
    store_url = store_url.rstrip('/')
    
    print(f"\n🔍 Testing authentication for: {store_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print("-" * 50)
    
    try:
        # Test authentication
        auth = (username, password)
        response = requests.get(f"{store_url}/wp-json/wp/v2/users/me", 
                              auth=auth, timeout=15)
        
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print(f"   👤 User ID: {data.get('id')}")
            print(f"   👤 Username: {data.get('username')}")
            print(f"   👤 Display name: {data.get('name')}")
            print(f"   👤 Email: {data.get('email')}")
            print(f"   👤 Roles: {', '.join(data.get('roles', []))}")
            
            # Check if user is admin
            if 'administrator' in data.get('roles', []):
                print("   ✅ User has administrator role - READY TO CONNECT!")
            else:
                print("   ❌ User does NOT have administrator role")
                print("   💡 User needs Administrator role to use WooCommerce integration")
                
            # Test WooCommerce API access
            print("\n🛒 Testing WooCommerce API access...")
            wc_response = requests.get(f"{store_url}/wp-json/wc/v3/system_status", 
                                     auth=auth, timeout=10)
            if wc_response.status_code == 200:
                print("   ✅ WooCommerce API is accessible")
            elif wc_response.status_code == 401:
                print("   ❌ WooCommerce API requires different authentication")
            else:
                print(f"   ⚠️  WooCommerce API status: {wc_response.status_code}")
                
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED - Invalid credentials")
            print("\n💡 TROUBLESHOOTING STEPS:")
            print("1. ✅ Double-check your WordPress username (not email address)")
            print("2. ✅ Verify your password by logging into WordPress admin")
            print("3. ✅ Make sure two-factor authentication is disabled")
            print("4. ✅ Check if your user has Administrator role")
            print("5. ✅ Try creating an Application Password in WordPress admin")
            
        elif response.status_code == 403:
            print("❌ ACCESS DENIED - User authenticated but lacks permissions")
            print("\n💡 TROUBLESHOOTING STEPS:")
            print("1. ✅ Ensure user has Administrator role in WordPress")
            print("2. ✅ Check if security plugins are blocking REST API")
            print("3. ✅ Verify REST API is enabled for your user role")
            
        elif response.status_code == 404:
            print("❌ REST API NOT FOUND")
            print("\n💡 TROUBLESHOOTING STEPS:")
            print("1. ✅ Ensure WordPress is properly installed")
            print("2. ✅ Check if REST API is enabled (should be by default)")
            print("3. ✅ Verify permalinks are working in WordPress")
            
        else:
            print(f"❓ UNEXPECTED RESPONSE: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED - Cannot reach the store")
        print("\n💡 TROUBLESHOOTING STEPS:")
        print("1. ✅ Check the store URL is correct")
        print("2. ✅ Ensure the website is online and accessible")
        print("3. ✅ Try with www. prefix if not using it (or vice versa)")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Store is taking too long to respond")
        print("\n💡 TROUBLESHOOTING STEPS:")
        print("1. ✅ Check your internet connection")
        print("2. ✅ Try again later - server might be busy")
        print("3. ✅ Contact your hosting provider if issue persists")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("💡 If authentication is successful, you can now use the web interface:")
    print("   🌐 Go to: http://localhost:3000/connect")
    print("   🔧 Use the same credentials to connect your store")
    print("=" * 50)

if __name__ == "__main__":
    try:
        quick_auth_test()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(0) 