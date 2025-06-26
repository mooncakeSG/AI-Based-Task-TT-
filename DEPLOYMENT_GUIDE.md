# 🚀 AI-Based Task Management - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Configuration](#database-configuration)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Scaling & Performance](#scaling--performance)

## Overview

This guide provides step-by-step instructions for deploying the AI-Based Task Management application to production environments. The deployment includes both manual setup and automated cloud deployment options.

### Deployment Options:

#### 🚀 **Quick Cloud Deployment (Recommended)**
- **Backend**: Render.com with `render.yaml` configuration
- **Frontend**: Vercel with `vercel.json` configuration
- **Database**: PostgreSQL on Render (free tier)
- **Zero-config deployment**: Push to GitHub and deploy automatically

#### 🛠️ **Manual Server Deployment**
- **Frontend**: React.js application with Vite
- **Backend**: FastAPI Python application  
- **Database**: Supabase (PostgreSQL)
- **AI Services**: Groq LLaMA, Hugging Face (Whisper, BLIP)
- **File Storage**: Local/Cloud storage for uploads

## 🚀 Quick Cloud Deployment

### Files Created for Cloud Deployment:
- **`render.yaml`** - Backend deployment configuration for Render
- **`react-app/vercel.json`** - Frontend deployment configuration for Vercel

### Backend on Render (render.yaml)
```yaml
services:
  # PostgreSQL Database (Free Tier)
  - type: pserv
    name: intelliassist-database
    plan: free
    
  # FastAPI Backend Service (Free Tier)
  - type: web
    name: intelliassist-backend
    env: python
    plan: free
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /ping
```

