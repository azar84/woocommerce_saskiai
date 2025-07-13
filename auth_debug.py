#!/usr/bin/env python3
"""
Detailed authentication debugger for WooCommerce integration.
This script helps identify specific authentication issues.
"""

import requests
import json
import base64
from urllib.parse import urlparse

def test_wordpress_auth_methods(store_url, username, password):
    """Test different WordPress authentication methods."""
    print(f"🔍 Testing authentication methods for: {store_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print("-" * 60)
    
    # Normalize URL
    if not store_url.startswith(('http://', 'https://')):
        store_url = 'https://' + store_url
    store_url = store_url.rstrip('/')
    
    # Test 1: Basic connectivity
    print("1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{store_url}/wp-json/", timeout=10)
        print(f"   ✅ Basic connectivity: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 Site name: {data.get('name', 'Unknown')}")
            print(f"   📋 Description: {data.get('description', 'Unknown')}")
            print(f"   📋 WordPress version: {data.get('gmt_offset', 'Unknown')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return
    
    # Test 2: Check if REST API authentication is available
    print("\n2️⃣ Testing REST API authentication availability...")
    try:
        response = requests.get(f"{store_url}/wp-json/wp/v2/users/me", timeout=10)
        print(f"   📋 No-auth status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Authentication required (this is expected)")
        elif response.status_code == 403:
            print("   ⚠️  Forbidden - REST API might be disabled")
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
    
    # Test 3: Try Basic Authentication
    print("\n3️⃣ Testing Basic Authentication...")
    try:
        auth = (username, password)
        response = requests.get(f"{store_url}/wp-json/wp/v2/users/me", 
                              auth=auth, timeout=10)
        print(f"   📋 Basic auth status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Authentication successful!")
            print(f"   👤 User ID: {data.get('id')}")
            print(f"   👤 Username: {data.get('username')}")
            print(f"   👤 Display name: {data.get('name')}")
            print(f"   👤 Email: {data.get('email')}")
            print(f"   👤 Roles: {data.get('roles', [])}")
            
            # Check if user is admin
            if 'administrator' in data.get('roles', []):
                print("   ✅ User has administrator role")
            else:
                print("   ❌ User does NOT have administrator role")
                print("   💡 This might be the issue - user needs admin privileges")
                
        elif response.status_code == 401:
            print("   ❌ Authentication failed - Invalid credentials")
            print("   💡 Possible causes:")
            print("      - Username is incorrect (try without @ symbol)")
            print("      - Password is incorrect")
            print("      - Two-factor authentication is enabled")
            print("      - Application passwords are required")
            
        elif response.status_code == 403:
            print("   ❌ Forbidden - User authenticated but access denied")
            print("   💡 Possible causes:")
            print("      - User doesn't have sufficient permissions")
            print("      - REST API is disabled for this user role")
            print("      - Security plugin is blocking access")
            
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
            print(f"   📋 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
    
    # Test 4: Check for Application Passwords
    print("\n4️⃣ Testing Application Passwords support...")
    try:
        response = requests.get(f"{store_url}/wp-json/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            auth_methods = data.get('authentication', {})
            if 'application-passwords' in str(auth_methods).lower():
                print("   ✅ Application Passwords might be supported")
                print("   💡 Try creating an Application Password in WordPress admin")
            else:
                print("   📋 No specific Application Password info found")
        else:
            print("   ❌ Could not check Application Password support")
    except Exception as e:
        print(f"   ❌ Check failed: {str(e)}")
    
    # Test 5: Check common WordPress configurations
    print("\n5️⃣ Checking WordPress configuration...")
    
    # Check if it's a multisite
    try:
        response = requests.get(f"{store_url}/wp-json/wp/v2/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 WordPress API available: Yes")
            print(f"   📋 Namespaces: {data.get('namespaces', [])}")
            
            # Check for WooCommerce
            if 'wc/v3' in data.get('namespaces', []):
                print("   ✅ WooCommerce API detected")
            else:
                print("   ⚠️  WooCommerce API not found")
                
        else:
            print(f"   ❌ WordPress API check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Configuration check failed: {str(e)}")

def main():
    """Main function to run authentication debugging."""
    print("🔐 WordPress Authentication Debugger")
    print("=" * 60)
    
    # You can modify these values or make them interactive
    print("\n💡 INSTRUCTIONS:")
    print("1. Edit this script and replace the example values below")
    print("2. Or run it interactively by uncommenting the input lines")
    print("3. Make sure to use your WordPress admin USERNAME (not email)")
    print("4. Use your regular WordPress password (not an application password)")
    print("\n" + "=" * 60)
    
    # Example values - REPLACE THESE WITH YOUR ACTUAL VALUES
    store_url = "https://your-store.com"  # Replace with your store URL
    username = "admin"  # Replace with your WordPress admin username
    password = "your-password"  # Replace with your WordPress admin password
    
    # Uncomment these lines to make it interactive:
    # store_url = input("Enter your store URL: ").strip()
    # username = input("Enter your WordPress admin username: ").strip()
    # password = input("Enter your WordPress admin password: ").strip()
    
    if store_url == "https://your-store.com":
        print("\n❌ Please edit this script and replace the example values!")
        print("   Look for the lines starting with 'store_url =', 'username =', 'password ='")
        return
    
    test_wordpress_auth_methods(store_url, username, password)
    
    print("\n" + "=" * 60)
    print("💡 TROUBLESHOOTING TIPS:")
    print("- If you get 401 errors, double-check your username and password")
    print("- Username should be your WordPress login name, not email address")
    print("- Try logging into your WordPress admin panel manually first")
    print("- Check if two-factor authentication is enabled")
    print("- Some security plugins block REST API authentication")
    print("- Consider creating an Application Password in WordPress admin")
    print("=" * 60)

if __name__ == "__main__":
    main() 