#!/bin/bash

# Fly.io deployment script for IntelliAssist backend
echo "🚀 Deploying IntelliAssist backend to Fly.io..."

# Navigate to backend directory
cd backend

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please log in to Fly.io:"
    flyctl auth login
fi

# Deploy
echo "📦 Deploying application..."
flyctl deploy

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: https://intelliassist-backend.fly.dev"
echo "🔍 Check status: flyctl status"
echo "📋 View logs: flyctl logs" 