import requests
import base64
import json
import urllib.parse
from datetime import datetime
from config import WORDPRESS_API_BASE, WOOCOMMERCE_API_BASE, REQUEST_TIMEOUT, DEFAULT_PERMISSIONS, DEFAULT_DESCRIPTION

class WooCommerceClient:
    def __init__(self, store_url, username=None, password=None):
        self.store_url = store_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT
        
        # Set up basic auth if credentials provided
        if username and password:
            self.session.auth = (username, password)
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make an HTTP request to the WordPress/WooCommerce API."""
        url = f"{self.store_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Saski AI WooCommerce Integration/1.0'
                }
            )
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def test_wordpress_connection(self):
        """Test if we can authenticate with WordPress."""
        try:
            endpoint = f"{WORDPRESS_API_BASE}/users/me"
            user_data = self._make_request('GET', endpoint)
            
            return {
                'success': True,
                'user_data': user_data,
                'message': f"Successfully authenticated as {user_data.get('name', 'Unknown')}"
            }
        except Exception as e:
            error_msg = str(e)
            detailed_message = "Failed to authenticate with WordPress"
            error_code = "UNKNOWN_ERROR"
            troubleshooting_steps = []
            
            # Provide more specific error messages based on common issues
            if "401" in error_msg or "Unauthorized" in error_msg:
                # Check if it's actually a permission issue disguised as 401
                if "access denied" in error_msg.lower() or "lacks sufficient permissions" in error_msg.lower() or "lacks permissions" in error_msg.lower():
                    error_code = "ACCESS_DENIED"
                    detailed_message = "Access denied: User authenticated but lacks sufficient permissions"
                    troubleshooting_steps = [
                        "✓ Ensure user has Administrator role (not Editor, Author, or Contributor)",
                        "✓ Check WordPress user capabilities: go to Users > All Users > Edit user",
                        "✓ Verify user has 'manage_woocommerce' capability",
                        "✓ Temporarily deactivate security plugins (Wordfence, iThemes Security, etc.)",
                        "✓ Check if REST API is restricted by security plugins",
                        "✓ Verify WooCommerce is installed, activated, and properly configured",
                        "✓ Try creating a new Administrator user and test with that account",
                        "✓ Check if user account is part of a multisite network with restricted permissions"
                    ]
                else:
                    error_code = "AUTHENTICATION_FAILED"
                    detailed_message = "Authentication failed: Invalid username or password"
                    troubleshooting_steps = [
                        "✓ Use WordPress USERNAME (not email address)",
                        "✓ Verify password is correct",
                        "✓ Try creating an Application Password in WordPress admin",
                        "✓ Disable two-factor authentication temporarily",
                        "✓ Check if user account is active and not locked"
                    ]
            elif "404" in error_msg or "Not Found" in error_msg:
                error_code = "API_NOT_FOUND"
                detailed_message = "WordPress REST API not found"
                troubleshooting_steps = [
                    "✓ Ensure WordPress is properly installed and up-to-date",
                    "✓ Check if REST API is enabled (usually enabled by default)",
                    "✓ Verify the store URL is correct",
                    "✓ Check for custom URL structures or redirects"
                ]
            elif "403" in error_msg or "Forbidden" in error_msg:
                error_code = "ACCESS_DENIED"
                detailed_message = "Access denied: User authenticated but lacks sufficient permissions"
                troubleshooting_steps = [
                    "✓ Ensure user has Administrator role (not Editor, Author, or Contributor)",
                    "✓ Check WordPress user capabilities: go to Users > All Users > Edit user",
                    "✓ Verify user has 'manage_woocommerce' capability",
                    "✓ Temporarily deactivate security plugins (Wordfence, iThemes Security, etc.)",
                    "✓ Check if REST API is restricted by security plugins",
                    "✓ Verify WooCommerce is installed, activated, and properly configured",
                    "✓ Try creating a new Administrator user and test with that account",
                    "✓ Check if user account is part of a multisite network with restricted permissions"
                ]
            elif "Connection" in error_msg or "timeout" in error_msg:
                error_code = "CONNECTION_ERROR"
                detailed_message = "Cannot connect to the store"
                troubleshooting_steps = [
                    "✓ Verify the store URL is correct and accessible",
                    "✓ Check if the website is online and responding",
                    "✓ Try accessing the URL in your browser",
                    "✓ Check for firewall or network restrictions"
                ]
            elif "SSL" in error_msg or "certificate" in error_msg:
                error_code = "SSL_ERROR"
                detailed_message = "SSL certificate issue"
                troubleshooting_steps = [
                    "✓ Check if the SSL certificate is valid and not expired",
                    "✓ Try using 'http://' instead of 'https://' temporarily",
                    "✓ Contact your hosting provider about SSL configuration",
                    "✓ Check if SSL is properly configured for the domain"
                ]
            
            return {
                'success': False,
                'error': error_msg,
                'message': detailed_message,
                'error_code': error_code,
                'troubleshooting_steps': troubleshooting_steps,
                'endpoint_tested': f"{self.store_url}{endpoint}"
            }
    
    def get_store_info(self):
        """Get basic store information."""
        try:
            # Try to get site info
            site_info = self._make_request('GET', '/wp-json/')
            
            # Try to get WooCommerce system status
            wc_status = None
            try:
                wc_status = self._make_request('GET', f"{WOOCOMMERCE_API_BASE}/system_status")
            except:
                pass  # WooCommerce might not be active or API might not be accessible
            
            return {
                'success': True,
                'site_info': site_info,
                'woocommerce_status': wc_status,
                'store_name': site_info.get('name', 'Unknown Store'),
                'store_url': self.store_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to get store information"
            }

    def get_orders_with_auth(self, limit=10):
        """Get orders using Application Password authentication."""
        try:
            # Use the built-in _make_request method which uses self.session with auth
            endpoint = f"{WOOCOMMERCE_API_BASE}/orders"
            params = {'per_page': limit}
            
            orders_data = self._make_request('GET', endpoint, params=params)
            
            return {
                'success': True,
                'orders': orders_data if isinstance(orders_data, list) else [],
                'count': len(orders_data) if isinstance(orders_data, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to retrieve orders with auth"
            }
    
    def get_products_with_auth(self, limit=10):
        """Get products using Application Password authentication."""
        try:
            # Use the built-in _make_request method which uses self.session with auth
            endpoint = f"{WOOCOMMERCE_API_BASE}/products"
            params = {'per_page': limit}
            
            products_data = self._make_request('GET', endpoint, params=params)
            
            return {
                'success': True,
                'products': products_data if isinstance(products_data, list) else [],
                'count': len(products_data) if isinstance(products_data, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to retrieve products with auth"
            }

    def test_api_endpoint(self, endpoint_type, search_params=None):
        """Test different WooCommerce API endpoints with search parameters."""
        try:
            # Define endpoint mappings
            endpoints = {
                'orders': f"{WOOCOMMERCE_API_BASE}/orders",
                'products': f"{WOOCOMMERCE_API_BASE}/products", 
                'customers': f"{WOOCOMMERCE_API_BASE}/customers",
                'settings': f"{WOOCOMMERCE_API_BASE}/settings"
            }
            
            if endpoint_type not in endpoints:
                return {
                    'success': False,
                    'error': f"Unknown endpoint type: {endpoint_type}",
                    'message': "Invalid endpoint specified"
                }
            
            endpoint = endpoints[endpoint_type]
            params = search_params or {}
            
            # Handle specific ID requests by modifying the endpoint URL
            if 'id' in params:
                resource_id = params.pop('id')  # Remove 'id' from params
                endpoint = f"{endpoint}/{resource_id}"
                # Don't set default pagination for specific resource requests
            else:
                # Set default pagination if not specified
                if 'per_page' not in params:
                    params['per_page'] = 10
            
            # Make the API request
            response_data = self._make_request('GET', endpoint, params=params)
            
            return {
                'success': True,
                'endpoint': endpoint,
                'endpoint_type': endpoint_type,
                'search_params': params,
                'data': response_data,
                'count': len(response_data) if isinstance(response_data, list) else 1,
                'message': f"Successfully retrieved {endpoint_type} data"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': endpoints.get(endpoint_type, 'unknown'),
                'endpoint_type': endpoint_type,
                'search_params': search_params or {},
                'message': f"Failed to retrieve {endpoint_type} data"
            } 