### Frontend on Vercel (vercel.json)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    }
  ],
  "routes": [
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

### Quick Deployment Steps:

1. **Deploy Backend to Render**:
   - Connect GitHub repository to Render
   - Render auto-detects `render.yaml`
   - Set environment variables in Render dashboard:
     ```bash
     GROQ_API_KEY=your_groq_api_key
     HF_API_KEY=your_hf_api_key
     SUPABASE_URL=your_supabase_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

2. **Deploy Frontend to Vercel**:
   - Connect GitHub repository to Vercel
   - Select `react-app` as root directory
   - Set environment variables:
     ```bash
     VITE_API_BASE_URL=https://your-backend.onrender.com
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

3. **Update CORS**: Add your Vercel domain to backend CORS settings

**Total deployment time: ~10 minutes** ⚡

---

## 🛠️ Manual Server Deployment

## Prerequisites

### System Requirements
- **Server**: Linux/Ubuntu 20.04+ (recommended) or Windows Server
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 20GB+ available space
- **Network**: Stable internet connection for AI API calls

### Required Software
```bash
# For Linux/Ubuntu
sudo apt update && sudo apt upgrade -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y

# Install PM2 (for process management)
sudo npm install -g pm2

# Install Git
sudo apt install git -y
```

## Environment Setup

### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/mooncakesg/AI-Based-Task-TT-.git
cd AI-Based-Task-TT-

# Create environment files
cp backend/env.example backend/.env
```

### 2. API Keys Configuration

#### Required API Keys
1. **Groq API Key**
   - Visit: https://console.groq.com/
   - Create account and generate API key
   - Free tier: 30 requests/minute
   - Models: LLaMA 3.1 70B, LLaMA 3.1 8B

2. **Hugging Face API Key**
   - Visit: https://huggingface.co/settings/tokens
   - Create account and generate token
   - Free tier available
   - Models: Whisper (speech-to-text), BLIP (image captioning)

3. **Supabase Configuration**
   - Visit: https://supabase.com/
   - Create new project
   - Get URL, anon key, and service role key

#### Backend Environment (.env)
```bash
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Database
DATABASE_URL=your_supabase_database_url

# Security
SECRET_KEY=your_secure_secret_key_here
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads

# Production settings
ENVIRONMENT=production
DEBUG=false
```

#### Frontend Environment (.env)
```bash
# react-app/.env
VITE_API_URL=https://api.yourdomain.com
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Database Configuration

### 1. Supabase Setup
```sql
-- Run this SQL in Supabase SQL Editor

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    summary TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    user_id VARCHAR(255),
    due_date TIMESTAMP,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    message TEXT NOT NULL,
    response TEXT,
    model VARCHAR(100),
    response_time FLOAT,
    tokens_used INTEGER,
    context TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create uploaded_files table
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    content_type VARCHAR(100),
    file_id VARCHAR(255) UNIQUE,
    description TEXT,
    processing_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_file_id ON uploaded_files(file_id);

-- Enable Row Level Security (RLS)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth requirements)
CREATE POLICY "Enable read access for all users" ON tasks FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON tasks FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON tasks FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON tasks FOR DELETE USING (true);

-- Apply similar policies to other tables
CREATE POLICY "Enable all access for chat_messages" ON chat_messages FOR ALL USING (true);
CREATE POLICY "Enable all access for uploaded_files" ON uploaded_files FOR ALL USING (true);
```

## Backend Deployment

### 1. Setup Python Environment
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn uvicorn[standard]
```

### 2. Production Configuration

#### Gunicorn Configuration
```python
# backend/gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
accesslog = "/var/log/ai-task-management/access.log"
errorlog = "/var/log/ai-task-management/error.log"
loglevel = "info"
```

### 3. Process Management

#### Using Systemd (Linux)
```bash
sudo cat > /etc/systemd/system/ai-task-backend.service << 'EOF'
[Unit]
Description=AI Task Management Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/AI-Based-Task-TT-/backend
Environment=PATH=/path/to/AI-Based-Task-TT-/backend/venv/bin
EnvironmentFile=/etc/ai-task-management/backend.env
ExecStart=/path/to/AI-Based-Task-TT-/backend/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Update paths and enable service
sudo systemctl daemon-reload
sudo systemctl enable ai-task-backend
sudo systemctl start ai-task-backend
```

#### Using PM2 (Cross-platform)
```bash
# Install PM2 globally
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'ai-task-backend',
    script: 'venv/bin/python',
    args: '-m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4',
    cwd: './backend',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

### 4. File Upload Directory
```bash
# Create uploads directory with proper permissions
sudo mkdir -p /var/www/ai-task-uploads
sudo chown www-data:www-data /var/www/ai-task-uploads
sudo chmod 755 /var/www/ai-task-uploads

# Update .env file
echo "UPLOAD_DIR=/var/www/ai-task-uploads" >> backend/.env
```

## Frontend Deployment

### 1. Build React Application
```bash
cd react-app

# Install dependencies
npm install

# Build for production
npm run build

# The build files will be in the 'dist' directory
```

### 2. Static File Serving

#### Using Nginx
```bash
# Move build files to web server directory
sudo mkdir -p /var/www/ai-task-frontend
sudo cp -r dist/* /var/www/ai-task-frontend/
sudo chown -R www-data:www-data /var/www/ai-task-frontend

# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/ai-task-management << 'EOF'
# Frontend configuration
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/ai-task-frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;

    # Handle React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets with long-term caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # File upload support
        client_max_body_size 50M;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-task-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Using Apache (Alternative)
```apache
# /etc/apache2/sites-available/ai-task-management.conf
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    DocumentRoot /var/www/ai-task-frontend
    
    # Handle React Router
    <Directory /var/www/ai-task-frontend>
        Options -Indexes
        AllowOverride All
        Require all granted
        
        # Fallback to index.html for SPA
        FallbackResource /index.html
    </Directory>
    
    # Proxy API requests to backend
    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:8000/api/
    ProxyPassReverse /api/ http://127.0.0.1:8000/api/
    
    # Enable compression
    LoadModule deflate_module modules/mod_deflate.so
    <Location />
        SetOutputFilter DEFLATE
    </Location>
</VirtualHost>
```

### 3. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (add to crontab)
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Production Considerations

### 1. Security Hardening

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### File Permissions
```bash
# Secure file permissions
sudo find /var/www -type f -exec chmod 644 {} \;
sudo find /var/www -type d -exec chmod 755 {} \;
sudo chmod 600 backend/.env
```

#### Environment Variables Security
```bash
# Move environment file to secure location
sudo mkdir -p /etc/ai-task-management
sudo cp backend/.env /etc/ai-task-management/backend.env
sudo chmod 600 /etc/ai-task-management/backend.env
sudo chown root:root /etc/ai-task-management/backend.env
```

### 2. Monitoring & Logging

#### Log Configuration
```bash
# Create log directories
sudo mkdir -p /var/log/ai-task-management
sudo chown www-data:www-data /var/log/ai-task-management

# Configure log rotation
sudo cat > /etc/logrotate.d/ai-task-management << 'EOF'
/var/log/ai-task-management/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ai-task-backend || pm2 reload ai-task-backend
    endscript
}
EOF
```

#### Health Check Script
```bash
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash

