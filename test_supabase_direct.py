#!/usr/bin/env python3
"""
Direct Supabase Connection Test
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

async def test_supabase_direct():
    """Test Supabase connection directly"""
    print("🔗 Testing Supabase Connection Directly...")
    
    if not SUPABASE_AVAILABLE:
        print("❌ Supabase client not available. Install with: pip install supabase")
        return False
    
    # Get credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"SUPABASE_URL configured: {'Yes' if supabase_url else 'No'}")
    print(f"SUPABASE_ANON_KEY configured: {'Yes' if supabase_anon_key else 'No'}")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Supabase credentials not found in environment")
        print("Make sure your .env file contains:")
        print("SUPABASE_URL=https://your-project-id.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key-here")
        return False
    
    if supabase_url == "https://your-project-id.supabase.co":
        print("❌ Supabase URL is still placeholder")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        print("✅ Supabase client created successfully")
        
        # Test connection with a simple query
        result = supabase.table('tasks').select('count').limit(1).execute()
        print("✅ Supabase connection test successful")
        
        # Try to get existing tasks
        tasks_result = supabase.table('tasks').select('*').limit(5).execute()
        print(f"📋 Found {len(tasks_result.data) if tasks_result.data else 0} existing tasks")
        
        # Try to create a test task
        test_task = {
            "summary": "Test task from direct connection",
            "category": "testing",
            "priority": "high",
            "status": "pending",
            "created_at": "2025-06-23T12:00:00Z"
        }
        
        create_result = supabase.table('tasks').insert(test_task).execute()
        if create_result.data:
            print(f"✅ Successfully created test task: {create_result.data[0].get('id')}")
            
            # Clean up the test task
            task_id = create_result.data[0].get('id')
            if task_id:
                delete_result = supabase.table('tasks').delete().eq('id', task_id).execute()
                print("🧹 Cleaned up test task")
        else:
            print("❌ Failed to create test task")
            return False
        
        print("🎉 Supabase connection and operations working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Direct Supabase Test\n")
    
    try:
        success = await test_supabase_direct()
        if success:
            print("\n✅ Supabase connection test passed!")
        else:
            print("\n❌ Supabase connection test failed!")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 