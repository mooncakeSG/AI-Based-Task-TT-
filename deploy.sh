#!/bin/bash

# AI Task Management - Fly.io Deployment Script
set -e

echo "🚀 Starting deployment to Fly.io..."

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    print_error "flyctl is not installed. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if user is logged in to fly.io
if ! flyctl auth whoami &> /dev/null; then
    print_error "Please log in to fly.io first:"
    echo "flyctl auth login"
    exit 1
fi

print_status "Deploying backend..."
cd backend

# Check if backend app exists, if not create it
if ! flyctl apps list | grep -q "ai-task-backend"; then
    print_status "Creating backend app..."
    flyctl apps create ai-task-backend
fi

# Set environment secrets for backend
print_status "Setting backend environment variables..."
if [ -f .env ]; then
    print_warning "Make sure to set these secrets in fly.io:"
    echo "flyctl secrets set GROQ_API_KEY=your_groq_api_key_here"
    echo "flyctl secrets set HF_API_KEY=your_huggingface_api_key_here"
    echo "flyctl secrets set SUPABASE_URL=your_supabase_url"
    echo "flyctl secrets set SUPABASE_ANON_KEY=your_supabase_anon_key"
    echo "flyctl secrets set SUPABASE_SERVICE_KEY=your_supabase_service_key"
    echo "flyctl secrets set DATABASE_URL=your_database_url"
    echo ""
    read -p "Have you set all the required secrets? (y/n): " confirm
    if [[ $confirm != [yY] ]]; then
        print_error "Please set the secrets first, then run this script again."
        exit 1
    fi
else
    print_warning ".env file not found. Make sure to set secrets manually."
fi

# Deploy backend
print_status "Deploying backend application..."
flyctl deploy

# Get backend URL
BACKEND_URL=$(flyctl info | grep Hostname | awk '{print $2}')
print_status "Backend deployed at: https://$BACKEND_URL"

cd ..

print_status "Deploying frontend..."
cd react-app

# Create frontend environment file
print_status "Creating frontend environment configuration..."
cat > .env.production << EOF
VITE_API_URL=https://$BACKEND_URL
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
EOF

print_warning "Please update .env.production with your actual Supabase credentials"

# Check if frontend app exists, if not create it
if ! flyctl apps list | grep -q "ai-task-frontend"; then
    print_status "Creating frontend app..."
    flyctl apps create ai-task-frontend
fi

# Deploy frontend
print_status "Deploying frontend application..."
flyctl deploy

# Get frontend URL
FRONTEND_URL=$(flyctl info | grep Hostname | awk '{print $2}')
print_status "Frontend deployed at: https://$FRONTEND_URL"

cd ..

print_status "✅ Deployment complete!"
echo ""
echo "🌐 Your applications are now live:"
echo "   Frontend: https://$FRONTEND_URL"
echo "   Backend:  https://$BACKEND_URL"
echo ""
print_warning "Next steps:"
echo "1. Update your frontend environment variables with actual Supabase credentials"
echo "2. Test both applications to ensure they're working correctly"
echo "3. Set up monitoring and logging as needed"
echo ""
print_status "To update your deployments in the future, run:"
echo "   flyctl deploy (in the respective directory)" 