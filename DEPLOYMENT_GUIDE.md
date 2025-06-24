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

This guide provides step-by-step instructions for deploying the AI-Based Task Management application to production environments. The application consists of:

- **Frontend**: React.js application
- **Backend**: FastAPI Python application
- **Database**: Supabase (PostgreSQL)
- **AI Services**: Groq, Hugging Face APIs
- **File Storage**: Local/Cloud storage for uploads

## Prerequisites

### System Requirements
- **Server**: Linux/Ubuntu 20.04+ (recommended)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 20GB+ available space
- **Network**: Stable internet connection for AI API calls

### Required Software
```bash
# Update system
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
git clone https://github.com/your-username/AI-Based-Task-TT-.git
cd AI-Based-Task-TT-

# Create environment files
cp backend/env.example backend/.env
cp react-app/.env.example react-app/.env
```

### 2. API Keys Configuration

#### Required API Keys
1. **Groq API Key**
   - Visit: https://console.groq.com/
   - Create account and generate API key
   - Free tier: 30 requests/minute

2. **Hugging Face API Key**
   - Visit: https://huggingface.co/settings/tokens
   - Create account and generate token
   - Free tier available

3. **Supabase Configuration**
   - Visit: https://supabase.com/
   - Create new project
   - Get URL and anon key

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
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_SUPABASE_URL=your_supabase_project_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
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
```

### 2. Database Backup Strategy
```bash
# Create backup script
cat > /opt/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Backup using Supabase CLI or pg_dump
# Adjust connection string as needed
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup-db.sh

# Add to crontab for daily backups
echo "0 2 * * * /opt/backup-db.sh" | crontab -
```

## Backend Deployment

### 1. Setup Python Environment
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn uvicorn[standard]
```

### 2. Create Production Configuration
```bash
# Create gunicorn configuration
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF
```

### 3. Create Systemd Service
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
ExecStart=/path/to/AI-Based-Task-TT-/backend/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Update paths in the service file
sudo sed -i 's|/path/to/AI-Based-Task-TT-|'$(pwd)'/..|g' /etc/systemd/system/ai-task-backend.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-task-backend
sudo systemctl start ai-task-backend
```

### 4. Create Upload Directory
```bash
# Create uploads directory with proper permissions
sudo mkdir -p /var/www/ai-task-uploads
sudo chown www-data:www-data /var/www/ai-task-uploads
sudo chmod 755 /var/www/ai-task-uploads

# Update .env file
echo "UPLOAD_DIR=/var/www/ai-task-uploads" >> .env
```

## Frontend Deployment

### 1. Build React Application
```bash
cd react-app

# Install dependencies
npm install

# Build for production
npm run build

# Move build files to web server directory
sudo mkdir -p /var/www/ai-task-frontend
sudo cp -r dist/* /var/www/ai-task-frontend/
sudo chown -R www-data:www-data /var/www/ai-task-frontend
```

### 2. Configure Nginx
```bash
sudo cat > /etc/nginx/sites-available/ai-task-management << 'EOF'
# Frontend configuration
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/ai-task-frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend API configuration
server {
    listen 80;
    server_name api.yourdomain.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
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
    }

    # File upload endpoint with larger body size
    location /api/v1/upload {
        client_max_body_size 50M;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-task-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Production Considerations

### 1. Security Hardening
```bash
# Firewall configuration
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Secure file permissions
sudo find /var/www -type f -exec chmod 644 {} \;
sudo find /var/www -type d -exec chmod 755 {} \;
```

### 2. Environment Variables Security
```bash
# Restrict .env file permissions
chmod 600 backend/.env

# Use systemd environment file for production
sudo mkdir -p /etc/ai-task-management
sudo cp backend/.env /etc/ai-task-management/backend.env
sudo chmod 600 /etc/ai-task-management/backend.env
sudo chown root:root /etc/ai-task-management/backend.env

# Update systemd service to use environment file
sudo sed -i '/\[Service\]/a EnvironmentFile=/etc/ai-task-management/backend.env' /etc/systemd/system/ai-task-backend.service
```

### 3. Logging Configuration
```bash
# Create log directory
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
        systemctl reload ai-task-backend
    endscript
}
EOF
```

## Monitoring & Maintenance

### 1. Health Check Script
```bash
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $BACKEND_STATUS != "200" ]; then
    echo "Backend health check failed: $BACKEND_STATUS"
    systemctl restart ai-task-backend
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ $FRONTEND_STATUS != "200" ]; then
    echo "Frontend health check failed: $FRONTEND_STATUS"
    systemctl reload nginx
fi

# Check disk space
DISK_USAGE=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//g')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is at ${DISK_USAGE}%"
fi
EOF

chmod +x /opt/health-check.sh

# Add to crontab
echo "*/5 * * * * /opt/health-check.sh" | crontab -
```

### 2. Application Monitoring
```bash
# Install monitoring tools
npm install -g pm2

