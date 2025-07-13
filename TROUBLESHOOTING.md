# 🔧 WooCommerce Integration Troubleshooting Guide

## Issues Fixed ✅

Your WooCommerce integration web app is now running successfully with enhanced debugging capabilities! Here's what was fixed:

### 1. Port Conflicts
- **Issue**: Port 3000 was already in use by another process
- **Fix**: Killed conflicting processes and restarted the server cleanly
- **Status**: ✅ **RESOLVED** - Server now runs on http://localhost:3000

### 2. Missing Assets (404 Errors)
- **Issue**: Missing favicon, service worker, and Apple touch icons
- **Fix**: Added proper asset routes and created branded favicon
- **Status**: ✅ **RESOLVED** - No more 404 errors for static assets

### 3. Enhanced Debugging
- **Issue**: Limited error information for connection failures
- **Fix**: Added comprehensive debugging tools
- **Status**: ✅ **IMPROVED** - Better error messages and debugging capabilities

---

## 🚨 Solving 401 Authentication Errors

If you're still getting 401 errors when connecting stores, here's how to troubleshoot:

### Step 1: Test Basic Connectivity
1. Go to http://localhost:3000/connect
2. Enter your store URL (e.g., `https://yourstore.com`)
3. Click **"Debug URL"** button
4. Check the results:
   - ✅ **Green message**: Store is accessible, proceed to Step 2
   - ❌ **Red message**: Store connectivity issue, see [Connectivity Issues](#connectivity-issues)

### Step 2: Test Authentication
1. Fill in all fields (Store URL, Username, Password)
2. Click **"Test Connection"** button
3. Check the results:
   - ✅ **Green message**: Authentication successful, you can now connect
   - ❌ **Red message**: Authentication failed, see [Authentication Issues](#authentication-issues)

### Step 3: Full Connection
1. Once both tests pass, click **"Connect Store"**
2. Monitor the progress modal
3. Store should be successfully connected

---

## 🔍 Common Issues and Solutions

### Connectivity Issues

**❌ "Cannot access store"**
- **Cause**: Store URL is incorrect or unreachable
- **Solutions**:
  - Check URL spelling and format
  - Ensure the site is online and accessible
  - Try with and without `www.` prefix
  - Verify SSL certificate is valid

**❌ "WordPress REST API not found"**
- **Cause**: WordPress REST API is disabled or not available
- **Solutions**:
  - Ensure WordPress is properly installed
  - Check if REST API is enabled (should be by default)
  - Verify `/wp-json/` endpoint is accessible

### Authentication Issues

**❌ "Invalid username or password"**
- **Cause**: WordPress admin credentials are incorrect
- **Solutions**:
  - Double-check username (not email address)
  - Verify password is correct
  - Try logging into WordPress admin panel manually first
  - Check if two-factor authentication is enabled

**❌ "Access denied"**
- **Cause**: User doesn't have administrator privileges
- **Solutions**:
  - Ensure user has Administrator role
  - Check user permissions in WordPress admin
  - Try with a different admin user

**❌ "SSL certificate issue"**
- **Cause**: SSL configuration problems
- **Solutions**:
  - Verify SSL certificate is valid
  - Try with `http://` instead of `https://` (temporarily)
  - Check if mixed content is causing issues

---

## 🛠️ Advanced Debugging

### Using the Debug Tools

1. **Basic Debug Test**:
   ```bash
   curl -X POST http://localhost:3000/api/debug-connection \
     -H "Content-Type: application/json" \
     -d '{"store_url":"https://yourstore.com"}'
   ```

2. **Authentication Test**:
   ```bash
   curl -X POST http://localhost:3000/api/test-connection \
     -H "Content-Type: application/json" \
     -d '{"store_url":"https://yourstore.com","username":"admin","password":"password"}'
   ```

3. **Run Debug Script**:
   ```bash
   python3 test_debug.py
   ```

### Console Debugging

1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Attempt connection
4. Check for detailed error messages and debug info

---

## 📋 Pre-Connection Checklist

Before connecting a store, ensure:

- [ ] WordPress site is accessible and working
- [ ] You have administrator account credentials
- [ ] WordPress REST API is enabled (default)
- [ ] WooCommerce plugin is installed and active
- [ ] SSL certificate is valid (if using HTTPS)
- [ ] No security plugins blocking REST API access
- [ ] No firewall blocking your IP address

---

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check the logs**: Go to http://localhost:3000/logs
2. **Review error details**: Look for specific error messages
3. **Try different stores**: Test with a demo WooCommerce site first
4. **Check WordPress settings**: Ensure REST API isn't disabled

### Test with Demo Store

Try connecting to a demo store first to verify the integration works:
- Store URL: `https://demo.woothemes.com`
- This will help isolate if the issue is with your specific store

---

## 📞 Common WordPress/WooCommerce Issues

### Plugin Conflicts
- Disable security plugins temporarily
- Check if any plugins are blocking REST API access
- Try with a fresh WordPress installation

### Server Configuration
- Ensure PHP version is compatible
- Check if mod_rewrite is enabled
- Verify WordPress permalinks are working

### WooCommerce Settings
- Ensure WooCommerce is properly configured
- Check if REST API is enabled in WooCommerce settings
- Verify store is not in maintenance mode

---

## 🎯 Success Indicators

You'll know everything is working when:
- ✅ Debug URL test shows "Store is accessible"
- ✅ Test Connection shows "Connection test successful"
- ✅ Connect Store completes without errors
- ✅ Store appears in the Stores page with "Active" status

---

*Happy integrating! 🚀* 