import os
from cryptography.fernet import Fernet

# Database configuration
DATABASE_NAME = "woocommerce_credentials.db"

# Encryption key for storing sensitive data
def get_or_create_encryption_key():
    """Get encryption key from environment or create/load from file."""
    # First try environment variable (production)
    env_key = os.getenv('ENCRYPTION_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    
    # Otherwise, use/create a key file (development)
    key_file = "encryption.key"
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # Generate new key and save it
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_or_create_encryption_key()

# API endpoints
WORDPRESS_API_BASE = "/wp-json/wp/v2"
WOOCOMMERCE_API_BASE = "/wp-json/wc/v3"

# Request timeout
REQUEST_TIMEOUT = 30

# Default authentication settings
DEFAULT_PERMISSIONS = "read_write"
DEFAULT_DESCRIPTION = "Application Password Authentication" 