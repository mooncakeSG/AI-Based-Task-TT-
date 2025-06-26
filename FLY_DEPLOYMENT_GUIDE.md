# 🚁 Fly.io Deployment Guide

This guide will help you deploy the AI Task Management application (both frontend and backend) to Fly.io.

## 📋 Prerequisites

1. **Fly.io Account**: Sign up at [fly.io](https://fly.io/)
2. **Fly CLI**: Install the Fly CLI tool
3. **API Keys**: Groq, Hugging Face, and Supabase credentials
4. **Docker**: Ensure Docker is installed and running

## 🛠️ Installation & Setup

### 1. Install Fly CLI

```bash
# For Linux/macOS
curl -L https://fly.io/install.sh | sh

# For Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Add to PATH if needed
export PATH="$HOME/.fly/bin:$PATH"
```

### 2. Login to Fly.io

```bash
flyctl auth login
```

### 3. Prepare Environment Variables

Create a `.env` file in the `backend` directory with your credentials:

```env
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
DATABASE_URL=your_supabase_database_url
```

## 🚀 Deployment Steps

### Option A: Automated Deployment (Recommended)

1. Make the deployment script executable:
```bash
chmod +x deploy.sh
```

2. Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Check for Fly CLI installation
- Create apps if they don't exist
- Guide you through setting secrets
- Deploy both frontend and backend
- Provide the deployed URLs

### Option B: Manual Deployment

#### Backend Deployment

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create the Fly app:
```bash
flyctl apps create ai-task-backend
```

3. Set environment secrets:
```bash
flyctl secrets set GROQ_API_KEY="your_groq_api_key_here"
flyctl secrets set HF_API_KEY="your_huggingface_api_key_here"
flyctl secrets set SUPABASE_URL="your_supabase_url"
flyctl secrets set SUPABASE_ANON_KEY="your_supabase_anon_key"
flyctl secrets set SUPABASE_SERVICE_KEY="your_supabase_service_key"
flyctl secrets set DATABASE_URL="your_supabase_database_url"
```

4. Deploy the backend:
```bash
flyctl deploy
```

5. Get the backend URL:
```bash
flyctl info
```

#### Frontend Deployment

1. Navigate to the react-app directory:
```bash
cd ../react-app
```

2. Create the frontend environment file:
```bash
cat > .env.production << EOF
VITE_API_URL=https://your-backend-url.fly.dev
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF
```

3. Create the Fly app:
```bash
flyctl apps create ai-task-frontend
```

4. Deploy the frontend:
```bash
flyctl deploy
```

## 🔧 Configuration Details

### Backend Configuration (`backend/fly.toml`)

- **Memory**: 1GB (adjustable based on needs)
- **CPU**: Shared CPU, 1 core
- **Health Check**: `/ping` endpoint
- **Auto-scaling**: Enabled with 0 minimum machines

### Frontend Configuration (`react-app/fly.toml`)

- **Memory**: 512MB
- **CPU**: Shared CPU, 1 core
- **Health Check**: Root path `/`
- **Auto-scaling**: Enabled with 0 minimum machines

## 🌐 Post-Deployment

### 1. Update CORS Settings

Update your backend's CORS origins to include your frontend URL:

```bash
cd backend
flyctl secrets set CORS_ORIGINS="https://your-frontend-url.fly.dev,http://localhost:5173"
```

### 2. Test Your Applications

- **Backend**: `https://your-backend-url.fly.dev/ping`
- **Frontend**: `https://your-frontend-url.fly.dev`
- **API Docs**: `https://your-backend-url.fly.dev/docs`

### 3. Monitor Your Apps

```bash
# View logs
flyctl logs -a ai-task-backend
flyctl logs -a ai-task-frontend

# Check status
flyctl status -a ai-task-backend
flyctl status -a ai-task-frontend

# Monitor resources
flyctl machine list -a ai-task-backend
```

## 🔄 Updates & Maintenance

### Updating Your Applications

```bash
# Backend updates
cd backend
flyctl deploy

# Frontend updates
cd react-app
flyctl deploy
```

### Scaling

```bash
# Scale backend
flyctl scale memory 2048 -a ai-task-backend
flyctl scale count 2 -a ai-task-backend

# Scale frontend
flyctl scale memory 1024 -a ai-task-frontend
```

### Managing Secrets

```bash
# List secrets
flyctl secrets list -a ai-task-backend

# Update a secret
flyctl secrets set API_KEY="new_value" -a ai-task-backend

# Remove a secret
flyctl secrets unset OLD_SECRET -a ai-task-backend
```

## 🛡️ Security Best Practices

1. **Use Secrets**: Never commit API keys to version control
2. **HTTPS Only**: Fly.io enforces HTTPS by default
3. **Environment Separation**: Use different apps for staging/production
4. **Regular Updates**: Keep dependencies updated
5. **Monitor Logs**: Set up log monitoring and alerts

## 💰 Cost Optimization

1. **Auto-scaling**: Both apps are configured to scale to zero when not in use
2. **Resource Limits**: Configured with minimal resources that can be scaled up
3. **Health Checks**: Ensure apps don't restart unnecessarily
4. **Monitoring**: Use Fly.io metrics to optimize resource usage

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Dockerfile syntax
   - Ensure all dependencies are listed
   - Verify base image compatibility

2. **App Won't Start**:
   - Check health check endpoint
   - Verify port configuration
   - Review application logs

3. **Environment Variables**:
   - Ensure all required secrets are set
   - Check secret names match code
   - Verify Supabase credentials

### Debug Commands

```bash
# Check app logs
flyctl logs -a ai-task-backend

# SSH into app
flyctl ssh console -a ai-task-backend

# Check app configuration
flyctl config show -a ai-task-backend

# Monitor app health
flyctl checks list -a ai-task-backend
```

## 📞 Support

- **Fly.io Documentation**: [fly.io/docs](https://fly.io/docs)
- **Community Forum**: [community.fly.io](https://community.fly.io)
- **Status Page**: [status.fly.io](https://status.fly.io)

## 📝 Notes

- Both applications will be accessible via HTTPS automatically
- Auto-scaling is enabled to save costs when not in use
- Health checks ensure your apps stay running
- Logs are available through the Fly CLI and dashboard
- Consider setting up monitoring and alerting for production use

---

🎉 **Congratulations!** Your AI Task Management application is now deployed on Fly.io! 