# ReStitch Store Troubleshooting Guide

## Issue: "View and Add to Cart not working"

### Quick Fixes:

1. **Check if Flask app is running:**
   ```bash
   python restitch.py
   # or
   flask run
   ```

2. **Verify database has products:**
   ```bash
   python test_store.py
   ```

3. **Seed database if empty:**
   ```bash
   python seed.py
   ```

4. **Check browser console for JavaScript errors:**
   - Open browser Developer Tools (F12)
   - Go to Console tab
   - Look for any red error messages

### Common Issues:

#### 1. User not logged in
- **Problem:** Add to Cart button shows "Login to Buy"
- **Solution:** Login with test credentials:
  - Email: `priya@example.com`
  - Password: `password123`

#### 2. Products out of stock
- **Problem:** Button shows "Out of Stock"
- **Solution:** Run `python seed.py` to reset stock levels

#### 3. JavaScript errors
- **Problem:** Buttons don't respond to clicks
- **Solution:** Check browser console for errors, refresh page

#### 4. Flask routes not registered
- **Problem:** 404 errors when clicking buttons
- **Solution:** Restart Flask application

### Debug Steps:

1. **Test URLs manually:**
   - Store: `http://localhost:5000/store/`
   - Product: `http://localhost:5000/store/upcycled-denim-jacket`
   - Add to cart: `http://localhost:5000/store/add-to-cart/1`

2. **Check Flask logs:**
   - Look for "Store index route accessed" messages
   - Look for "Add to cart route accessed" messages

3. **Verify user authentication:**
   - Check if user is logged in
   - Verify session is active

### Team Credentials:

**Admin Access:**
- Email: `admin@restitch.com`
- Password: `admin123`

**Designer Access:**
- Email: `designer@restitch.com` 
- Password: `designer123`

**Test User:**
- Email: `priya@example.com`
- Password: `password123`

### Contact Information:

**CEO & Founder:** Saloni Gupta  
**Operation Head:** Ayushi Gupta  
**Design Head:** Urvashi Chaudhary  
**Marketing Head:** Natasha  
**Sales Head:** Smriti Dawra  

### Quick Test Commands:

```bash
# Test if app starts
python run_test.py

# Check database
python test_store.py

# Reset everything
python seed.py
python restitch.py
```

### Browser Testing:

1. Open `http://localhost:5000/store/`
2. Check browser console (F12 → Console)
3. Look for debug messages:
   - "Store links found: X"
   - "Add to cart buttons found: X"
4. Click View button - should navigate to product page
5. Login and click Add to Cart - should add item and redirect

If issues persist, check Flask application logs and browser console for specific error messages.