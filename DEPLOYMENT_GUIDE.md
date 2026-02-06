# 🚀 Production Deployment Guide

## Quick Setup (SQLite for Testing)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Migrate Your Data
```powershell
python migrate_to_db.py
```

### 3. Test with SQLite Database
```powershell
# Start backend with database
python main_with_db.py

# Or with uvicorn
python -m uvicorn main_with_db:app --host 0.0.0.0 --port 8000
```

Your data is now in `chatapp.db` (SQLite file) instead of JSON files!

---

## 🌐 Production Deployment Options

### Option 1: Heroku (Recommended - FREE Tier Available)

#### Setup Steps:

1. **Create Heroku Account**
   - Go to https://heroku.com
   - Sign up for free account

2. **Install Heroku CLI**
   ```powershell
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   # Or use: winget install Heroku.HerokuCLI
   ```

3. **Login and Create App**
   ```powershell
   heroku login
   heroku create your-chat-app-name
   ```

4. **Add PostgreSQL Database**
   ```powershell
   heroku addons:create heroku-postgresql:mini
   ```

5. **Create Required Files**

   **Procfile** (create in project root):
   ```
   web: uvicorn main_with_db:app --host 0.0.0.0 --port $PORT
   ```

   **runtime.txt** (create in project root):
   ```
   python-3.11.7
   ```

6. **Deploy**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a your-chat-app-name
   git push heroku main
   ```

7. **Run Database Migration**
   ```powershell
   heroku run python migrate_to_db.py
   ```

8. **Get Your API URL**
   ```powershell
   heroku info
   # Your API URL: https://your-chat-app-name.herokuapp.com
   ```

---

### Option 2: Railway.app (Very Easy)

1. **Create Account**: https://railway.app
2. **Click "New Project" → "Deploy from GitHub repo"**
3. **Add PostgreSQL**: Click "+ New" → "Database" → "PostgreSQL"
4. **Environment Variables** (automatically set by Railway)
5. **Deploy automatically on git push**

**Your API URL**: `https://your-app.railway.app`

---

### Option 3: Render.com (Free SSL + Free Tier)

1. **Create Account**: https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn main_with_db:app --host 0.0.0.0 --port 10000`
5. **Add PostgreSQL Database** from dashboard
6. **Copy DATABASE_URL** to environment variables

**Your API URL**: `https://your-app.onrender.com`

---

### Option 4: AWS/DigitalOcean (Advanced)

#### DigitalOcean App Platform (Easiest):
1. Create account at https://digitalocean.com
2. Click "Create" → "Apps"
3. Connect GitHub repo
4. Add Managed PostgreSQL database
5. Set environment variables
6. Deploy!

**Cost**: ~$5-12/month

---

## 📱 Update Android App for Production

Once your backend is deployed, update your app:

### 1. Update API URL in MainActivity.kt

**Before (localhost):**
```kotlin
webView.loadUrl("http://10.0.2.2:8080/chat.html")

// In fetch interception:
url = url.replace('localhost:8000', '10.0.2.2:8000');
```

**After (production):**
```kotlin
// Host your frontend too, or serve it from backend
webView.loadUrl("https://your-app.herokuapp.com/chat")

// In fetch interception (if chat.html still uses localhost):
url = url.replace('localhost:8000', 'your-app.herokuapp.com');
```

### 2. Or Better - Serve Frontend from Backend

Add to `main_with_db.py`:
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Serve static files
@app.get("/chat")
async def serve_chat():
    with open("chat.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
```

Then in MainActivity.kt:
```kotlin
webView.loadUrl("https://your-app.herokuapp.com/chat")
// No fetch interception needed!
```

### 3. Rebuild APK
```powershell
cd android_app
gradle assembleRelease
```

---

## 🔐 Production Security Checklist

### Before Going Live:

1. **Remove Plain Passwords**
   In `database.py` and `main_with_db.py`:
   ```python
   # Remove this line:
   plain_password = Column(String(255), nullable=True)
   
   # And in endpoints, don't return plain passwords
   ```

2. **Use Environment Variables**
   Create `.env` file:
   ```env
   DATABASE_URL=postgresql://user:pass@host/dbname
   SECRET_KEY=your-secret-key-here
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Update CORS**
   In `main_with_db.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[os.getenv("ALLOWED_ORIGINS", "*").split(",")],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Enable HTTPS**
   - All hosting platforms provide free SSL
   - Update app URLs to `https://`

5. **Add Rate Limiting**
   ```powershell
   pip install slowapi
   ```
   
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/login")
   @limiter.limit("5/minute")
   def login(...):
       ...
   ```

---

## 📊 Database Management

### Backup Database (PostgreSQL)
```powershell
# Heroku
heroku pg:backups:capture
heroku pg:backups:download

# Manual
pg_dump -U username dbname > backup.sql
```

### View Database
```powershell
# Heroku
heroku pg:psql

# Local
psql -U username -d chatapp
```

### Common SQL Queries
```sql
-- View all users
SELECT * FROM users;

-- Count messages
SELECT COUNT(*) FROM messages;

-- Recent messages
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;

-- Online users
SELECT username FROM users 
JOIN online_users ON users.id = online_users.user_id;
```

---

## 📈 Monitoring & Analytics

### Add Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/login")
def login(...):
    logger.info(f"Login attempt: {user.username}")
    ...
```

### Track Errors

Most platforms (Heroku, Railway, Render) have built-in:
- Error tracking
- Performance monitoring
- Database metrics
- Traffic analytics

---

## 🎯 Testing Your Deployed App

### 1. Test Backend API
```powershell
# Test health endpoint
curl https://your-app.herokuapp.com/

# Test login
curl -X POST https://your-app.herokuapp.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 2. Test in Browser
```
https://your-app.herokuapp.com/docs
```
This opens FastAPI's interactive API documentation!

### 3. Test Mobile App
- Install APK on your phone
- Make sure phone has internet connection
- App should connect to your deployed backend

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (if needed) |
|----------|-----------|------------------|
| **Heroku** | ✅ Yes (with student pack) | $7/month mini PostgreSQL |
| **Railway** | ✅ $5 free credit/month | $5/month per service |
| **Render** | ✅ Yes (750 hrs/month) | $7/month if exceeded |
| **DigitalOcean** | ❌ No | $5-12/month |

**Recommendation for Students**: Heroku or Railway

---

## 🆘 Troubleshooting

### Database Connection Error
```python
# Check DATABASE_URL
import os
print(os.getenv("DATABASE_URL"))

# Test connection
from database import engine
engine.connect()
```

### App Won't Start
```powershell
# Check logs
heroku logs --tail

# Or
railway logs
```

### Migration Failed
```powershell
# Drop all tables and recreate
python
>>> from database import Base, engine
>>> Base.metadata.drop_all(engine)
>>> Base.metadata.create_all(engine)
```

---

## 📞 Next Steps After Deployment

1. ✅ Deploy backend to Heroku/Railway
2. ✅ Update Android app with production URL
3. ✅ Test thoroughly
4. ✅ Enable HTTPS
5. ✅ Remove plain password storage
6. ✅ Add rate limiting
7. ✅ Setup database backups
8. ✅ Monitor errors and performance
9. ✅ (Optional) Get custom domain
10. ✅ (Optional) Publish to Google Play Store

---

## 🎉 You're Ready for Production!

Your chat app is now database-ready and can scale to thousands of users!

**Summary:**
- ✅ SQLite for local testing
- ✅ PostgreSQL for production
- ✅ Easy deployment to cloud platforms
- ✅ All data migrated from JSON
- ✅ Secure and scalable architecture
