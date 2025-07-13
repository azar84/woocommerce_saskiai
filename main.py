#!/usr/bin/env python3
"""
WooCommerce API Key Generation and Storage - Proof of Concept
=============================================================

This script demonstrates how to:
1. Authenticate with WordPress/WooCommerce
2. Generate API keys programmatically
3. Store credentials securely in a database
4. Test the generated API keys

Usage:
    python main.py

Author: Saski AI Integration Team
"""

import sys
import getpass
from datetime import datetime
from database import DatabaseManager
from woocommerce_client import WooCommerceClient

class WooCommerceIntegrationApp:
    def __init__(self):
        self.db = DatabaseManager()
        print("🚀 WooCommerce API Integration - Proof of Concept")
        print("=" * 50)
    
    def display_menu(self):
        """Display the main menu options."""
        print("\n📋 Available Actions:")
        print("1. Connect New Store")
        print("2. List Connected Stores")
        print("3. Test Store Connection")
        print("4. View Connection Logs")
        print("5. Disconnect Store")
        print("6. Exit")
        print("-" * 30)
    
    def get_user_input(self, prompt, hidden=False):
        """Get user input with optional hidden input for passwords."""
        if hidden:
            return getpass.getpass(f"🔑 {prompt}: ")
        else:
            return input(f"📝 {prompt}: ").strip()
    
    def validate_store_url(self, url):
        """Validate and normalize store URL."""
        if not url:
            return None
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url
    
    def connect_new_store(self):
        """Connect a new WooCommerce store."""
        print("\n🔗 Connect New WooCommerce Store")
        print("-" * 35)
        
        # Get store details
        store_url = self.get_user_input("Store URL (e.g., https://example.com)")
        store_url = self.validate_store_url(store_url)
        
        if not store_url:
            print("❌ Invalid store URL provided")
            return
        
        username = self.get_user_input("Admin Username")
        password = self.get_user_input("Admin Password", hidden=True)
        
        if not username or not password:
            print("❌ Username and password are required")
            return
        
        print(f"\n🔍 Connecting to {store_url}...")
        
        # Initialize WooCommerce client
        client = WooCommerceClient(store_url, username, password)
        
        # Step 1: Test WordPress authentication
        print("1️⃣ Testing WordPress authentication...")
        auth_result = client.test_wordpress_connection()
        
        if not auth_result['success']:
            print(f"❌ Authentication failed: {auth_result['message']}")
            print(f"   Error: {auth_result.get('error', 'Unknown error')}")
            return
        
        print(f"✅ Authenticated successfully as: {auth_result['user_data'].get('name', 'Unknown')}")
        
        # Step 2: Get store information
        print("2️⃣ Getting store information...")
        store_info = client.get_store_info()
        
        if not store_info['success']:
            print(f"❌ Failed to get store info: {store_info['message']}")
            return
        
        store_name = store_info.get('store_name', 'Unknown Store')
        print(f"✅ Store name: {store_name}")
        
        # Step 3: Generate API keys
        print("3️⃣ Generating WooCommerce API keys...")
        api_keys = client.generate_api_keys_via_rest()
        
        if not api_keys['success']:
            print(f"❌ Failed to generate API keys: {api_keys['message']}")
            return
        
        consumer_key = api_keys['consumer_key']
        consumer_secret = api_keys['consumer_secret']
        key_id = api_keys.get('key_id')
        
        print(f"✅ API keys generated successfully")
        if api_keys.get('note'):
            print(f"ℹ️  Note: {api_keys['note']}")
        
        # Step 4: Test API keys
        print("4️⃣ Testing API keys...")
        test_result = client.test_api_keys(consumer_key, consumer_secret)
        
        if not test_result['success']:
            print(f"⚠️  API key test failed: {test_result['message']}")
            print(f"   Error: {test_result.get('error', 'Unknown error')}")
            print("   Proceeding to store credentials anyway...")
        else:
            print(f"✅ API keys are working correctly")
        
        # Step 5: Store credentials securely
        print("5️⃣ Storing credentials securely...")
        try:
            store_id = self.db.store_credentials(
                store_url=store_url,
                store_name=store_name,
                admin_username=username,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                key_id=key_id,
                permissions=api_keys.get('permissions', 'read_write'),
                description=api_keys.get('description', 'Auto-generated')
            )
            
            print(f"✅ Credentials stored successfully (ID: {store_id})")
            print(f"🎉 Store '{store_name}' connected successfully!")
            
        except Exception as e:
            print(f"❌ Failed to store credentials: {str(e)}")
    
    def list_connected_stores(self):
        """List all connected stores."""
        print("\n📊 Connected Stores")
        print("-" * 20)
        
        stores = self.db.list_stores()
        
        if not stores:
            print("🔍 No stores connected yet")
            return
        
        print(f"Found {len(stores)} connected store(s):\n")
        
        for i, store in enumerate(stores, 1):
            print(f"{i}. {store['store_name'] or 'Unknown Store'}")
            print(f"   URL: {store['store_url']}")
            print(f"   Permissions: {store['permissions']}")
            print(f"   Connected: {store['created_at']}")
            print(f"   Status: {store['status']}")
            print()
    
    def test_store_connection(self):
        """Test an existing store connection."""
        print("\n🧪 Test Store Connection")
        print("-" * 25)
        
        stores = self.db.list_stores()
        
        if not stores:
            print("🔍 No stores connected yet")
            return
        
        # Display available stores
        print("Available stores:")
        for i, store in enumerate(stores, 1):
            print(f"{i}. {store['store_name']} ({store['store_url']})")
        
        try:
            choice = int(self.get_user_input("Select store number")) - 1
            if choice < 0 or choice >= len(stores):
                print("❌ Invalid selection")
                return
            
            selected_store = stores[choice]
            store_url = selected_store['store_url']
            
            # Get credentials
            credentials = self.db.get_credentials(store_url)
            if not credentials:
                print("❌ Could not retrieve credentials")
                return
            
            print(f"\n🔍 Testing connection to {credentials['store_name']}...")
            
            # Initialize client
            client = WooCommerceClient(store_url)
            
            # Test API keys
            test_result = client.test_api_keys(
                credentials['consumer_key'],
                credentials['consumer_secret']
            )
            
            if test_result['success']:
                print("✅ Connection test successful!")
                
                # Try to get some data
                print("\n📦 Testing data retrieval...")
                
                # Test orders
                orders_result = client.get_orders(
                    credentials['consumer_key'],
                    credentials['consumer_secret'],
                    limit=5
                )
                
                if orders_result['success']:
                    print(f"   Orders: {orders_result['count']} retrieved")
                else:
                    print(f"   Orders: Failed - {orders_result['message']}")
                
                # Test products
                products_result = client.get_products(
                    credentials['consumer_key'],
                    credentials['consumer_secret'],
                    limit=5
                )
                
                if products_result['success']:
                    print(f"   Products: {products_result['count']} retrieved")
                else:
                    print(f"   Products: Failed - {products_result['message']}")
                
            else:
                print(f"❌ Connection test failed: {test_result['message']}")
                print(f"   Error: {test_result.get('error', 'Unknown error')}")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def view_connection_logs(self):
        """View connection logs."""
        print("\n📋 Connection Logs")
        print("-" * 18)
        
        logs = self.db.get_logs(limit=20)
        
        if not logs:
            print("🔍 No logs found")
            return
        
        print(f"Showing last {len(logs)} log entries:\n")
        
        for log in logs:
            timestamp = log['timestamp']
            status_icon = "✅" if log['status'] == 'success' else "❌"
            store_url = log['store_url'] or 'Unknown Store'
            
            print(f"{status_icon} {timestamp} - {log['action']}")
            print(f"   Store: {store_url}")
            print(f"   Message: {log['message']}")
            print()
    
    def disconnect_store(self):
        """Disconnect a store."""
        print("\n🔌 Disconnect Store")
        print("-" * 18)
        
        stores = self.db.list_stores()
        
        if not stores:
            print("🔍 No stores connected yet")
            return
        
        # Display available stores
        print("Available stores:")
        for i, store in enumerate(stores, 1):
            print(f"{i}. {store['store_name']} ({store['store_url']})")
        
        try:
            choice = int(self.get_user_input("Select store number to disconnect")) - 1
            if choice < 0 or choice >= len(stores):
                print("❌ Invalid selection")
                return
            
            selected_store = stores[choice]
            store_url = selected_store['store_url']
            store_name = selected_store['store_name']
            
            # Confirm disconnection
            confirm = self.get_user_input(f"Are you sure you want to disconnect '{store_name}'? (y/N)")
            
            if confirm.lower() != 'y':
                print("❌ Disconnection cancelled")
                return
            
            # Disconnect
            if self.db.disconnect_store(store_url):
                print(f"✅ Successfully disconnected '{store_name}'")
            else:
                print(f"❌ Failed to disconnect '{store_name}'")
                
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def run(self):
        """Run the main application loop."""
        while True:
            self.display_menu()
            
            try:
                choice = self.get_user_input("Select an option (1-6)")
                
                if choice == '1':
                    self.connect_new_store()
                elif choice == '2':
                    self.list_connected_stores()
                elif choice == '3':
                    self.test_store_connection()
                elif choice == '4':
                    self.view_connection_logs()
                elif choice == '5':
                    self.disconnect_store()
                elif choice == '6':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")
                print("Please try again.")

def main():
    """Main entry point."""
    try:
        app = WooCommerceIntegrationApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 