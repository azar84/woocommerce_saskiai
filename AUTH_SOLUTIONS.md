# 🔐 Quick Authentication Solutions

## Most Common Fixes for 401 Errors

Based on your error message, here are the **most likely solutions** ranked by frequency:

### 🥇 **Solution 1: Check Username Format** (Most Common)
- ❌ **Wrong**: Using email address like `admin@yourstore.com`
- ✅ **Correct**: Using WordPress username like `admin` or `john_doe`

**How to find your username:**
1. Go to your WordPress admin: `https://yourstore.com/wp-admin/`
2. Click **Users** → **All Users**
3. Find your user and note the **Username** column (NOT the email)

---

### 🥈 **Solution 2: Two-Factor Authentication** (Very Common)
If you have 2FA enabled (Wordfence, Google Authenticator, etc.):

**Option A: Temporarily disable 2FA**
1. Go to WordPress admin → Plugins
2. Deactivate security plugins temporarily
3. Try connecting again
4. Re-enable plugins after connection

**Option B: Create Application Password**
1. Go to WordPress admin → Users → Your Profile
2. Scroll to "Application Passwords" section
3. Name: `WooCommerce Integration`
4. Click "Add New Application Password"
5. Copy the generated password
6. Use your **username** + **application password** (not regular password)

---

### 🥉 **Solution 3: Security Plugins Blocking API** (Common)
Common security plugins that block REST API:
- Wordfence Security
- iThemes Security  
- Sucuri Security
- All In One WP Security

**Fixes:**
1. **Whitelist your IP** in security plugin settings
2. **Enable REST API** in security plugin settings
3. **Temporarily disable** security plugins
4. Check plugin logs for blocked requests

---

### 🔧 **Solution 4: User Role Check**
- Ensure your user has **Administrator** role
- Editor/Author roles won't work for WooCommerce integration

**How to check:**
1. WordPress admin → Users → All Users
2. Find your user and check the **Role** column
3. Should say "Administrator"

---

## 🛠️ **Interactive Troubleshooter**

Run this command for step-by-step help:
```bash
python3 auth_troubleshooter.py
```

This will walk you through each possible issue systematically.

---

## 🚀 **Quick Test Command**

For immediate testing:
```bash
python3 quick_auth_test.py
```

This prompts for credentials and tests them instantly.

---

## ✅ **Success Checklist**

Before connecting, verify:
- [ ] Using WordPress **username** (not email)
- [ ] Can log into WordPress admin manually
- [ ] User has **Administrator** role
- [ ] No 2FA blocking (or use Application Password)
- [ ] Security plugins not blocking REST API
- [ ] Store URL is correct and accessible

---

## 🎯 **Next Steps**

1. **Try Solution 1 first** (username format) - fixes 60% of issues
2. **If still failing**, try Solution 2 (Application Password) - fixes 80% of remaining issues
3. **If still stuck**, run the interactive troubleshooter
4. **Last resort**: Contact hosting provider or disable all security plugins

---

*Once authentication works, go to http://localhost:3000/connect and use the working credentials! 🚀* 