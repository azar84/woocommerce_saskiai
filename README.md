# WooCommerce API Key Generation - Proof of Concept

## 🎯 Overview

This proof of concept demonstrates how to automatically generate WooCommerce API keys and store credentials securely without requiring users to manually create keys or install plugins. The system authenticates with WordPress, generates API keys programmatically, and stores them in an encrypted database.

## 🏗️ Architecture

### Components

1. **`main.py`** - Main application with CLI interface
2. **`database.py`** - Database management with encryption
3. **`woocommerce_client.py`** - WordPress/WooCommerce API client
4. **`config.py`** - Configuration settings
5. **`helper_plugin.php`** - WordPress plugin for actual API key generation

### Workflow

1. **User Input**: Store URL + Admin credentials
2. **Authentication**: Validate credentials with WordPress REST API
3. **API Key Generation**: Generate WooCommerce API keys (simulated in POC)
4. **Secure Storage**: Encrypt and store credentials in SQLite database
5. **Verification**: Test generated keys with WooCommerce API calls

## 🚀 Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd woocommerce-saski-integration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🎮 Usage

### CLI Interface

The application provides a simple command-line interface with the following options:

1. **Connect New Store** - Add a new WooCommerce store
2. **List Connected Stores** - View all connected stores
3. **Test Store Connection** - Verify API keys work
4. **View Connection Logs** - See connection history
5. **Disconnect Store** - Remove a store connection
6. **Exit** - Close the application

### Example Usage

```bash
$ python main.py

🚀 WooCommerce API Integration - Proof of Concept
==================================================

📋 Available Actions:
1. Connect New Store
2. List Connected Stores
3. Test Store Connection
4. View Connection Logs
5. Disconnect Store
6. Exit

📝 Select an option (1-6): 1

🔗 Connect New WooCommerce Store
-----------------------------------
📝 Store URL (e.g., https://example.com): https://mystore.com
📝 Admin Username: admin
🔑 Admin Password: [hidden]

🔍 Connecting to https://mystore.com...
1️⃣ Testing WordPress authentication...
✅ Authenticated successfully as: Admin User
2️⃣ Getting store information...
✅ Store name: My Store
3️⃣ Generating WooCommerce API keys...
✅ API keys generated successfully
ℹ️  Note: This is a simulated response. In production, you'd need a custom plugin.
4️⃣ Testing API keys...
⚠️  API key test failed: API keys test failed
   Error: HTTP 401: Unauthorized
   Proceeding to store credentials anyway...
5️⃣ Storing credentials securely...
✅ Credentials stored successfully (ID: 1)
🎉 Store 'My Store' connected successfully!
```

## 🔐 Security Features

- **Encryption**: All sensitive data encrypted using Fernet symmetric encryption
- **Secure Password Input**: Passwords hidden during input
- **HTTPS Only**: All API calls use HTTPS
- **Credential Storage**: No raw passwords stored, only encrypted API keys
- **Database Security**: SQLite database with encrypted sensitive fields

## 📊 Database Schema

### Stores Table
- `id` - Primary key
- `store_url` - Store URL (unique)
- `store_name` - Store display name
- `admin_username` - Encrypted admin username
- `consumer_key` - Encrypted WooCommerce consumer key
- `consumer_secret` - Encrypted WooCommerce consumer secret
- `key_id` - WooCommerce key ID
- `permissions` - API key permissions (read_write)
- `description` - Key description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `status` - Active/inactive status

### Connection Logs Table
- `id` - Primary key
- `store_id` - Foreign key to stores table
- `action` - Action performed
- `status` - Success/failure status
- `message` - Action message
- `timestamp` - Action timestamp

## 🔧 Production Implementation

### Real API Key Generation

For production use, you need to implement actual API key generation. This requires:

1. **WordPress Plugin**: Install `helper_plugin.php` on the target WooCommerce store
2. **Custom Endpoint**: Create a REST API endpoint that generates keys
3. **Authentication**: Secure the endpoint with proper authentication

### Example Plugin Implementation

```php
<?php
// In helper_plugin.php
add_action('rest_api_init', function () {
    register_rest_route('saski/v1', '/generate-keys', [
        'methods' => 'POST',
        'callback' => 'generate_woocommerce_keys',
        'permission_callback' => 'is_user_logged_in'
    ]);
});

function generate_woocommerce_keys($request) {
    if (!current_user_can('manage_woocommerce')) {
        return new WP_Error('forbidden', 'Insufficient permissions', ['status' => 403]);
    }
    
    $user_id = get_current_user_id();
    $description = 'Saski AI Integration - ' . date('Y-m-d H:i:s');
    $permissions = 'read_write';
    
    $key_data = WC()->api_keys->generate_key($user_id, $description, $permissions);
    
    return [
        'consumer_key' => $key_data['consumer_key'],
        'consumer_secret' => $key_data['consumer_secret'],
        'key_id' => $key_data['key_id'],
        'permissions' => $permissions,
        'description' => $description
    ];
}
?>
```

## 📝 Configuration

### Environment Variables

Set these environment variables for production:

```bash
export ENCRYPTION_KEY="your-encryption-key-here"
export DATABASE_URL="path/to/your/database.db"
```

### Config Options

Edit `config.py` to customize:

- Database name and location
- API endpoints
- Request timeouts
- Default permissions
- Encryption settings

## 🧪 Testing

### Unit Tests

Run the test suite:

```bash
python -m pytest tests/
```

### Manual Testing

1. Set up a test WooCommerce store
2. Create admin credentials
3. Run the application
4. Test all functionality

## 🚨 Important Notes

### Current Limitations

1. **API Key Generation**: Currently simulated - requires custom plugin for production
2. **Authentication**: Basic auth only - consider OAuth for production
3. **Database**: SQLite for simplicity - use PostgreSQL/MySQL for production
4. **Error Handling**: Basic error handling - enhance for production use

### Production Considerations

1. **Security Auditing**: Regular security reviews
2. **Monitoring**: Add logging and monitoring
3. **Backup**: Regular database backups
4. **Scalability**: Consider database optimization
5. **Compliance**: Ensure GDPR/privacy compliance

## 📋 API Reference

### WooCommerceClient Methods

- `test_wordpress_connection()` - Test WordPress authentication
- `get_store_info()` - Get store information
- `generate_api_keys_via_rest()` - Generate API keys
- `test_api_keys(key, secret)` - Test API key validity
- `get_orders(key, secret, limit)` - Retrieve orders
- `get_products(key, secret, limit)` - Retrieve products

### DatabaseManager Methods

- `store_credentials(...)` - Store encrypted credentials
- `get_credentials(store_url)` - Retrieve decrypted credentials
- `list_stores()` - List all connected stores
- `disconnect_store(store_url)` - Deactivate store connection
- `log_action(...)` - Log actions
- `get_logs(...)` - Retrieve logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@saski.ai
- Documentation: [docs.saski.ai](https://docs.saski.ai)
- Issues: [GitHub Issues](https://github.com/saski-ai/woocommerce-integration/issues)

---

**Note**: This is a proof of concept. For production use, implement proper API key generation, enhanced security measures, and comprehensive error handling. 