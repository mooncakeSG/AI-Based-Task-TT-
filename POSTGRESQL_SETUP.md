# PostgreSQL Database Setup Guide

## Overview

Your IntelliAssist.AI application now supports **direct PostgreSQL connections** as the primary database method, with Supabase and in-memory storage as fallbacks. This provides better performance, reliability, and direct control over your database.

## Connection Priority

The application will try to connect in this order:

1. **PostgreSQL Direct Connection** (preferred) - Fast, reliable, full control
2. **Supabase Connection** (fallback) - Your existing setup
3. **In-Memory Storage** (development) - Temporary storage for testing

## Setup Instructions

### Step 1: Configure Your Database URL

Based on your Supabase connection string, you need to set the `DATABASE_URL` environment variable.

From your Supabase dashboard (as shown in your image), you have:
```
postgresql://postgres:[YOUR-PASSWORD]@db.kbnnbqxklvguxchrdgel.supabase.co:5432/postgres
```

#### Option A: Create/Update `.env` file

Create or update `backend/.env` with your actual password:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.kbnnbqxklvguxchrdgel.supabase.co:5432/postgres

# Keep your existing Supabase settings as fallback
SUPABASE_URL=https://kbnnbqxklvguxchrdgel.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Your existing AI settings
GROQ_API_KEY=your-groq-api-key-here
# ... other settings
```

#### Option B: Set Environment Variable Directly

Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.kbnnbqxklvguxchrdgel.supabase.co:5432/postgres"
```

Windows Command Prompt:
```cmd
set DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.kbnnbqxklvguxchrdgel.supabase.co:5432/postgres
```

### Step 2: Install Required Dependencies

The necessary packages are already installed:
- ✅ `asyncpg` - PostgreSQL async driver
- ✅ `sqlalchemy` - Database ORM
- ✅ `psycopg2-binary` - PostgreSQL adapter
- ✅ `alembic` - Database migrations

### Step 3: Test the Connection

Run the PostgreSQL connection test:

```bash
python test_postgresql_connection.py
```

**Expected Output:**
```
🚀 Starting PostgreSQL Database Test

🔗 Testing PostgreSQL Database Connection...
Database URL configured: Yes
✅ PostgreSQL connection successful!

📝 Testing task creation...
Cleared 0 existing tasks
✅ Created task: 1 - Test PostgreSQL connection
✅ Created task: 2 - Verify task storage in PostgreSQL
✅ Created task: 3 - Check task retrieval functionality

📋 Retrieving tasks...
Total tasks in database: 3
  - Task 1: Test PostgreSQL connection [pending]
  - Task 2: Verify task storage in PostgreSQL [pending]
  - Task 3: Check task retrieval functionality [pending]

Tasks for test_user: 3

🎉 PostgreSQL test completed successfully!
   - Connection type: postgresql
   - Tasks created: 3
   - Tasks retrieved: 3

✅ All tests passed!
```

### Step 4: Start the Server

The backend server is already configured to use the new PostgreSQL service:

```bash
cd backend
python main.py
```

### Step 5: Verify Database Health

Check the database health endpoint:

```bash
curl http://localhost:8000/api/v1/database/health
```

**Expected Response:**
```json
{
  "status": "connected",
  "type": "postgresql",
  "message": "PostgreSQL database connection healthy",
  "timestamp": 1750681293.356
}
```

## Database Features

### Automatic Table Creation

The service automatically creates the necessary tables:

- **`tasks`** - Stores AI-generated tasks
  - `id` (Primary Key)
  - `summary` (Task description)
  - `category` (Task category)
  - `priority` (high/medium/low)
  - `status` (pending/completed/cancelled)
  - `user_id` (Optional user identifier)
  - `created_at` & `updated_at` (Timestamps)

- **`chat_history`** - Stores conversation history
  - `id` (Primary Key)
  - `user_id` (Optional user identifier)
  - `message` & `response` (Conversation data)
  - `model`, `response_time`, `tokens_used` (AI metrics)
  - `created_at` (Timestamp)

### Fallback Behavior

If PostgreSQL connection fails, the system will:

1. **Try Supabase** - Use your existing Supabase configuration
2. **Use Memory Storage** - Temporary in-memory storage for development

## Troubleshooting

### Connection Issues

**Problem**: `Database URL configured: No`
**Solution**: Make sure `DATABASE_URL` is set in your environment or `.env` file

**Problem**: `Failed to connect to PostgreSQL: connection refused`
**Solution**: 
- Verify your password is correct
- Check if your IP is whitelisted in Supabase
- Ensure the database URL format is correct

**Problem**: `SSL required`
**Solution**: The connection string automatically handles SSL for Supabase

### Task Saving Issues

**Problem**: Tasks are extracted but not saved
**Solution**: 
1. Check database health: `GET /api/v1/database/health`
2. Verify PostgreSQL connection is active
3. Check server logs for connection errors

### Performance Issues

**Problem**: Slow database operations
**Solution**: 
- PostgreSQL direct connection should be faster than REST API calls
- Check network latency to your database
- Consider connection pooling for high-traffic scenarios

## Benefits of PostgreSQL Direct Connection

✅ **Better Performance** - Direct connection is faster than REST API calls
✅ **More Reliable** - Fewer network hops and dependencies
✅ **Full SQL Support** - Complex queries and transactions
✅ **Better Error Handling** - Detailed database error messages
✅ **Connection Pooling** - Efficient connection management
✅ **Automatic Failover** - Falls back to Supabase if needed

## Security Notes

- Store your database password securely
- Use environment variables, not hardcoded values
- Consider using connection pooling for production
- Monitor database connections and usage
- Keep your database credentials private

## Next Steps

1. **Set your DATABASE_URL** with the actual password
2. **Test the connection** using the test script
3. **Restart your backend server** to use PostgreSQL
4. **Test task creation** through the frontend
5. **Monitor performance** and connection health

Your application will now use direct PostgreSQL connections for better performance and reliability! 🎉 