# Configuration
BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost/"
LOG_FILE="/var/log/ai-task-management/health-check.log"
EMAIL_ALERT="admin@yourdomain.com"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL)
if [ $BACKEND_STATUS != "200" ]; then
    log_message "Backend health check failed: HTTP $BACKEND_STATUS"
    systemctl restart ai-task-backend
    # Send email alert (requires mail setup)
    # echo "Backend service restarted due to health check failure" | mail -s "AI Task Backend Alert" $EMAIL_ALERT
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ $FRONTEND_STATUS != "200" ]; then
    log_message "Frontend health check failed: HTTP $FRONTEND_STATUS"
    systemctl reload nginx
fi

# Check disk space
DISK_USAGE=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//g')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "High disk usage: ${DISK_USAGE}%"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 80 ]; then
    log_message "High memory usage: ${MEMORY_USAGE}%"
fi
EOF

chmod +x /opt/health-check.sh

# Add to crontab for every 5 minutes
echo "*/5 * * * * /opt/health-check.sh" | crontab -
```

### 3. Backup Strategy

#### Database Backup
```bash
# Create backup script
cat > /opt/backup-database.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

# Backup Supabase database (adjust connection string)
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Database backup completed: backup_$DATE.sql.gz"
EOF

chmod +x /opt/backup-database.sh

# Schedule daily backups at 2 AM
echo "0 2 * * * /opt/backup-database.sh" | crontab -
```

#### File Backup
```bash
# Create file backup script
cat > /opt/backup-files.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIRS="/var/www/ai-task-uploads /etc/ai-task-management"

mkdir -p $BACKUP_DIR

# Create tar archive
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz $SOURCE_DIRS

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +30 -delete

echo "File backup completed: files_backup_$DATE.tar.gz"
EOF

chmod +x /opt/backup-files.sh

# Schedule weekly backups on Sunday at 3 AM
echo "0 3 * * 0 /opt/backup-files.sh" | crontab -
```

## Monitoring & Maintenance

### 1. Performance Monitoring

#### System Metrics
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor system resources
htop                    # CPU and memory
iotop                   # Disk I/O
nethogs                 # Network usage
```

#### Application Metrics
```bash
# Monitor backend performance
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics"

# Monitor with PM2 (if using PM2)
pm2 monit
pm2 logs ai-task-backend --lines 100
```

### 2. Database Maintenance

#### Regular Maintenance Tasks
```sql
-- Run these queries regularly in Supabase

-- Analyze table statistics
ANALYZE tasks;
ANALYZE chat_messages;
ANALYZE uploaded_files;

-- Check for slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Monitor database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. AI API Monitoring

#### API Usage Tracking
```python
# Add to backend monitoring
import time
import logging
from collections import defaultdict

class APIUsageTracker:
    def __init__(self):
        self.usage_stats = defaultdict(lambda: {
            'calls': 0,
            'total_time': 0,
            'errors': 0,
            'last_call': None
        })
    
    def track_call(self, api_name, response_time, success=True):
        stats = self.usage_stats[api_name]
        stats['calls'] += 1
        stats['total_time'] += response_time
        stats['last_call'] = time.time()
        if not success:
            stats['errors'] += 1
    
    def get_stats(self):
        return dict(self.usage_stats)
```

## Troubleshooting

### Common Issues

#### 1. Backend Service Issues
```bash
# Check service status
sudo systemctl status ai-task-backend

# View recent logs
sudo journalctl -u ai-task-backend -n 50 -f

# Check Python environment
cd backend && source venv/bin/activate && python -c "import main; print('Backend imports OK')"

# Test API endpoints
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/docs"
```

#### 2. Database Connection Issues
```bash
# Test database connection
python3 -c "
import os
import psycopg2
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
print('Database connection successful')
conn.close()
"

# Check Supabase status
curl -X GET "https://your-project.supabase.co/rest/v1/" \
  -H "apikey: your-anon-key"
```

#### 3. AI API Issues
```bash
# Test Groq API
curl -X GET "https://api.groq.com/openai/v1/models" \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY"

