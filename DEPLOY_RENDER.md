# Render Deployment Guide

This guide will help you deploy the IntelliAssist.AI application to Render.

## Prerequisites

1. GitHub account with your code repository
2. Render account (https://render.com)
3. Environment variables ready (Supabase keys, AI API keys)

## Deployment Steps

### Step 1: Prepare Environment Variables

In Render, you'll need to create environment variable groups:

#### Supabase Group
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon/public key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key

#### AI Keys Group
- `HUGGINGFACE_API_KEY`: Your Hugging Face API key
- `OPENAI_API_KEY`: Your OpenAI API key (if using)
- `GROQ_API_KEY`: Your Groq API key

### Step 2: Deploy Using Blueprint

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Configure environment variable groups when prompted
6. Deploy

### Step 3: Manual Deployment (Alternative)

If blueprint deployment doesn't work, deploy services manually:

#### Backend Service
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: `intelliassist-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python main.py`
   - **Health Check Path**: `/health`
4. Add environment variables
5. Deploy

#### Frontend Service
1. Click "New +" → "Static Site"
2. Connect GitHub repository
3. Configure:
   - **Name**: `intelliassist-frontend`
   - **Build Command**: `cd react-app && npm install && npm run build`
   - **Publish Directory**: `react-app/dist`
4. Add environment variables:
   - `VITE_API_BASE_URL`: `https://intelliassist-backend.onrender.com`
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
5. Deploy

### Step 4: Update Frontend Configuration

After backend deployment, update the frontend environment variable:
- Set `VITE_API_BASE_URL` to your actual backend URL

### Expected URLs

- Backend: `https://intelliassist-backend.onrender.com`
- Frontend: `https://intelliassist-frontend.onrender.com`

### Troubleshooting

#### Common Issues

1. **Build Failures**: Check build logs for missing dependencies
2. **CORS Errors**: Ensure frontend URL is added to CORS origins
3. **Database Connection**: Verify Supabase credentials
4. **API Rate Limits**: Check AI service quotas

#### Health Checks

- Backend health: `https://intelliassist-backend.onrender.com/health`
- API status: `https://intelliassist-backend.onrender.com/api/v1/status`

### Environment Variables Reference

#### Backend
- `PORT`: Auto-set by Render (10000)
- `ENVIRONMENT`: `production`
- `ALLOWED_ORIGINS`: Auto-configured for Render domains

#### Frontend
- `VITE_API_BASE_URL`: Backend service URL
- `VITE_SUPABASE_URL`: Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Supabase public key

## Support

If you encounter issues:
1. Check Render service logs
2. Review this deployment guide
3. Verify all environment variables are set correctly
4. Test endpoints individually 