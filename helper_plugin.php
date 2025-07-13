<?php
/**
 * Plugin Name: Saski AI WooCommerce Integration Helper
 * Description: Provides API endpoints for automatic WooCommerce API key generation
 * Version: 1.0.0
 * Author: Saski AI
 * License: MIT
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Main plugin class
 */
class SaskiWooCommerceHelper {
    
    private $version = '1.0.0';
    private $plugin_name = 'saski-woocommerce-helper';
    
    public function __construct() {
        add_action('init', [$this, 'init']);
        add_action('rest_api_init', [$this, 'register_api_routes']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_scripts']);
        
        // Add admin menu
        add_action('admin_menu', [$this, 'add_admin_menu']);
        
        // Add plugin action links
        add_filter('plugin_action_links_' . plugin_basename(__FILE__), [$this, 'add_plugin_action_links']);
    }
    
    /**
     * Initialize the plugin
     */
    public function init() {
        // Check if WooCommerce is active
        if (!class_exists('WooCommerce')) {
            add_action('admin_notices', [$this, 'woocommerce_missing_notice']);
            return;
        }
        
        // Load text domain
        load_plugin_textdomain($this->plugin_name, false, dirname(plugin_basename(__FILE__)) . '/languages/');
    }
    
    /**
     * Register REST API routes
     */
    public function register_api_routes() {
        // Register the API key generation endpoint
        register_rest_route('saski/v1', '/generate-keys', [
            'methods' => 'POST',
            'callback' => [$this, 'generate_api_keys'],
            'permission_callback' => [$this, 'check_permissions'],
            'args' => [
                'description' => [
                    'required' => false,
                    'type' => 'string',
                    'default' => 'Saski AI Integration - ' . date('Y-m-d H:i:s'),
                    'sanitize_callback' => 'sanitize_text_field'
                ],
                'permissions' => [
                    'required' => false,
                    'type' => 'string',
                    'default' => 'read_write',
                    'enum' => ['read', 'write', 'read_write']
                ]
            ]
        ]);
        
        // Register the key validation endpoint
        register_rest_route('saski/v1', '/validate-keys', [
            'methods' => 'POST',
            'callback' => [$this, 'validate_api_keys'],
            'permission_callback' => [$this, 'check_permissions'],
            'args' => [
                'consumer_key' => [
                    'required' => true,
                    'type' => 'string',
                    'sanitize_callback' => 'sanitize_text_field'
                ],
                'consumer_secret' => [
                    'required' => true,
                    'type' => 'string',
                    'sanitize_callback' => 'sanitize_text_field'
                ]
            ]
        ]);
        
        // Register the store info endpoint
        register_rest_route('saski/v1', '/store-info', [
            'methods' => 'GET',
            'callback' => [$this, 'get_store_info'],
            'permission_callback' => [$this, 'check_permissions']
        ]);
        
        // Register the key management endpoint
        register_rest_route('saski/v1', '/manage-keys', [
            'methods' => 'DELETE',
            'callback' => [$this, 'revoke_api_keys'],
            'permission_callback' => [$this, 'check_permissions'],
            'args' => [
                'key_id' => [
                    'required' => true,
                    'type' => 'integer',
                    'sanitize_callback' => 'absint'
                ]
            ]
        ]);
    }
    
    /**
     * Check if user has permissions to access endpoints
     */
    public function check_permissions($request) {
        // Check if user is logged in
        if (!is_user_logged_in()) {
            return new WP_Error('rest_forbidden', 'You must be logged in to access this endpoint.', ['status' => 401]);
        }
        
        // Check if user can manage WooCommerce
        if (!current_user_can('manage_woocommerce')) {
            return new WP_Error('rest_forbidden', 'You do not have permission to manage WooCommerce settings.', ['status' => 403]);
        }
        
        return true;
    }
    
    /**
     * Generate WooCommerce API keys
     */
    public function generate_api_keys($request) {
        try {
            $user_id = get_current_user_id();
            $description = $request->get_param('description');
            $permissions = $request->get_param('permissions');
            
            // Validate permissions
            if (!in_array($permissions, ['read', 'write', 'read_write'])) {
                return new WP_Error('invalid_permissions', 'Invalid permissions specified.', ['status' => 400]);
            }
            
            // Generate the API key
            $key_data = WC()->api_keys->generate_key($user_id, $description, $permissions);
            
            if (is_wp_error($key_data)) {
                return new WP_Error('generation_failed', 'Failed to generate API keys: ' . $key_data->get_error_message(), ['status' => 500]);
            }
            
            // Log the action
            $this->log_action('generate_keys', 'success', "API keys generated for user ID: $user_id");
            
            return [
                'success' => true,
                'consumer_key' => $key_data['consumer_key'],
                'consumer_secret' => $key_data['consumer_secret'],
                'key_id' => $key_data['key_id'],
                'permissions' => $permissions,
                'description' => $description,
                'user_id' => $user_id,
                'created_at' => current_time('mysql')
            ];
            
        } catch (Exception $e) {
            $this->log_action('generate_keys', 'error', 'Exception: ' . $e->getMessage());
            return new WP_Error('generation_error', 'An error occurred while generating API keys.', ['status' => 500]);
        }
    }
    
    /**
     * Validate API keys
     */
    public function validate_api_keys($request) {
        try {
            $consumer_key = $request->get_param('consumer_key');
            $consumer_secret = $request->get_param('consumer_secret');
            
            // Get the API key from database
            global $wpdb;
            $key_data = $wpdb->get_row($wpdb->prepare(
                "SELECT * FROM {$wpdb->prefix}woocommerce_api_keys WHERE consumer_key = %s",
                wc_api_hash($consumer_key)
            ));
            
            if (!$key_data) {
                return new WP_Error('invalid_key', 'Invalid consumer key.', ['status' => 401]);
            }
            
            // Validate the consumer secret
            if (!hash_equals($key_data->consumer_secret, $consumer_secret)) {
                return new WP_Error('invalid_secret', 'Invalid consumer secret.', ['status' => 401]);
            }
            
            // Check if key is active
            if ('approved' !== $key_data->permissions) {
                return new WP_Error('key_not_approved', 'API key is not approved.', ['status' => 401]);
            }
            
            return [
                'success' => true,
                'key_id' => $key_data->key_id,
                'permissions' => $key_data->permissions,
                'description' => $key_data->description,
                'user_id' => $key_data->user_id,
                'last_access' => $key_data->last_access
            ];
            
        } catch (Exception $e) {
            $this->log_action('validate_keys', 'error', 'Exception: ' . $e->getMessage());
            return new WP_Error('validation_error', 'An error occurred while validating API keys.', ['status' => 500]);
        }
    }
    
    /**
     * Get store information
     */
    public function get_store_info($request) {
        try {
            $store_info = [
                'success' => true,
                'store_name' => get_bloginfo('name'),
                'store_url' => home_url(),
                'store_description' => get_bloginfo('description'),
                'woocommerce_version' => WC()->version,
                'wordpress_version' => get_bloginfo('version'),
                'currency' => get_woocommerce_currency(),
                'currency_symbol' => get_woocommerce_currency_symbol(),
                'api_version' => 'v3',
                'timezone' => wp_timezone_string(),
                'date_format' => get_option('date_format'),
                'time_format' => get_option('time_format')
            ];
            
            // Add WooCommerce status
            if (class_exists('WC_REST_System_Status_Controller')) {
                $status_controller = new WC_REST_System_Status_Controller();
                $system_status = $status_controller->get_item(null);
                $store_info['system_status'] = $system_status->get_data();
            }
            
            return $store_info;
            
        } catch (Exception $e) {
            $this->log_action('get_store_info', 'error', 'Exception: ' . $e->getMessage());
            return new WP_Error('info_error', 'An error occurred while getting store information.', ['status' => 500]);
        }
    }
    
    /**
     * Revoke API keys
     */
    public function revoke_api_keys($request) {
        try {
            $key_id = $request->get_param('key_id');
            
            // Get the API key
            global $wpdb;
            $key_data = $wpdb->get_row($wpdb->prepare(
                "SELECT * FROM {$wpdb->prefix}woocommerce_api_keys WHERE key_id = %d",
                $key_id
            ));
            
            if (!$key_data) {
                return new WP_Error('key_not_found', 'API key not found.', ['status' => 404]);
            }
            
            // Check if current user can revoke this key
            if ($key_data->user_id != get_current_user_id() && !current_user_can('manage_options')) {
                return new WP_Error('insufficient_permissions', 'You can only revoke your own API keys.', ['status' => 403]);
            }
            
            // Delete the key
            $deleted = $wpdb->delete(
                $wpdb->prefix . 'woocommerce_api_keys',
                ['key_id' => $key_id],
                ['%d']
            );
            
            if ($deleted === false) {
                return new WP_Error('deletion_failed', 'Failed to delete API key.', ['status' => 500]);
            }
            
            $this->log_action('revoke_keys', 'success', "API key revoked: $key_id");
            
            return [
                'success' => true,
                'message' => 'API key revoked successfully.',
                'key_id' => $key_id
            ];
            
        } catch (Exception $e) {
            $this->log_action('revoke_keys', 'error', 'Exception: ' . $e->getMessage());
            return new WP_Error('revocation_error', 'An error occurred while revoking API keys.', ['status' => 500]);
        }
    }
    
    /**
     * Log actions
     */
    private function log_action($action, $status, $message) {
        $log_entry = [
            'timestamp' => current_time('mysql'),
            'action' => $action,
            'status' => $status,
            'message' => $message,
            'user_id' => get_current_user_id(),
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
        ];
        
        // You can extend this to write to a custom log table or use WordPress logging
        error_log('Saski WooCommerce Helper: ' . json_encode($log_entry));
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_options_page(
            'Saski WooCommerce Helper',
            'Saski Helper',
            'manage_options',
            'saski-woocommerce-helper',
            [$this, 'admin_page']
        );
    }
    
    /**
     * Admin page
     */
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>Saski WooCommerce Integration Helper</h1>
            <div class="card">
                <h2>Plugin Status</h2>
                <p><strong>Version:</strong> <?php echo esc_html($this->version); ?></p>
                <p><strong>WooCommerce:</strong> <?php echo class_exists('WooCommerce') ? 'Active' : 'Not Active'; ?></p>
                <p><strong>API Endpoints:</strong></p>
                <ul>
                    <li><code><?php echo rest_url('saski/v1/generate-keys'); ?></code> - Generate API keys</li>
                    <li><code><?php echo rest_url('saski/v1/validate-keys'); ?></code> - Validate API keys</li>
                    <li><code><?php echo rest_url('saski/v1/store-info'); ?></code> - Get store information</li>
                    <li><code><?php echo rest_url('saski/v1/manage-keys'); ?></code> - Manage API keys</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>Security Notice</h2>
                <p>This plugin provides API endpoints for generating WooCommerce API keys. Ensure that:</p>
                <ul>
                    <li>Only trusted users have admin access</li>
                    <li>HTTPS is enabled on your site</li>
                    <li>API keys are transmitted securely</li>
                    <li>Regular security audits are performed</li>
                </ul>
            </div>
        </div>
        <?php
    }
    
    /**
     * Add plugin action links
     */
    public function add_plugin_action_links($links) {
        $settings_link = '<a href="' . admin_url('options-general.php?page=saski-woocommerce-helper') . '">Settings</a>';
        array_unshift($links, $settings_link);
        return $links;
    }
    
    /**
     * WooCommerce missing notice
     */
    public function woocommerce_missing_notice() {
        ?>
        <div class="notice notice-error">
            <p><strong>Saski WooCommerce Helper</strong> requires WooCommerce to be installed and active.</p>
        </div>
        <?php
    }
    
    /**
     * Enqueue scripts
     */
    public function enqueue_scripts() {
        // Add any frontend scripts if needed
    }
}

// Initialize the plugin
new SaskiWooCommerceHelper();

/**
 * Plugin activation hook
 */
register_activation_hook(__FILE__, function() {
    // Check if WooCommerce is active
    if (!class_exists('WooCommerce')) {
        wp_die('This plugin requires WooCommerce to be installed and active.');
    }
    
    // Create any necessary database tables or options
    flush_rewrite_rules();
});

/**
 * Plugin deactivation hook
 */
register_deactivation_hook(__FILE__, function() {
    // Clean up if necessary
    flush_rewrite_rules();
});
?> 