# Supabase Authentication Setup Guide

This guide will help you set up Supabase authentication for the AI-Based Task Management application.

## Prerequisites

1. **Supabase Account**: Create an account at [supabase.com](https://supabase.com)
2. **Project Created**: You should have already created a Supabase project for the task management system

## Step 1: Configure Authentication Settings

### 1.1 Enable Email Authentication

1. Go to your Supabase project dashboard
2. Navigate to **Authentication** → **Settings**
3. Under **Auth Providers**, ensure **Email** is enabled
4. Configure the following settings:

```
✅ Enable email confirmations
✅ Enable email change confirmations
✅ Enable secure email change
⚠️  Disable sign ups (optional - enable only if you want public registration)
```

### 1.2 Configure Email Templates (Optional)

1. Go to **Authentication** → **Email Templates**
2. Customize the confirmation and recovery email templates
3. Update the redirect URLs to match your domain

## Step 2: Set Up Row Level Security (RLS)

### 2.1 Enable RLS on Tasks Table

```sql
-- Enable RLS on the tasks table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to see only their own tasks
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (auth.uid()::text = user_id);

-- Policy to allow users to insert their own tasks
CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- Policy to allow users to update their own tasks
CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Policy to allow users to delete their own tasks
CREATE POLICY "Users can delete own tasks" ON tasks
    FOR DELETE USING (auth.uid()::text = user_id);
```

### 2.2 Create User Profiles Table (Optional)

```sql
-- Create a profiles table for additional user data
CREATE TABLE profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    full_name TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    
    PRIMARY KEY (id)
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy for profiles
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Function to automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

## Step 3: Update Environment Variables

### 3.1 Backend Environment Variables

Update your `backend/.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Database URL (if using direct PostgreSQL connection)
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# Other existing variables...
GROQ_API_KEY=your-groq-api-key
HF_API_KEY=your-hugging-face-api-key
```

### 3.2 Frontend Environment Variables

Update your `react-app/.env` file:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key

# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
```

## Step 4: Test Authentication Flow

### 4.1 Backend Testing

1. Start the backend server:
```bash
cd backend
python -m uvicorn main:app --reload
```

2. Test authentication endpoints:
```bash
# Health check
curl http://localhost:8000/api/v1/auth/health

# Sign up
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Sign in
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 4.2 Frontend Testing

1. Start the frontend development server:
```bash
cd react-app
npm run dev
```

2. Test the authentication flow:
   - Click "Sign Up" in the header
   - Create a new account
   - Check your email for verification
   - Sign in with your credentials
   - Test creating tasks (should be user-specific)

## Step 5: Security Considerations

### 5.1 API Security

1. **JWT Token Validation**: The backend validates JWT tokens from Supabase
2. **User ID Extraction**: User ID is extracted from authenticated requests
3. **Data Isolation**: Tasks and data are isolated by user ID

### 5.2 Frontend Security

1. **Token Storage**: Tokens are managed by Supabase client
2. **Automatic Refresh**: Tokens are automatically refreshed
3. **Secure Logout**: Proper session cleanup on logout

### 5.3 Database Security

1. **Row Level Security**: Enabled on all user data tables
2. **Service Role**: Used only for admin operations
3. **Anon Key**: Used for client-side operations with RLS

## Step 6: Production Deployment

### 6.1 Update CORS Settings

In Supabase dashboard:
1. Go to **Settings** → **API**
2. Update **CORS origins** to include your production domain

### 6.2 Environment Variables for Production

```env
# Production Frontend
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
VITE_API_URL=https://your-backend-domain.com/api/v1

# Production Backend
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
```

### 6.3 Email Configuration

For production, configure custom SMTP:
1. Go to **Settings** → **Auth**
2. Configure **SMTP Settings**
3. Update email templates with production URLs

## Step 7: Advanced Features

### 7.1 Social Authentication (Optional)

Enable Google, GitHub, or other providers:
1. Go to **Authentication** → **Settings**
2. Configure OAuth providers
3. Update frontend to include social login buttons

### 7.2 Multi-Factor Authentication (Optional)

Enable MFA for enhanced security:
1. Go to **Authentication** → **Settings**
2. Enable **Multi-Factor Authentication**
3. Update frontend to handle MFA flow

### 7.3 User Roles and Permissions (Optional)

Implement role-based access:
1. Add role column to profiles table
2. Create policies based on roles
3. Update frontend to show/hide features based on roles

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP configuration and email templates
2. **RLS blocking queries**: Verify policies and user authentication
3. **CORS errors**: Update allowed origins in Supabase settings
4. **Token expiration**: Ensure automatic refresh is working

### Debug Steps

1. Check browser console for authentication errors
2. Verify JWT tokens in browser developer tools
3. Test API endpoints with curl or Postman
4. Check Supabase logs for authentication events

## API Endpoints Reference

### Authentication Endpoints

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/signin` - Sign in user
- `POST /api/v1/auth/signout` - Sign out user
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/reset-password` - Reset password
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update user profile
- `GET /api/v1/auth/status` - Check auth status
- `GET /api/v1/auth/health` - Auth service health

### Protected Endpoints

All task-related endpoints now require authentication:
- `GET /api/v1/tasks` - Get user's tasks
- `POST /api/v1/tasks` - Create task for user
- `PUT /api/v1/tasks/{id}` - Update user's task
- `DELETE /api/v1/tasks/{id}` - Delete user's task

## Conclusion

This authentication system provides:
- ✅ Secure user registration and login
- ✅ Email verification
- ✅ Password reset functionality
- ✅ JWT token-based authentication
- ✅ User-specific data isolation
- ✅ Row-level security
- ✅ Automatic token refresh
- ✅ Responsive UI components

The system is production-ready and follows security best practices for modern web applications. 