# Monitor with PM2 (alternative to systemd)
pm2 start backend/main.py --name ai-task-backend --interpreter python3
pm2 startup
pm2 save

# View logs
pm2 logs ai-task-backend
```

### 3. Performance Monitoring
```bash
# Install system monitoring
sudo apt install htop iotop -y

# Monitor API performance
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics"
```

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check service status
sudo systemctl status ai-task-backend

# Check logs
sudo journalctl -u ai-task-backend -f

# Check Python dependencies
cd backend && source venv/bin/activate && pip check
```

#### 2. Database Connection Issues
```bash
# Test database connection
python3 -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful')
"
```

#### 3. API Key Issues
```bash
# Test Groq API
curl -H "Authorization: Bearer YOUR_GROQ_KEY" https://api.groq.com/openai/v1/models

# Test Hugging Face API
curl -H "Authorization: Bearer YOUR_HF_KEY" https://api-inference.huggingface.co/models/gpt2
```

#### 4. File Upload Issues
```bash
# Check upload directory permissions
ls -la /var/www/ai-task-uploads

# Check nginx file size limits
grep client_max_body_size /etc/nginx/sites-enabled/ai-task-management
```

### Log Locations
- **Backend Logs**: `/var/log/ai-task-management/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `sudo journalctl -u ai-task-backend`

## Scaling & Performance

### 1. Horizontal Scaling
```bash
# Load balancer configuration (nginx)
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

# Update proxy_pass to use upstream
proxy_pass http://backend;
```

### 2. Database Optimization
```sql
-- Add database indexes for performance
CREATE INDEX CONCURRENTLY idx_tasks_created_at ON tasks(created_at);
CREATE INDEX CONCURRENTLY idx_tasks_priority_status ON tasks(priority, status);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'user123';
```

### 3. Caching Strategy
```bash
# Install Redis for caching
sudo apt install redis-server -y

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. CDN Integration
```bash
# Configure static asset serving through CDN
# Update frontend build to use CDN URLs
REACT_APP_CDN_URL=https://cdn.yourdomain.com npm run build
```

## Deployment Checklist

### Pre-Deployment
- [ ] API keys configured and tested
- [ ] Database schema created and migrated
- [ ] Environment variables set
- [ ] SSL certificates obtained
- [ ] Firewall configured
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Log rotation set up
- [ ] Performance baseline established
- [ ] Documentation updated
- [ ] Team trained on maintenance procedures

### Security Checklist
- [ ] API keys secured
- [ ] Database access restricted
- [ ] File upload validation enabled
- [ ] Rate limiting configured
- [ ] Security headers set
- [ ] Regular security updates scheduled

## Support & Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Review logs and performance metrics
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and test backup/restore procedures
4. **Annually**: Security audit and penetration testing

### Emergency Procedures
1. **Service Down**: Check health-check.sh output, restart services
2. **Database Issues**: Check connection, review recent migrations
3. **High CPU/Memory**: Scale horizontally or optimize queries
4. **Security Breach**: Rotate API keys, review access logs

---

## 📞 Support

For deployment support or issues:
- **Documentation**: Check README.md and API documentation
- **Logs**: Review application and system logs
- **Community**: Create GitHub issues for bugs or feature requests

---

**Last Updated**: December 2024
**Version**: 1.0.0 