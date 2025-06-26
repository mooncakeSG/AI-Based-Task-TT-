#!/usr/bin/env python3

import asyncio
import requests
import json

async def test_supabase_connection():
    """Test the Supabase database connection"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🔗 Testing Supabase Connection...")
    
    try:
        # Test database health endpoint
        response = requests.get(f"{base_url}/database/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            database_status = result.get('database', {})
            status = database_status.get('status', 'unknown')
            
            print(f"✅ Database health check: {status}")
            
            if status in ['connected', 'development_mode']:
                if status == 'development_mode':
                    print("🛠️ Running in development mode with in-memory storage!")
                    print(f"📊 Current tasks in memory: {database_status.get('tasks_count', 0)}")
                else:
                    print("🎉 Supabase connection is working!")
                
                # Test creating a task directly via API
                print("\n📝 Testing direct task creation...")
                
                test_task = {
                    "summary": "Test task from Python script",
                    "category": "testing",
                    "priority": "low",
                    "status": "pending"
                }
                
                create_response = requests.post(
                    f"{base_url}/tasks",
                    json=test_task,
                    timeout=10
                )
                
                if create_response.status_code == 200:
                    created_task = create_response.json()
                    print(f"✅ Task created successfully: ID {created_task.get('id')}")
                    
                    # Verify task was saved
                    tasks_response = requests.get(f"{base_url}/tasks", timeout=10)
                    if tasks_response.status_code == 200:
                        tasks_result = tasks_response.json()
                        print(f"📊 Total tasks now: {tasks_result.get('count', 0)}")
                        
                        # Find our test task
                        test_task_found = any(
                            task.get('summary') == test_task['summary'] 
                            for task in tasks_result.get('tasks', [])
                        )
                        
                        if test_task_found:
                            print("✅ Test task found in database!")
                        else:
                            print("⚠️ Test task not found in database")
                    
                else:
                    print(f"❌ Task creation failed: {create_response.status_code}")
                    print(f"Error: {create_response.text}")
                    
            else:
                print(f"⚠️ Database status: {status}")
                print("💡 Check your Supabase configuration in .env file")
                
        else:
            print(f"❌ Database health check failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        print("💡 Make sure the backend server is running on port 8000")

if __name__ == "__main__":
    asyncio.run(test_supabase_connection()) 