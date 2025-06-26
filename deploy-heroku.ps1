# PowerShell script for deploying Full-Stack AI Task App to Heroku

Write-Host "🚀 Deploying Full-Stack AI Task App to Heroku" -ForegroundColor Cyan

Write-Host "📋 Prerequisites Check" -ForegroundColor Blue
Write-Host "Make sure you have:"
Write-Host "1. Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli"
Write-Host "2. Heroku account created"
Write-Host "3. Git repository ready"
Write-Host ""

# Check if Heroku CLI is installed
if (-not (Get-Command heroku -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Heroku CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli"
    exit 1
}

Write-Host "✅ Heroku CLI found" -ForegroundColor Green

# Check login status
Write-Host "🔐 Checking Heroku login status..." -ForegroundColor Blue
try {
    $loginCheck = heroku auth:whoami 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Not logged in to Heroku. Please run: heroku login" -ForegroundColor Yellow
        Write-Host "After logging in, run this script again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Logged in to Heroku as: $loginCheck" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Unable to check login status. Please run: heroku login" -ForegroundColor Yellow
    exit 1
}

# Generate unique app names
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$BACKEND_APP_NAME = "ai-task-backend-$timestamp"
$FRONTEND_APP_NAME = "ai-task-frontend-$timestamp"

Write-Host "🔧 Creating Backend App: $BACKEND_APP_NAME" -ForegroundColor Blue

# Create Heroku app for backend
heroku create $BACKEND_APP_NAME --region us
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create backend app" -ForegroundColor Red
    exit 1
}

# Add PostgreSQL database
Write-Host "🗄️ Adding PostgreSQL database..." -ForegroundColor Blue
heroku addons:create heroku-postgresql:essential-0 -a $BACKEND_APP_NAME

Write-Host "⚙️ Setting up environment variables" -ForegroundColor Blue
Write-Host "You need to set these in Heroku dashboard:" -ForegroundColor Yellow
Write-Host "- SUPABASE_URL" -ForegroundColor Yellow
Write-Host "- SUPABASE_KEY" -ForegroundColor Yellow
Write-Host "- GROQ_API_KEY" -ForegroundColor Yellow
Write-Host "- DATABASE_URL (auto-set by Postgres addon)" -ForegroundColor Yellow

Write-Host ""
Write-Host "🚀 Ready to deploy!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. cd to your project root directory"
Write-Host "2. Run: git subtree push --prefix=backend https://git.heroku.com/$BACKEND_APP_NAME.git main"
Write-Host "3. Set environment variables in Heroku dashboard"
Write-Host "4. Create frontend app: heroku create $FRONTEND_APP_NAME"
Write-Host "5. Deploy frontend: git subtree push --prefix=react-app https://git.heroku.com/$FRONTEND_APP_NAME.git main"

Write-Host ""
Write-Host "Backend URL: https://$BACKEND_APP_NAME.herokuapp.com" -ForegroundColor Green
Write-Host "Frontend URL: https://$FRONTEND_APP_NAME.herokuapp.com" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Blue
Write-Host "heroku logs --tail -a $BACKEND_APP_NAME   # View backend logs"
Write-Host "heroku logs --tail -a $FRONTEND_APP_NAME  # View frontend logs"
Write-Host "heroku open -a $FRONTEND_APP_NAME         # Open frontend in browser" 