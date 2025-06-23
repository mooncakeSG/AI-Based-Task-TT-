#!/usr/bin/env python3
"""
Simple Supabase Task Creation Test
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the backend directory
load_dotenv('backend/.env')

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

def test_supabase_task_creation():
    """Test Supabase task creation directly"""
    print("🧪 Testing Supabase Task Creation...")
    
    if not SUPABASE_AVAILABLE:
        print("❌ Supabase client not available")
        return False
    
    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"SUPABASE_URL: {'✅' if supabase_url else '❌'}")
    print(f"SUPABASE_ANON_KEY: {'✅' if supabase_anon_key else '❌'}")
    
    if supabase_url:
        print(f"URL starts with: {supabase_url[:30]}...")
    if supabase_anon_key:
        print(f"Key starts with: {supabase_anon_key[:20]}...")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        # Create client
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        print("✅ Supabase client created")
        
        # Test simple task creation with only required fields
        test_task = {
            "summary": "Test task from direct script - UUID fix!",
            "user_id": None  # Set to null since UUID format is required
        }
        
        print(f"📝 Creating task: {test_task}")
        result = supabase.table('tasks').insert(test_task).execute()
        
        if result.data:
            task_id = result.data[0].get('id')
            print(f"✅ Task created successfully! ID: {task_id}")
            print(f"📋 Task data: {result.data[0]}")
            
            # Verify by reading it back
            read_result = supabase.table('tasks').select('*').eq('id', task_id).execute()
            if read_result.data:
                print(f"✅ Task verified in database: {read_result.data[0]}")
            
            return True
        else:
            print(f"❌ Task creation failed - no data returned")
            print(f"Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Supabase Test\n")
    success = test_supabase_task_creation()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}") 