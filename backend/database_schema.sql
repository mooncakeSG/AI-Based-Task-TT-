-- IntelliAssist.AI Database Schema for Supabase
-- Run this script in your Supabase SQL editor to create all necessary tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100),
    full_name VARCHAR(255),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS (Row Level Security) for users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- ==========================================
-- TASKS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    due_date TIMESTAMP WITH TIME ZONE,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Add RLS for tasks
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own tasks
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tasks" ON tasks
    FOR DELETE USING (auth.uid() = user_id);

-- ==========================================
-- CHAT HISTORY TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID DEFAULT uuid_generate_v4(),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(100),
    response_time FLOAT,
    tokens_used INTEGER,
    context TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for chat history
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at DESC);

-- Add RLS for chat history
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Users can only see their own chat history
CREATE POLICY "Users can view own chat history" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat history" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- UPLOADED FILES TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS uploaded_files (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    storage_bucket VARCHAR(100) DEFAULT 'uploads',
    processing_status VARCHAR(50) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_result JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for uploaded files
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_content_type ON uploaded_files(content_type);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_processing_status ON uploaded_files(processing_status);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_created_at ON uploaded_files(created_at DESC);

-- Add RLS for uploaded files
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;

-- Users can only see and modify their own files
CREATE POLICY "Users can view own files" ON uploaded_files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own files" ON uploaded_files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own files" ON uploaded_files
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own files" ON uploaded_files
    FOR DELETE USING (auth.uid() = user_id);

-- ==========================================
-- ANALYTICS TABLE (Optional)
-- ==========================================
CREATE TABLE IF NOT EXISTS analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at DESC);

-- Add RLS for analytics
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Users can only see their own analytics data
CREATE POLICY "Users can view own analytics" ON analytics_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analytics" ON analytics_events
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- FUNCTIONS AND TRIGGERS
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_uploaded_files_updated_at BEFORE UPDATE ON uploaded_files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- SAMPLE DATA (Optional - for testing)
-- ==========================================

-- Insert a sample user (you can remove this in production)
-- INSERT INTO users (id, email, username, full_name) VALUES 
-- ('00000000-0000-0000-0000-000000000000', 'demo@intelliassist.ai', 'demo_user', 'Demo User')
-- ON CONFLICT (email) DO NOTHING;

-- Insert sample tasks (you can remove this in production)
-- INSERT INTO tasks (user_id, summary, category, priority, status) VALUES 
-- ('00000000-0000-0000-0000-000000000000', 'Complete project presentation', 'work', 'high', 'pending'),
-- ('00000000-0000-0000-0000-000000000000', 'Review quarterly budget', 'finance', 'medium', 'pending'),
-- ('00000000-0000-0000-0000-000000000000', 'Schedule team meeting', 'management', 'low', 'completed')
-- ON CONFLICT DO NOTHING;

-- ==========================================
-- VIEWS (Optional - for easier querying)
-- ==========================================

-- View for task statistics per user
CREATE OR REPLACE VIEW user_task_stats AS
SELECT 
    user_id,
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
    COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority_tasks,
    COUNT(CASE WHEN priority = 'urgent' THEN 1 END) as urgent_tasks
FROM tasks
GROUP BY user_id;

-- View for recent activity
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'task' as activity_type,
    t.id as item_id,
    t.user_id,
    t.summary as title,
    t.status as status,
    t.created_at,
    t.updated_at
FROM tasks t
UNION ALL
SELECT 
    'chat' as activity_type,
    c.id as item_id,
    c.user_id,
    LEFT(c.message, 50) as title,
    'completed' as status,
    c.created_at,
    c.created_at as updated_at
FROM chat_history c
ORDER BY created_at DESC;

-- ==========================================
-- SECURITY NOTES
-- ==========================================

-- 1. Row Level Security (RLS) is enabled on all tables
-- 2. Users can only access their own data
-- 3. All foreign keys have proper CASCADE rules
-- 4. Indexes are added for performance
-- 5. Check constraints ensure data integrity
-- 6. UUID is used for user IDs for better security
-- 7. Timestamps use timezone-aware types

-- ==========================================
-- SETUP INSTRUCTIONS
-- ==========================================

-- 1. Run this script in your Supabase SQL editor
-- 2. Set up authentication in Supabase dashboard
-- 3. Configure your environment variables:
--    SUPABASE_URL=https://your-project.supabase.co
--    SUPABASE_ANON_KEY=your-anon-key
--    SUPABASE_SERVICE_KEY=your-service-key (for server-side operations)
-- 4. Test the connection using the health check endpoint 