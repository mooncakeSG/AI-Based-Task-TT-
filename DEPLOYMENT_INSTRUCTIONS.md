# Deployment Instructions for IntelliAssist.AI

This guide will help you deploy the IntelliAssist.AI application with the backend on Render and frontend on Vercel.

## 🚀 Backend Deployment on Render

### Prerequisites
- Render account (free tier available)
- GitHub repository with your code
- Required API keys (Groq, Hugging Face, Supabase)

### Step 1: Deploy using render.yaml

1. **Connect Repository**: Link your GitHub repository to Render
2. **Auto-deploy**: Render will automatically detect the `render.yaml` file
3. **Environment Variables**: Set the following environment variables in Render dashboard:

```bash
# Required API Keys (Set these in Render dashboard)
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here

# Supabase Settings (if using Supabase)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# CORS Origins (Update after frontend deployment)
CORS_ORIGINS=https://your-app.vercel.app,https://intelliassist-ai.vercel.app
```

### Step 2: Database Setup
The `render.yaml` includes PostgreSQL database setup. The `DATABASE_URL` will be automatically set by Render.

### Step 3: Verify Deployment
- Check health endpoint: `https://your-backend.onrender.com/ping`
- View API docs: `https://your-backend.onrender.com/docs` (disabled in production)

## 🌐 Frontend Deployment on Vercel

### Prerequisites
- Vercel account (free tier available)
- GitHub repository with your code

### Step 1: Deploy to Vercel

1. **Import Project**: Connect your GitHub repository to Vercel
2. **Configure Build**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### Step 2: Environment Variables
Set these in Vercel dashboard:

```bash
# Backend API URL (after Render deployment)
VITE_API_BASE_URL=https://your-backend.onrender.com

# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Step 3: Update CORS Settings
After frontend deployment, update the `CORS_ORIGINS` environment variable in Render with your Vercel domain.

## 🔧 Configuration Files Created

### render.yaml
- PostgreSQL database with free tier
- FastAPI backend service
- Environment variables configuration
- Health check endpoint
- File upload disk storage

### vercel.json
- Static build configuration
- SPA routing setup
- Security headers
- Asset caching
- Environment variables

## 📋 Post-Deployment Checklist

### Backend (Render)
- [ ] Service is running and healthy
- [ ] Database connection successful
- [ ] API endpoints responding
- [ ] File uploads working
- [ ] CORS properly configured

### Frontend (Vercel)
- [ ] Build completed successfully
- [ ] SPA routing working
- [ ] API calls connecting to backend
- [ ] Authentication flow working
- [ ] File uploads functional

## 🔑 Required API Keys

### Groq API
1. Visit [Groq Console](https://console.groq.com/)
2. Create account and generate API key
3. Add to Render environment variables

### Hugging Face
1. Visit [Hugging Face](https://huggingface.co/settings/tokens)
2. Create access token
3. Add to Render environment variables

### Supabase (if using)
1. Create project at [Supabase](https://supabase.com/)
2. Get URL and anon key from project settings
3. Add to both Render and Vercel

## 🚨 Security Notes

- Never commit API keys to repository
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Configure proper CORS origins
- Regular security updates

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**: Update CORS_ORIGINS in backend
2. **Build Failures**: Check Node.js version and dependencies
3. **API Connection**: Verify VITE_API_BASE_URL
4. **Database Issues**: Check DATABASE_URL and connection

### Logs Access
- **Render**: View logs in Render dashboard
- **Vercel**: View function logs in Vercel dashboard

## 📞 Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test API endpoints manually
4. Check CORS configuration

Your application will be available at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com` 