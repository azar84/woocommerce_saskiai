#!/usr/bin/env python3
"""
Interactive WordPress Authentication Troubleshooter
This script walks you through each possible authentication issue step by step.
"""

import requests
import getpass
import sys

def step1_verify_site_access():
    """Step 1: Verify the site is accessible."""
    print("🔍 STEP 1: Verify Site Access")
    print("=" * 40)
    
    store_url = input("Enter your store URL (e.g., https://yourstore.com): ").strip()
    
    if not store_url:
        print("❌ Store URL is required!")
        return None
    
    # Normalize URL
    if not store_url.startswith(('http://', 'https://')):
        store_url = 'https://' + store_url
    store_url = store_url.rstrip('/')
    
    print(f"\n🌐 Testing basic access to: {store_url}")
    
    try:
        response = requests.get(f"{store_url}/wp-json/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Site is accessible!")
            print(f"   📋 Site name: {data.get('name', 'Unknown')}")
            print(f"   📋 Description: {data.get('description', 'Unknown')}")
            
            # Check for WooCommerce
            if 'wc/v3' in data.get('namespaces', []):
                print(f"   ✅ WooCommerce detected!")
            else:
                print(f"   ⚠️  WooCommerce not detected")
                
            return store_url
        else:
            print(f"❌ Site not accessible (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Cannot access site: {str(e)}")
        return None

