#!/bin/bash

echo "🚂 Deploying Full-Stack AI Task App to Railway (No Credit Card Required!)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Railway Setup (100% Free)${NC}"
echo "✅ No credit card required"
echo "✅ $5 monthly credits included"
echo "✅ Full-stack support"
echo "✅ PostgreSQL database included"
echo ""

echo -e "${BLUE}🔧 Setup Steps:${NC}"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub (no payment info needed)"
echo "3. Connect your repository"
echo "4. Railway auto-detects Python + Node.js"
echo ""

echo -e "${GREEN}🎯 Railway Configuration:${NC}"
echo ""
echo -e "${BLUE}Backend Configuration:${NC}"
echo "- Build Command: pip install -r requirements-render.txt"
echo "- Start Command: gunicorn main:app --host=0.0.0.0 --port=\$PORT"
echo "- Root Directory: /backend"
echo ""

echo -e "${BLUE}Frontend Configuration:${NC}"
echo "- Build Command: npm run build"
echo "- Start Command: npm run preview"
echo "- Root Directory: /react-app"
echo ""

echo -e "${BLUE}Environment Variables to Set:${NC}"
echo "GROQ_API_KEY=your_groq_key"
echo "SUPABASE_URL=your_supabase_url"
echo "SUPABASE_KEY=your_supabase_key"
echo "PORT=8000"
echo ""

echo -e "${GREEN}✨ Advantages over Heroku:${NC}"
echo "✅ No credit card required"
echo "✅ Better free tier limits"
echo "✅ Automatic HTTPS"
echo "✅ Environment variable management"
echo "✅ Real-time logs"
echo "✅ Database included"

echo ""
echo -e "${YELLOW}🚀 Quick Deploy:${NC}"
echo "1. Push your code to GitHub"
echo "2. Connect Railway to your GitHub repo"
echo "3. Railway automatically deploys both frontend and backend"
echo "4. Set environment variables in Railway dashboard" 