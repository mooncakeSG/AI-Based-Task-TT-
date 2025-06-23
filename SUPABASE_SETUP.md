# 🚀 Supabase Integration Setup Guide

## Overview

This guide will help you integrate Supabase database with your IntelliAssist.AI application, replacing the in-memory storage with a persistent, scalable database solution.

## 📋 Prerequisites

- Supabase account (free tier available)
- Python 3.8+ with pip
- Node.js 16+ with npm
- Basic understanding of SQL and environment variables

## 🛠️ Step 1: Create Supabase Project

### 1.1 Sign Up for Supabase
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: `intelliassist-ai`
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your users
6. Click "Create new project"

### 1.2 Get Project Credentials
1. Go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1...` (public key)
   - **service_role key**: `eyJhbGciOiJIUzI1...` (secret key)

## 🗄️ Step 2: Set Up Database Schema

### 2.1 Run SQL Schema
1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy and paste the entire contents of `backend/database_schema.sql`
4. Click "Run" to execute the schema

### 2.2 Verify Tables Created
Go to **Table Editor** and verify these tables exist:
- `users`
- `tasks`
- `chat_history`
- `uploaded_files`
- `analytics_events`

## ⚙️ Step 3: Configure Backend

### 3.1 Set Up Environment Variables
1. Navigate to the `backend` directory
2. Copy the environment template:
   ```bash
   cp env.example .env
   ```
3. Edit `.env` file with your Supabase credentials:
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-public-key-here
   SUPABASE_SERVICE_KEY=your-service-role-secret-key-here
   
   # Other settings...
   GROQ_API_KEY=your-groq-api-key-here
   HF_API_KEY=your-huggingface-api-key-here
   ```

### 3.2 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3.3 Test Backend Connection
```bash
python main.py
```

Then test the database health check:
```bash
curl http://localhost:8000/api/v1/database/health
```

Expected response:
```json
{
  "timestamp": 1234567890.123,
  "database": {
    "status": "connected",
    "message": "Database connection healthy"
  }
}
```

## 🎨 Step 4: Configure Frontend

### 4.1 Set Up Environment Variables
1. Navigate to the `react-app` directory
2. Copy the environment template:
   ```bash
   cp env.example .env.local
   ```
3. Edit `.env.local` file:
   ```env
   # Supabase Configuration (Frontend)
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-public-key-here
   
   # API Configuration
   VITE_API_BASE_URL=http://localhost:8000
   ```

### 4.2 Install Dependencies
```bash
cd react-app
npm install
```

### 4.3 Start Frontend
```bash
npm run dev
```

## 🔐 Step 5: Set Up Authentication (Optional)

### 5.1 Enable Email Authentication
1. In Supabase dashboard, go to **Authentication** → **Settings**
2. Under **Auth Providers**, enable **Email**
3. Configure email templates if needed
4. Set up SMTP (optional, for custom emails)

### 5.2 Configure Social Providers (Optional)
- **Google**: Add OAuth credentials
- **GitHub**: Add OAuth app credentials
- **Discord**: Add bot credentials

## 🧪 Step 6: Test the Integration

### 6.1 Test Task Operations
1. Open the app at `http://localhost:5173`
2. Navigate to the **Tasks** tab
3. Try creating, updating, and deleting tasks
4. Verify data persists in Supabase **Table Editor**

### 6.2 Test Chat History
1. Send some chat messages
2. Check the `chat_history` table in Supabase
3. Verify messages are being saved

### 6.3 Test File Uploads
1. Upload a file through the interface
2. Check the `uploaded_files` table
3. Verify file metadata is saved

## 📊 Step 7: Set Up Row Level Security (RLS)

The schema includes RLS policies, but you may want to customize them:

### 7.1 Understanding Current Policies
- Users can only see their own data
- All tables have user-based isolation
- Anonymous access is restricted

### 7.2 Customize Policies (Advanced)
```sql
-- Example: Allow public read access to certain data
CREATE POLICY "Public tasks read" ON tasks
  FOR SELECT USING (status = 'public');
```

## 🚀 Step 8: Production Deployment

### 8.1 Environment Variables
Set these in your production environment:
```env
# Production Supabase
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_SERVICE_KEY=your-prod-service-key

# Security
DEBUG=false
CORS_ORIGINS=https://your-domain.com
```

### 8.2 Database Backups
1. Enable automated backups in Supabase
2. Set up monitoring and alerts
3. Test restore procedures

## 🔧 Troubleshooting

### Common Issues

#### Backend Connection Issues
```bash
# Check if Supabase credentials are correct
curl -H "apikey: YOUR_ANON_KEY" \
     -H "Authorization: Bearer YOUR_ANON_KEY" \
     "https://your-project.supabase.co/rest/v1/tasks"
```

#### Frontend Connection Issues
- Check browser console for CORS errors
- Verify environment variables are loaded
- Ensure Supabase URL doesn't have trailing slash

#### RLS Policy Issues
- Check if user is authenticated
- Verify user ID matches table records
- Test policies in Supabase SQL editor

### Debug Commands

```bash
# Backend health checks
curl http://localhost:8000/ping
curl http://localhost:8000/api/v1/database/health
curl http://localhost:8000/api/v1/tasks

# Check environment variables
python -c "from config.settings import settings; print(settings.supabase_url)"
```

## 📈 Performance Optimization

### 8.1 Database Indexes
The schema includes optimized indexes, but monitor query performance:
```sql
-- Check slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
```

### 8.2 Connection Pooling
For high-traffic applications, consider:
- Supabase connection pooling (built-in)
- Application-level connection management
- Caching frequently accessed data

## 🔒 Security Best Practices

1. **Never expose service keys** in frontend code
2. **Use RLS policies** for data isolation
3. **Regularly rotate API keys**
4. **Monitor authentication logs**
5. **Set up rate limiting**
6. **Use HTTPS in production**

## 📊 Monitoring and Analytics

### 8.1 Supabase Dashboard
- Monitor database performance
- Track API usage
- Set up alerts for errors

### 8.2 Application Metrics
The schema includes an `analytics_events` table for custom tracking:
```python
# Track user actions
await database_service.save_analytics_event({
    "user_id": user_id,
    "event_type": "task_created",
    "event_data": {"task_id": task.id}
})
```

## 🆘 Support

- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Community**: [https://github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
- **IntelliAssist.AI Issues**: Create an issue in the project repository

## ✅ Checklist

- [ ] Supabase project created
- [ ] Database schema deployed
- [ ] Backend environment configured
- [ ] Frontend environment configured
- [ ] Dependencies installed
- [ ] Database connection tested
- [ ] Task operations working
- [ ] Chat history saving
- [ ] File uploads working
- [ ] Authentication configured (optional)
- [ ] RLS policies verified
- [ ] Production deployment planned

---

🎉 **Congratulations!** Your IntelliAssist.AI application now has a robust, scalable database backend powered by Supabase! 