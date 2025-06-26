#!/bin/bash

echo "🚀 Deploying Full-Stack AI Task App to Heroku"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Prerequisites Check${NC}"
echo "Make sure you have:"
echo "1. Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli"
echo "2. Heroku account created"
echo "3. Git repository ready"
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Heroku CLI found${NC}"

# Login to Heroku (if not already logged in)
echo -e "${BLUE}🔐 Checking Heroku login status...${NC}"
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️ Not logged in to Heroku. Logging in...${NC}"
    heroku login
fi

echo -e "${GREEN}✅ Logged in to Heroku${NC}"

# Create Backend App
echo -e "${BLUE}🔧 Creating Backend App (FastAPI)${NC}"
BACKEND_APP_NAME="ai-task-backend-$(date +%s)"
echo "Creating app: $BACKEND_APP_NAME"

# Create Heroku app for backend
heroku create $BACKEND_APP_NAME --region us

# Set backend app for current directory
heroku git:remote -a $BACKEND_APP_NAME

# Add environment variables for backend
echo -e "${BLUE}⚙️ Setting up environment variables${NC}"
echo "You'll need to set these in Heroku dashboard:"
echo "- SUPABASE_URL"
echo "- SUPABASE_KEY" 
echo "- GROQ_API_KEY"
echo "- DATABASE_URL (Heroku Postgres will auto-set this)"

# Add Heroku Postgres
echo -e "${BLUE}🗄️ Adding PostgreSQL database${NC}"
heroku addons:create heroku-postgresql:essential-0 -a $BACKEND_APP_NAME

# Deploy backend
echo -e "${BLUE}🚀 Deploying Backend...${NC}"
git subtree push --prefix=backend heroku main

echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
echo "Backend URL: https://$BACKEND_APP_NAME.herokuapp.com"

# Create Frontend App
echo -e "${BLUE}🔧 Creating Frontend App (React)${NC}"
FRONTEND_APP_NAME="ai-task-frontend-$(date +%s)"
echo "Creating app: $FRONTEND_APP_NAME"

# Create separate Heroku app for frontend
heroku create $FRONTEND_APP_NAME --region us

# Build and deploy frontend
echo -e "${BLUE}🚀 Deploying Frontend...${NC}"

# Create a temporary directory for frontend deployment
mkdir -p temp-frontend
cp -r react-app/* temp-frontend/
cd temp-frontend

# Initialize git for frontend
git init
git add .
git commit -m "Initial frontend commit"

# Add Heroku remote for frontend
heroku git:remote -a $FRONTEND_APP_NAME

# Set environment variable for API URL
heroku config:set VITE_API_URL=https://$BACKEND_APP_NAME.herokuapp.com -a $FRONTEND_APP_NAME

# Deploy frontend
git push heroku main

cd ..
rm -rf temp-frontend

echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
echo "Frontend URL: https://$FRONTEND_APP_NAME.herokuapp.com"

echo -e "${GREEN}🎉 Full-Stack Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📱 Your Applications:${NC}"
echo "Backend API: https://$BACKEND_APP_NAME.herokuapp.com"
echo "Frontend App: https://$FRONTEND_APP_NAME.herokuapp.com" 
echo ""
echo -e "${YELLOW}⚙️ Next Steps:${NC}"
echo "1. Set environment variables in Heroku dashboard"
echo "2. Update frontend to use backend URL"
echo "3. Test the full application"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "heroku logs --tail -a $BACKEND_APP_NAME   # View backend logs"
echo "heroku logs --tail -a $FRONTEND_APP_NAME  # View frontend logs"
echo "heroku open -a $FRONTEND_APP_NAME         # Open frontend in browser" 