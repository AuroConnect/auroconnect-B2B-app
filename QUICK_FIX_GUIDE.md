# 🚀 AuroMart Quick Fix Guide

## 🚨 **IMMEDIATE FIX FOR LOADING ISSUE**

The app is stuck on loading because of authentication state issues. Here's how to fix it:

### **Step 1: Clear Browser Data**
1. Open your browser
2. Press `F12` to open Developer Tools
3. Right-click the refresh button and select "Empty Cache and Hard Reload"
4. Or manually clear localStorage:
   ```javascript
   localStorage.clear()
   ```

### **Step 2: Start Backend First**
```bash
# Terminal 1 - Start Backend
cd server
python run.py
```

**Wait until you see:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### **Step 3: Start Frontend**
```bash
# Terminal 2 - Start Frontend
cd client
npm run dev
```

**Wait until you see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### **Step 4: Test the Application**
1. Open `http://localhost:5173/` in your browser
2. You should see the landing page (not loading screen)
3. Click "Sign In" → Should go to login page
4. Click "Sign Up" → Should go to register page

## 🔧 **Alternative: Use the Startup Script**

I've created a startup script that handles everything automatically:

```bash
# Run this from the project root
python start_dev.py
```

This will:
- Start the backend server
- Wait for it to be ready
- Start the frontend server
- Show you the URLs to access

## 🧪 **Test Backend Health**

If you're unsure if the backend is working:

```bash
python check_backend_status.py
```

This will test:
- ✅ Backend connectivity
- ✅ API endpoints
- ✅ CORS configuration

## 🎯 **Demo Accounts**

Use these accounts to test the application:

| Role | Email | Password |
|------|-------|----------|
| Manufacturer | `hrushikesh@auromart.com` | `password123` |
| Manufacturer | `manufacturer1@test.com` | `password123` |
| Distributor | `distributor1@test.com` | `password123` |
| Retailer | `retailer1@test.com` | `password123` |

## 🚨 **Common Issues & Solutions**

### **Issue 1: Stuck on Loading Screen**
**Solution:** Clear browser cache and localStorage
```javascript
// In browser console
localStorage.clear()
location.reload()
```

### **Issue 2: Backend Not Starting**
**Solution:** Check if port 5000 is free
```bash
# Windows
netstat -ano | findstr :5000

# Mac/Linux
lsof -i :5000
```

### **Issue 3: Frontend Not Starting**
**Solution:** Check if port 5173 is free
```bash
# Windows
netstat -ano | findstr :5173

# Mac/Linux
lsof -i :5173
```

### **Issue 4: Database Connection Error**
**Solution:** Check database configuration
```bash
cd server
python -c "from app import db; print('Database OK')"
```

## 📱 **Expected Behavior**

After fixing:

1. **Landing Page** (`/`) - Shows AuroMart landing page
2. **Sign In** (`/login`) - Shows login form
3. **Sign Up** (`/register`) - Shows registration form
4. **Dashboard** (`/`) - Shows dashboard after login

## 🔍 **Debugging Steps**

If still having issues:

1. **Check Backend Logs:**
   ```bash
   cd server
   python run.py
   ```

2. **Check Frontend Console:**
   - Press F12 in browser
   - Look for errors in Console tab

3. **Test API Directly:**
   ```bash
   curl http://localhost:5000/api/health
   ```

4. **Check Network Tab:**
   - Press F12 in browser
   - Go to Network tab
   - Look for failed requests

## ✅ **Success Indicators**

You'll know it's working when:

- ✅ Landing page loads immediately (no loading screen)
- ✅ Sign In button navigates to `/login`
- ✅ Sign Up button navigates to `/register`
- ✅ Login form works with demo accounts
- ✅ Registration form works
- ✅ After login, redirects to dashboard

## 🆘 **Still Having Issues?**

If the problem persists:

1. **Restart Everything:**
   ```bash
   # Stop all processes (Ctrl+C)
   # Clear browser cache
   # Restart backend and frontend
   ```

2. **Check Environment:**
   ```bash
   # Backend
   cd server
   python -c "import flask; print('Flask OK')"
   
   # Frontend
   cd client
   npm list
   ```

3. **Reset Database:**
   ```bash
   cd server
   python reset_db.py
   ```

---

**🎉 The application should now work perfectly!**

**Frontend:** http://localhost:5173
**Backend:** http://localhost:5000
**Demo Account:** hrushikesh@auromart.com / password123
