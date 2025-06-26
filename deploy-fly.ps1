# Fly.io deployment script for IntelliAssist backend (PowerShell)

Write-Host "🚀 Deploying IntelliAssist backend to Fly.io..." -ForegroundColor Green

# Navigate to backend directory
Set-Location backend

# Check if flyctl is installed
try {
    flyctl version | Out-Null
    Write-Host "✅ flyctl found" -ForegroundColor Green
} catch {
    Write-Host "❌ flyctl is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   Download from: https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    flyctl auth whoami | Out-Null
    Write-Host "✅ Logged in to Fly.io" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please log in to Fly.io:" -ForegroundColor Yellow
    flyctl auth login
}

# Deploy
Write-Host "📦 Deploying application..." -ForegroundColor Blue
flyctl deploy

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app should be available at: https://intelliassist-backend.fly.dev" -ForegroundColor Cyan
Write-Host "🔍 Check status: flyctl status" -ForegroundColor Yellow
Write-Host "📋 View logs: flyctl logs" -ForegroundColor Yellow 