def step2_verify_credentials(store_url):
    """Step 2: Verify WordPress admin credentials."""
    print(f"\n🔑 STEP 2: Verify WordPress Admin Credentials")
    print("=" * 50)
    
    print("📌 IMPORTANT NOTES:")
    print("   - Use your WordPress admin USERNAME (not email address)")
    print("   - Use your regular WordPress password (not application password)")
    print("   - Make sure you can log into WordPress admin panel manually")
    print("")
    
    # Get credentials
    username = input("Enter your WordPress admin username: ").strip()
    password = getpass.getpass("Enter your WordPress admin password: ")
    
    if not username or not password:
        print("❌ Both username and password are required!")
        return None, None
    
    print(f"\n🧪 Testing authentication...")
    print(f"   Store: {store_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    try:
        auth = (username, password)
        
        # First, test WooCommerce REST API (this is what actually matters)
        wc_response = requests.get(f"{store_url}/wp-json/wc/v3/system_status", 
                                  auth=auth, timeout=15)
        
        if wc_response.status_code == 200:
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print(f"   👤 Username: {username}")
            print("   ✅ WooCommerce REST API access confirmed")
            print("   ✅ User has sufficient permissions for WooCommerce integration")
            return username, password
        elif wc_response.status_code == 401:
            print("❌ AUTHENTICATION FAILED - Invalid credentials")
            return None, None
        elif wc_response.status_code == 403:
            print("❌ ACCESS DENIED - User authenticated but lacks WooCommerce permissions")
            print("   💡 User needs Administrator role or WooCommerce manager capabilities")
            return None, None
        else:
            # Try WordPress REST API as fallback
            wp_response = requests.get(f"{store_url}/wp-json/wp/v2/users/me", 
                                     auth=auth, timeout=15)
            
            if wp_response.status_code == 200:
                data = wp_response.json()
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print(f"   👤 Username: {username}")
                print(f"   👤 Display name: {data.get('name', 'Unknown')}")
                print(f"   👤 User ID: {data.get('id', 'Unknown')}")
                print(f"   👤 Email: {data.get('email', 'Unknown')}")
                
                # Check if user can access WooCommerce
                roles = data.get('roles', [])
                if roles:
                    print(f"   👤 Roles: {', '.join(roles)}")
                    if 'administrator' in roles:
                        print("   ✅ User has administrator role - PERFECT!")
                        return username, password
                    else:
                        print("   ⚠️  User doesn't have Administrator role - might have issues")
                        print("   💡 Consider giving user Administrator role for full WooCommerce access")
                        return username, password
                else:
                    print("   ⚠️  Could not determine user roles, but authentication works")
                    print("   💡 If you're an admin, this should work fine")
                    return username, password
            elif wp_response.status_code == 401:
                print("❌ AUTHENTICATION FAILED - Invalid credentials")
                return None, None
            elif wp_response.status_code == 403:
                print("❌ ACCESS DENIED - User authenticated but lacks permissions")
                return None, None
            else:
                print(f"❓ Unexpected response: WC API {wc_response.status_code}, WP API {wp_response.status_code}")
                return None, None
            
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
        return None, None

def step3_troubleshoot_auth_issues(store_url):
    """Step 3: Troubleshoot common authentication issues."""
    print(f"\n🛠️  STEP 3: Troubleshooting Authentication Issues")
    print("=" * 55)
    
    print("Let's check common authentication problems:")
    
    # Check 1: Username format
    print("\n1️⃣ Username Format Check")
    print("   ❓ Are you using your WordPress username or email address?")
    print("   ✅ CORRECT: Use WordPress username (e.g., 'admin', 'john_doe')")
    print("   ❌ INCORRECT: Using email address (e.g., 'admin@yourstore.com')")
    
    username_check = input("   Enter 'y' if you're using WordPress username (not email): ").lower()
    if username_check != 'y':
        print("   💡 FIX: Go to WordPress admin → Users → find your user → note the 'Username' field")
        print("        This is what you should use, NOT the email address!")
    
    # Check 2: Password verification
    print("\n2️⃣ Password Verification")
    print("   ❓ Can you log into WordPress admin panel manually?")
    print("   1. Open: {}/wp-admin/".format(store_url))
    print("   2. Try logging in with the same username/password")
    
    login_check = input("   Enter 'y' if you can log into WordPress admin successfully: ").lower()
    if login_check != 'y':
        print("   💡 FIX: Reset your WordPress password or use a different admin user")
        return
    
    # Check 3: Two-factor authentication
    print("\n3️⃣ Two-Factor Authentication Check")
    print("   ❓ Do you have two-factor authentication (2FA) enabled?")
    print("   ❓ Are you using plugins like Wordfence, Google Authenticator, etc.?")
    
    tfa_check = input("   Enter 'y' if you have 2FA/security plugins: ").lower()
    if tfa_check == 'y':
        print("   💡 FIX OPTIONS:")
        print("      Option 1: Temporarily disable 2FA/security plugins")
        print("      Option 2: Create an Application Password (see step 4)")
        print("      Option 3: Add your IP to security plugin whitelist")
    
    # Check 4: Application passwords
    print("\n4️⃣ Application Password Option")
    print("   💡 If regular password doesn't work, try creating an Application Password:")
    print("   1. Go to WordPress admin → Users → Your Profile")
    print("   2. Scroll down to 'Application Passwords' section")
    print("   3. Enter a name like 'WooCommerce Integration'")
    print("   4. Click 'Add New Application Password'")
    print("   5. Copy the generated password and use it instead of your regular password")
    
    app_pass_check = input("   Enter 'y' to try creating an Application Password: ").lower()
    if app_pass_check == 'y':
        print("   📋 Steps to create Application Password:")
        print("      1. Open: {}/wp-admin/profile.php".format(store_url))
        print("      2. Scroll to 'Application Passwords'")
        print("      3. Name: 'WooCommerce Integration'")
        print("      4. Click 'Add New Application Password'")
        print("      5. Copy the generated password")
        print("      6. Use your regular username with the NEW application password")
        
        app_password = getpass.getpass("   Enter the Application Password (or press Enter to skip): ")
        if app_password:
            username = input("   Enter your WordPress username: ").strip()
            if username and app_password:
                return test_application_password(store_url, username, app_password)
    
    # Check 5: Security plugins
    print("\n5️⃣ Security Plugin Check")
    print("   Common security plugins that can block REST API:")
    print("   - Wordfence Security")
    print("   - iThemes Security")
    print("   - Sucuri Security")
    print("   - All In One WP Security")
    
    security_check = input("   Enter 'y' if you have security plugins installed: ").lower()
    if security_check == 'y':
        print("   💡 FIX OPTIONS:")
        print("      1. Temporarily disable security plugins")
        print("      2. Whitelist your IP address in security plugin settings")
        print("      3. Enable REST API access in security plugin settings")
        print("      4. Check plugin logs for blocked requests")
    
    return None, None

def test_application_password(store_url, username, app_password):
    """Test with application password."""
    print(f"\n🧪 Testing Application Password...")
    
    try:
        auth = (username, app_password)
        
        # First, test WooCommerce REST API (this is what actually matters)
        wc_response = requests.get(f"{store_url}/wp-json/wc/v3/system_status", 
                                  auth=auth, timeout=15)
        
        if wc_response.status_code == 200:
            print("✅ APPLICATION PASSWORD WORKS!")
            print(f"   👤 Username: {username}")
            print("   ✅ WooCommerce REST API access confirmed")
            print("   ✅ User has sufficient permissions for WooCommerce integration")
            print("   ✅ Ready to connect! Use these credentials in the web interface:")
            print(f"      Username: {username}")
            print(f"      Password: {app_password}")
            return username, app_password
        elif wc_response.status_code == 401:
            print("❌ Application password authentication failed")
            return None, None
        elif wc_response.status_code == 403:
            print("❌ Application password works but user lacks WooCommerce permissions")
            print("   💡 User needs Administrator role or WooCommerce manager capabilities")
            return None, None
        else:
            # Try WordPress REST API as fallback
            wp_response = requests.get(f"{store_url}/wp-json/wp/v2/users/me", 
                                     auth=auth, timeout=15)
            
            if wp_response.status_code == 200:
                data = wp_response.json()
                print("✅ APPLICATION PASSWORD WORKS!")
                print(f"   👤 Username: {username}")
                print(f"   👤 Display name: {data.get('name', 'Unknown')}")
                print(f"   👤 User ID: {data.get('id', 'Unknown')}")
                
                # Check if user can access WooCommerce
                roles = data.get('roles', [])
                if roles:
                    print(f"   👤 Roles: {', '.join(roles)}")
                    if 'administrator' in roles:
                        print("   ✅ User has Administrator role - should work with WooCommerce")
                        return username, app_password
                    else:
                        print("   ⚠️  User doesn't have Administrator role - might have issues")
                        print("   💡 Consider giving user Administrator role for full WooCommerce access")
                        return username, app_password
                else:
                    print("   ⚠️  Could not determine user roles, but authentication works")
                    print("   💡 If you're an admin, this should work fine")
                    return username, app_password
            else:
                print(f"❌ Application password failed (Status: {wc_response.status_code})")
                return None, None
            
    except Exception as e:
        print(f"❌ Application password test failed: {str(e)}")
        return None, None

def main():
    """Main troubleshooting workflow."""
    print("🔐 WordPress Authentication Troubleshooter")
    print("This tool will help you solve authentication issues step by step")
    print("=" * 65)
    
    # Step 1: Verify site access
    store_url = step1_verify_site_access()
    if not store_url:
        print("\n❌ Cannot proceed - site is not accessible")
        return
    
    # Step 2: Try normal authentication
    username, password = step2_verify_credentials(store_url)
    if username and password:
        print(f"\n🎉 SUCCESS! Your credentials work:")
        print(f"   Store URL: {store_url}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        print(f"\n✅ You can now use these credentials in the web interface:")
        print(f"   🌐 Go to: http://localhost:3000/connect")
        print(f"   🔧 Enter the same credentials")
        return
    
    # Step 3: Troubleshoot issues
    print(f"\n❌ Authentication failed - let's troubleshoot...")
    result = step3_troubleshoot_auth_issues(store_url)
    if result and result[0] and result[1]:
        username, password = result
        print(f"\n🎉 SUCCESS! Use these credentials:")
        print(f"   Store URL: {store_url}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        print(f"\n✅ Go to: http://localhost:3000/connect")
    else:
        print(f"\n📞 NEED MORE HELP?")
        print(f"   1. Contact your hosting provider")
        print(f"   2. Check WordPress error logs")
        print(f"   3. Try with a fresh WordPress admin user")
        print(f"   4. Disable all security plugins temporarily")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Troubleshooting cancelled by user")
        sys.exit(0) 