# Test Hugging Face API
curl -X POST "https://api-inference.huggingface.co/models/openai/whisper-large-v3" \
  -H "Authorization: Bearer YOUR_HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test"}'
```

#### 4. File Upload Issues
```bash
# Check upload directory
ls -la /var/www/ai-task-uploads
df -h /var/www/ai-task-uploads

# Check nginx configuration
sudo nginx -t
grep client_max_body_size /etc/nginx/sites-enabled/ai-task-management

# Test file upload
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test-file.txt" \
  -H "Content-Type: multipart/form-data"
```

### Log Analysis

#### Important Log Locations
- **Backend Logs**: `/var/log/ai-task-management/`
- **Nginx Logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **System Logs**: `sudo journalctl -u ai-task-backend`
- **PM2 Logs**: `pm2 logs ai-task-backend`

#### Log Analysis Commands
```bash
# Monitor real-time logs
tail -f /var/log/ai-task-management/error.log

# Search for errors
grep -i error /var/log/ai-task-management/*.log

# Analyze response times
awk '$9 >= 400 {print $0}' /var/log/nginx/access.log

# Count status codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c
```

## Scaling & Performance

### 1. Horizontal Scaling

#### Load Balancer Configuration
```nginx
# /etc/nginx/conf.d/upstream.conf
upstream backend_servers {
    least_conn;
    server 127.0.0.1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 weight=1 max_fails=3 fail_timeout=30s;
}

# Update main nginx config
location /api/ {
    proxy_pass http://backend_servers;
    # ... other proxy settings
}
```

#### Multiple Backend Instances
```bash
# Start multiple backend instances
pm2 start ecosystem.config.js --env production
pm2 scale ai-task-backend 4  # Scale to 4 instances
```

### 2. Database Optimization

#### Connection Pooling
```python
# backend/config/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

#### Query Optimization
```sql
-- Add composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX CONCURRENTLY idx_tasks_priority_created ON tasks(priority, created_at);

-- Partition large tables if needed
CREATE TABLE tasks_2024 PARTITION OF tasks
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 3. Caching Strategy

#### Redis Setup
```bash
# Install Redis
sudo apt install redis-server -y

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test Redis
redis-cli ping
```

#### Application Caching
```python
# backend/services/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 4. CDN Integration

#### Static Asset CDN
```bash
# Configure CDN for static assets
# Update frontend build to use CDN URLs
VITE_CDN_URL=https://cdn.yourdomain.com npm run build

# Upload static assets to CDN
aws s3 sync dist/assets/ s3://your-cdn-bucket/assets/
```

## Deployment Checklist

### Pre-Deployment
- [ ] API keys obtained and configured
- [ ] Database schema created and tested
- [ ] Environment variables set securely
- [ ] SSL certificates obtained
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring tools installed
- [ ] Load testing completed

### Post-Deployment
- [ ] Health checks passing
- [ ] All endpoints responding correctly
- [ ] File uploads working
- [ ] AI integrations functional
- [ ] Database queries optimized
- [ ] Logs configured and rotating
- [ ] Monitoring dashboards set up
- [ ] Backup procedures tested
- [ ] Documentation updated
- [ ] Team trained on operations

### Security Checklist
- [ ] API keys secured and rotated
- [ ] Database access restricted
- [ ] File upload validation enabled
- [ ] Rate limiting configured
- [ ] Security headers implemented
- [ ] HTTPS enforced
- [ ] Regular security updates scheduled
- [ ] Vulnerability scanning enabled

## Maintenance Schedule

### Daily Tasks
- [ ] Review error logs
- [ ] Check system resources
- [ ] Verify backup completion
- [ ] Monitor API usage

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Update dependencies
- [ ] Clean up old files
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Security updates
- [ ] Database maintenance
- [ ] Performance optimization
- [ ] Capacity planning review

### Quarterly Tasks
- [ ] Full security audit
- [ ] Disaster recovery testing
- [ ] Performance benchmarking
- [ ] Documentation updates

---

## 📞 Support

For deployment support or issues:

- **Documentation**: Check README.md and API documentation
- **Logs**: Review application and system logs first
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Join our Discord/Slack for real-time help

### Emergency Contacts
- **System Administrator**: admin@yourdomain.com
- **Development Team**: dev-team@yourdomain.com
- **On-Call Support**: +1-XXX-XXX-XXXX

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Deployment Environment**: Production 