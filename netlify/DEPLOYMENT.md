# Chat Application - Netlify Deployment Guide

## 📋 Deployment Overview

This folder contains the **frontend** of the chat application ready for Netlify deployment. The **backend** (Python/FastAPI) must be deployed separately.

## 🎯 Frontend Deployment (Netlify)

### Step 1: Deploy to Netlify

1. Sign up/login at [netlify.com](https://netlify.com)
2. Choose **"Deploy manually"** or connect your Git repository
3. Drag and drop the `netlify` folder contents, or:
   - Click "New site from Git"
   - Select your repository
   - Set publish directory to `netlify/`

### Step 2: Configure API URL

**IMPORTANT:** Update the backend API URL before deploying:

1. Open `index.html` in a text editor
2. Find this line (around line 1027):
   ```javascript
   const API_URL = 'http://localhost:8000';
   ```
3. Replace with your deployed backend URL:
   ```javascript
   const API_URL = 'https://your-backend-domain.com';
   // or
   const API_URL = 'https://your-ip-or-domain:8000';
   ```
4. Save and deploy

## 🖥️ Backend Deployment (Separate)

Your Python/FastAPI backend needs to be deployed separately. Here are popular options:

### Option 1: Heroku (Easiest for Python)
```bash
# Install Heroku CLI
# Create Procfile in your backend folder:
web: gunicorn -w 4 -b 0.0.0.0:$PORT main:app

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 2: AWS EC2
1. Create an EC2 instance (Ubuntu/Python)
2. Install Python, FastAPI, Uvicorn
3. Run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
4. Use IP address as API_URL

### Option 3: Google Cloud Run
```bash
gcloud run deploy chat-app --source . --platform managed
```

### Option 4: DigitalOcean
1. Create a Droplet (Ubuntu)
2. Install Python and dependencies
3. Deploy and configure nginx as reverse proxy

## 🔧 Environment Setup

### Frontend Environment Variables (in Netlify)
No environment variables needed for static deployment, but optionally add:
- `VITE_API_URL` - Backend API URL (if using with a build tool)

### Backend Environment Variables
- `CORS_ORIGINS` - Allow Netlify domain (e.g., `https://your-site.netlify.app`)
- `DATABASE_URL` - If using database instead of JSON files
- `SECRET_KEY` - For JWT tokens if needed

## 📝 Important Notes

1. **CORS Configuration**: Update your backend to allow requests from your Netlify domain:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-site.netlify.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **File Storage**: Backend stores files locally in `uploads/` folder. For production, consider:
   - AWS S3
   - Google Cloud Storage
   - DigitalOcean Spaces
   - Azure Blob Storage

3. **Database**: Currently uses JSON storage. For production, migrate to:
   - PostgreSQL
   - MongoDB
   - MySQL

4. **Security**:
   - Enable HTTPS (automatic on Netlify)
   - Use environment variables for sensitive data
   - Disable plain-text password storage in production
   - Add rate limiting on backend
   - Implement proper authentication

## 📂 File Structure

```
netlify/
├── index.html           # Main frontend file (single-page app)
├── netlify.toml        # Netlify configuration
├── _redirects          # SPA routing rules
└── DEPLOYMENT.md       # This file
```

## 🚀 Deployment Checklist

- [ ] Backend deployed and running
- [ ] API_URL updated in index.html
- [ ] CORS configured on backend
- [ ] Frontend deployed to Netlify
- [ ] Test login with admin/admin
- [ ] Test file uploads
- [ ] Test voice messages
- [ ] Test on mobile device
- [ ] Monitor logs for errors

## 📞 Troubleshooting

### "Connection error. Make sure the server is running."
- Backend API URL is incorrect
- Backend is not running
- CORS is not enabled on backend

### "Failed to send message"
- File upload disabled on backend
- File size too large (>200MB)
- Disk space full on backend server

### "Cannot access microphone"
- Browser permissions not granted
- HTTPS required for microphone access
- Only works in secure context

## 📊 Production Checklist

- [ ] Move to PostgreSQL database
- [ ] Use S3 or Cloud Storage for files
- [ ] Enable SSL/HTTPS
- [ ] Set up monitoring/logging (Sentry, LogRocket)
- [ ] Configure backups
- [ ] Set up CI/CD pipeline
- [ ] Run security audit
- [ ] Performance optimization
- [ ] Add rate limiting
- [ ] Enable spam/abuse detection
