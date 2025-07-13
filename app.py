#!/usr/bin/env python3
"""
WooCommerce Integration Web App
===============================

Flask web application providing a beautiful interface for
WooCommerce API key generation and management.

Usage:
    python app.py

Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, flash, url_for
import os
import json
from datetime import datetime
from database import DatabaseManager
from woocommerce_client import WooCommerceClient

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database
db = DatabaseManager()

@app.route('/')
def index():
    """Home page showing dashboard."""
    stores = db.list_stores()
    recent_logs = db.get_logs(limit=5)
    
    stats = {
        'total_stores': len(stores),
        'active_stores': len([s for s in stores if s['status'] == 'active']),
        'recent_connections': len([log for log in recent_logs if log['action'] == 'store_credentials'])
    }
    
    return render_template('index.html', stores=stores, logs=recent_logs, stats=stats)

@app.route('/connect')
def connect_page():
    """Connect new store page."""
    return render_template('connect.html')

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """API endpoint to test connection without storing credentials."""
    try:
        data = request.get_json()
        store_url = data.get('store_url', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not store_url or not username or not password:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Normalize store URL
        if not store_url.startswith(('http://', 'https://')):
            store_url = 'https://' + store_url
        store_url = store_url.rstrip('/')
        
        # Initialize client
        client = WooCommerceClient(store_url, username, password)
        
        # Test WordPress authentication
        auth_result = client.test_wordpress_connection()
        if not auth_result['success']:
            return jsonify({
                'success': False,
                'message': auth_result['message'],
                'error': auth_result.get('error', 'Unknown error'),
                'debug_info': {
                    'store_url': store_url,
                    'username': username,
                    'endpoint_tested': auth_result.get('endpoint_tested', 'Unknown')
                }
            }), 401
        
        # Get store information
        store_info = client.get_store_info()
        
        return jsonify({
            'success': True,
            'message': 'Connection test successful',
            'store_name': store_info.get('store_name', 'Unknown Store'),
            'user_name': auth_result.get('user_data', {}).get('name', 'Unknown User')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Connection test failed: {str(e)}"
        }), 500

@app.route('/api/debug-connection', methods=['POST'])
def debug_connection():
    """Debug endpoint to help troubleshoot connection issues."""
    try:
        data = request.get_json()
        store_url = data.get('store_url', '').strip()
        
        # Validate input
        if not store_url:
            return jsonify({
                'success': False,
                'message': 'Store URL is required'
            }), 400
        
        # Normalize store URL
        if not store_url.startswith(('http://', 'https://')):
            store_url = 'https://' + store_url
        store_url = store_url.rstrip('/')
        
        debug_info = {
            'store_url': store_url,
            'endpoints_to_test': [
                f"{store_url}/wp-json/",
                f"{store_url}/wp-json/wp/v2/users/me",
                f"{store_url}/wp-json/wc/v3/system_status"
            ]
        }
        
        # Test basic connectivity
        try:
            import requests
            response = requests.get(f"{store_url}/wp-json/", timeout=10)
            debug_info['basic_connectivity'] = {
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'response_headers': dict(response.headers)
            }
        except Exception as e:
            debug_info['basic_connectivity'] = {
                'error': str(e),
                'accessible': False
            }
        
        return jsonify({
            'success': True,
            'message': 'Debug information collected',
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Debug failed: {str(e)}"
        }), 500

@app.route('/api/connect', methods=['POST'])
def connect_store():
    """API endpoint to connect a new store."""
    try:
        data = request.get_json()
        store_url = data.get('store_url', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not store_url or not username or not password:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Normalize store URL
        if not store_url.startswith(('http://', 'https://')):
            store_url = 'https://' + store_url
        store_url = store_url.rstrip('/')
        
        # Initialize client
        client = WooCommerceClient(store_url, username, password)
        
        # Step 1: Test WordPress authentication
        auth_result = client.test_wordpress_connection()
        if not auth_result['success']:
            # Log the authentication failure for debugging
            db.log_action(None, "authentication_failed", "error", 
                         f"Authentication failed for {store_url}: {auth_result['message']}")
            
            return jsonify({
                'success': False,
                'message': f"Authentication failed: {auth_result['message']}",
                'error': auth_result.get('error', 'Unknown error'),
                'error_code': auth_result.get('error_code', 'UNKNOWN_ERROR'),
                'troubleshooting_steps': auth_result.get('troubleshooting_steps', []),
                'debug_info': {
                    'store_url': store_url,
                    'username': username,
                    'auth_endpoint': f"{store_url}/wp-json/wp/v2/users/me"
                }
            }), 401
        
        # Step 2: Get store information
        store_info = client.get_store_info()
        if not store_info['success']:
            return jsonify({
                'success': False,
                'message': f"Failed to get store info: {store_info['message']}"
            }), 400
        
        store_name = store_info.get('store_name', 'Unknown Store')
        
        # Step 3: Test WooCommerce API access
        orders_test = client.get_orders_with_auth(limit=1)
        products_test = client.get_products_with_auth(limit=1)
        
        # Step 4: Store credentials
        store_id = db.store_credentials(
            store_url=store_url,
            store_name=store_name,
            admin_username=username,
            admin_password=password,
            permissions='read_write',
            description='Application Password Authentication'
        )
        
        return jsonify({
            'success': True,
            'message': f"Store '{store_name}' connected successfully using Application Password!",
            'store_id': store_id,
            'store_name': store_name,
            'authentication_method': 'application_password',
            'woocommerce_access': {
                'orders_accessible': orders_test.get('success', False),
                'products_accessible': products_test.get('success', False)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        }), 500

@app.route('/stores')
def stores_page():
    """Stores management page."""
    stores = db.list_stores()
    return render_template('stores.html', stores=stores)

@app.route('/api/stores')
def get_stores():
    """API endpoint to get all stores."""
    stores = db.list_stores()
    return jsonify({'stores': stores})

@app.route('/api/stores/<int:store_id>/test', methods=['POST'])
def test_store(store_id):
    """API endpoint to test a store connection."""
    try:
        # Get store by finding it in the list (since we don't have direct ID lookup)
        stores = db.list_stores()
        store = None
        for s in stores:
            if s['id'] == store_id:
                store = s
                break
        
        if not store:
            return jsonify({
                'success': False,
                'message': 'Store not found'
            }), 404
        
        # Get credentials
        credentials = db.get_credentials(store['store_url'])
        if not credentials:
            return jsonify({
                'success': False,
                'message': 'Could not retrieve credentials'
            }), 500
        
        # Use Application Password authentication
        client = WooCommerceClient(
            store['store_url'], 
            credentials['admin_username'], 
            credentials['admin_password']
        )
        
        # Test WordPress authentication first
        auth_result = client.test_wordpress_connection()
        if not auth_result['success']:
            return jsonify({
                'success': False,
                'message': f"Authentication failed: {auth_result['message']}",
                'error': auth_result.get('error', 'Unknown error')
            })
        
        # Test WooCommerce API access
        store_info = client.get_store_info()
        if not store_info['success']:
            return jsonify({
                'success': False,
                'message': f"WooCommerce access failed: {store_info['message']}"
            })
        
        # Try to get some sample data using Application Password
        orders_result = client.get_orders_with_auth(limit=5)
        products_result = client.get_products_with_auth(limit=5)
        
        return jsonify({
            'success': True,
            'message': 'Connection test successful (Application Password)',
            'authentication_method': 'application_password',
            'orders_accessible': orders_result.get('success', False),
            'orders_count': orders_result.get('count', 0),
            'products_accessible': products_result.get('success', False),
            'products_count': products_result.get('count', 0)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Test failed: {str(e)}"
        }), 500

@app.route('/api/stores/<int:store_id>/credentials', methods=['GET'])
def get_store_credentials(store_id):
    """API endpoint to get store credentials."""
    try:
        # Get store by finding it in the list (since we don't have direct ID lookup)
        stores = db.list_stores()
        store = None
        for s in stores:
            if s['id'] == store_id:
                store = s
                break
        
        if not store:
            return jsonify({
                'success': False,
                'message': 'Store not found'
            }), 404
        
        # Get credentials
        credentials = db.get_credentials(store['store_url'])
        if not credentials:
            return jsonify({
                'success': False,
                'message': 'Could not retrieve credentials'
            }), 500
        
        return jsonify({
            'success': True,
            'credentials': credentials
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Failed to retrieve credentials: {str(e)}"
        }), 500

@app.route('/api/stores/disconnect', methods=['POST'])
def disconnect_store():
    """API endpoint to disconnect a store."""
    try:
        data = request.get_json()
        store_url = data.get('store_url')
        
        if not store_url:
            return jsonify({
                'success': False,
                'message': 'Store URL is required'
            }), 400
        
        result = db.disconnect_store(store_url)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Store disconnected successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to disconnect store'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error disconnecting store: {str(e)}"
        }), 500

@app.route('/logs')
def logs_page():
    """Logs page."""
    logs = db.get_logs()
    return render_template('logs.html', logs=logs)

@app.route('/api-tester')
def api_tester_page():
    """API testing page."""
    stores = db.list_stores()
    return render_template('api_tester.html', stores=stores)

@app.route('/api/logs')
def get_logs():
    """API endpoint to get logs."""
    logs = db.get_logs()
    return jsonify({'logs': logs})

@app.route('/api/test-endpoint', methods=['POST'])
def test_endpoint():
    """API endpoint to test WooCommerce endpoints."""
    try:
        # Check if we have JSON data
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        store_id = data.get('store_id')
        endpoint_type = data.get('endpoint_type')
        search_params = data.get('search_params', {})
        
        # Enhanced debugging
        print(f"DEBUG: Received data: {data}")
        print(f"DEBUG: store_id: {store_id}, endpoint_type: {endpoint_type}")
        
        if not store_id or not endpoint_type:
            return jsonify({
                'success': False,
                'message': 'Store ID and endpoint type are required',
                'received_data': data
            }), 400
        
        # Get store by finding it in the list
        stores = db.list_stores()
        print(f"DEBUG: Found {len(stores)} stores in database")
        
        if not stores:
            return jsonify({
                'success': False,
                'message': 'No stores found in database. Please connect a store first.',
                'available_stores': []
            }), 404
        
        store = None
        for s in stores:
            print(f"DEBUG: Checking store {s.get('id')} == {store_id}")
            if s['id'] == store_id:
                store = s
                break
        
        if not store:
            return jsonify({
                'success': False,
                'message': f'Store with ID {store_id} not found',
                'available_stores': [{'id': s['id'], 'name': s['store_name']} for s in stores]
            }), 404
        
        # Get credentials
        credentials = db.get_credentials(store['store_url'])
        if not credentials:
            return jsonify({
                'success': False,
                'message': f'Could not retrieve credentials for store: {store["store_url"]}',
                'store_info': store
            }), 500
        
        # Create client and test endpoint
        client = WooCommerceClient(
            store['store_url'], 
            credentials['admin_username'], 
            credentials['admin_password']
        )
        
        # Test the specified endpoint
        result = client.test_api_endpoint(endpoint_type, search_params)
        
        # Log the API test
        log_message = f"API test for {endpoint_type} on {store['store_url']}: {'Success' if result['success'] else 'Failed'}"
        db.log_action(store_id, "api_test", "success" if result['success'] else "error", log_message)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Exception in test_endpoint: {error_trace}")
        return jsonify({
            'success': False,
            'message': f"API test failed: {str(e)}",
            'error_type': type(e).__name__,
            'debug_info': {
                'request_data': request.get_json() if request.is_json else 'Not JSON',
                'error_trace': error_trace
            }
        }), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get dashboard statistics."""
    stores = db.list_stores()
    logs = db.get_logs(limit=100)
    
    stats = {
        'total_stores': len(stores),
        'active_stores': len([s for s in stores if s['status'] == 'active']),
        'recent_connections': len([log for log in logs if log['action'] == 'store_credentials']),
        'total_actions': len(logs)
    }
    
    return jsonify(stats)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory('static/assets', 'favicon.svg')

@app.route('/favicon.svg')
def favicon_svg():
    """Serve SVG favicon."""
    return send_from_directory('static/assets', 'favicon.svg')

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    """Serve Apple touch icon (redirect to SVG)."""
    return redirect('/favicon.svg')

@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon_precomposed():
    """Serve Apple touch icon precomposed (redirect to SVG)."""
    return redirect('/favicon.svg')

@app.route('/sw.js')
def service_worker():
    """Return empty service worker to prevent 404."""
    return "", 200, {'Content-Type': 'application/javascript'}

@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
    
    print("🌐 Starting WooCommerce Integration Web App...")
    print("📍 Access the app at: http://localhost:3000")
    print("🔗 Available endpoints:")
    print("   - / (Dashboard)")
    print("   - /connect (Connect New Store)")
    print("   - /stores (Manage Stores)")
    print("   - /logs (View Logs)")
    
    app.run(debug=True, host='0.0.0.0', port=3000) 