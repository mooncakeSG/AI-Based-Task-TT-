# 🚀 Complete Deployment Guide for IntelliAssist.AI

## Overview
This guide covers deploying:
- **Backend**: FastAPI on Render with PostgreSQL
- **Frontend**: React/Vite on Vercel

## 📦 Files Created for Deployment

### 1. `render.yaml` - Backend Configuration
- PostgreSQL database (free tier)
- FastAPI web service
- Environment variables setup
- Health monitoring
- File storage disk

### 2. `react-app/vercel.json` - Frontend Configuration
- Vite build setup
- SPA routing
- Security headers
- Asset caching
- Environment variables

## 🔧 Backend Deployment on Render

### Step 1: Repository Setup
1. Push code to GitHub
2. Connect GitHub to Render
3. Render will auto-detect `render.yaml`

### Step 2: Environment Variables (Set in Render Dashboard)
```bash
# 🔑 Required API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here
HF_API_KEY=hf_your_huggingface_token_here

# 🗄️ Supabase (if using instead of PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 🌐 CORS (Update after frontend deployment)
CORS_ORIGINS=https://your-app.vercel.app,https://localhost:5173
```

### Step 3: Database Migration (Optional)
If you need to run database migrations:
```bash
# Add to render.yaml build command
cd backend && pip install -r requirements.txt && alembic upgrade head
```

## 🌐 Frontend Deployment on Vercel

### Step 1: Project Setup
1. Connect GitHub repository to Vercel
2. Select `react-app` directory as root
3. Vercel auto-detects Vite configuration

### Step 2: Build Configuration
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 3: Environment Variables (Set in Vercel Dashboard)
```bash
# 🔗 Backend API URL (after Render deployment)
VITE_API_BASE_URL=https://intelliassist-backend.onrender.com

# 🗄️ Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔄 Deployment Sequence

### 1. Deploy Backend First
```bash
# Render will use render.yaml
git push origin main
# Monitor deployment at render.com dashboard
```

### 2. Get Backend URL
After successful deployment, note your backend URL:
`https://intelliassist-backend.onrender.com`

### 3. Deploy Frontend
```bash
# Update VITE_API_BASE_URL in Vercel
# Push to trigger deployment
git push origin main
```

### 4. Update CORS
Add your Vercel domain to backend CORS_ORIGINS

## 📝 Configuration Details

### render.yaml Breakdown
```yaml
services:
  # Database
  - type: pserv
    name: intelliassist-database
    plan: free  # 🆓 Free PostgreSQL

  # Backend API
  - type: web
    name: intelliassist-backend
    env: python
    plan: free  # 🆓 Free web service
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /ping  # Health monitoring
```

### vercel.json Breakdown
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"  # Vite build
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"  # SPA routing
    }
  ]
}
```

## 🔐 Security Configuration

### Backend Security
- HTTPS enforced by Render
- CORS properly configured
- Environment variables secured
- Health check monitoring

### Frontend Security
- Security headers in vercel.json
- Asset caching optimized
- XSS protection enabled
- Content type validation

## 🧪 Testing Deployment

### Backend Health Check
```bash
curl https://your-backend.onrender.com/ping
# Expected: {"status": "ok", "app": "IntelliAssist.AI"}
```

### Frontend Functionality
1. Visit your Vercel URL
2. Test authentication flow
3. Try file upload
4. Check API calls in browser dev tools

## 🚨 Common Issues & Solutions

### 1. CORS Errors
```bash
# Update in Render dashboard
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

### 2. Build Failures
```bash
# Check Node.js version in package.json
"engines": {
  "node": "18.x"
}
```

### 3. API Connection Issues
```bash
# Verify in Vercel dashboard
VITE_API_BASE_URL=https://your-backend.onrender.com
```

### 4. Database Connection
```bash
# Check DATABASE_URL in Render logs
# Ensure PostgreSQL service is running
```

## 📊 Monitoring & Maintenance

### Render Monitoring
- Service health dashboard
- Real-time logs
- Performance metrics
- Automatic restarts

### Vercel Analytics
- Build performance
- Function logs
- Edge network stats
- Core Web Vitals

## 💡 Production Tips

1. **Cold Starts**: Render free tier has ~30s cold start
2. **Caching**: Vercel provides excellent edge caching
3. **Monitoring**: Set up uptime monitoring
4. **Backups**: Regular database backups
5. **Updates**: Keep dependencies updated

## 🎯 Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] Database connection successful
- [ ] Frontend loads correctly
- [ ] Authentication works
- [ ] File uploads functional
- [ ] API calls successful
- [ ] CORS configured
- [ ] Environment variables set
- [ ] Custom domains configured (optional)
- [ ] Monitoring alerts set up

Your deployed application:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **Database**: Managed PostgreSQL on Render 