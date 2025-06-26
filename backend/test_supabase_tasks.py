#!/usr/bin/env python3
"""
Test script to verify Supabase task functionality
Run this to check if task creation, retrieval, and deletion is working
"""

import asyncio
import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api/v1"  # Change to your deployed URL if needed

async def test_supabase_tasks():
    """Test the complete task workflow with Supabase integration"""
    
    print("🧪 Testing Supabase Task Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Check system status
        print("\n1️⃣ Checking system status...")
        response = requests.get(f"{API_BASE}/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System Status: {status.get('status')}")
            print(f"📊 Current tasks in system: {status.get('data_counts', {}).get('tasks', 0)}")
            
            ai_services = status.get('ai_services', {})
            print(f"🤖 Supabase: {'✅' if ai_services.get('supabase') else '❌'}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
        # Test 2: Get current tasks
        print("\n2️⃣ Fetching existing tasks...")
        response = requests.get(f"{API_BASE}/tasks", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tasks retrieved successfully")
            print(f"📋 Source: {result.get('source', 'unknown')}")
            print(f"📊 Count: {result.get('count', 0)} tasks")
            
            if result.get('tasks'):
                print(f"📄 Sample task: {result['tasks'][0].get('summary', 'No summary')[:50]}...")
        else:
            print(f"❌ Get tasks failed: {response.status_code}")
            
        # Test 3: Create a new test task
        print("\n3️⃣ Creating test task...")
        test_task = {
            "title": f"Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This is a test task created by the Supabase integration test",
            "category": "testing",
            "priority": "medium",
            "status": "pending"
        }
        
        response = requests.post(
            f"{API_BASE}/tasks",
            json=test_task,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            created_task = result.get('task', {})
            task_id = created_task.get('id')
            print(f"✅ Task created successfully!")
            print(f"🆔 Task ID: {task_id}")
            print(f"📍 Source: {result.get('source', 'unknown')}")
            print(f"📝 Title: {created_task.get('title', 'No title')}")
            
            # Test 4: Update the task
            if task_id:
                print(f"\n4️⃣ Updating task {task_id}...")
                update_response = requests.put(
                    f"{API_BASE}/tasks/{task_id}",
                    json={"status": "completed", "priority": "high"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    print(f"✅ Task updated successfully!")
                    print(f"📍 Source: {update_result.get('source', 'unknown')}")
                else:
                    print(f"❌ Task update failed: {update_response.status_code}")
                    print(f"Error: {update_response.text}")
                
                # Test 5: Delete the test task
                print(f"\n5️⃣ Cleaning up test task {task_id}...")
                delete_response = requests.delete(
                    f"{API_BASE}/tasks/{task_id}",
                    timeout=10
                )
                
                if delete_response.status_code == 200:
                    delete_result = delete_response.json()
                    print(f"✅ Test task deleted successfully!")
                    print(f"📍 Source: {delete_result.get('source', 'unknown')}")
                else:
                    print(f"❌ Task deletion failed: {delete_response.status_code}")
                    print(f"Error: {delete_response.text}")
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
        # Test 6: Final status check
        print("\n6️⃣ Final system check...")
        response = requests.get(f"{API_BASE}/tasks", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Final task count: {result.get('count', 0)}")
            print(f"📍 Database source: {result.get('source', 'unknown')}")
            
            if result.get('source') == 'supabase':
                print("🎉 SUPABASE INTEGRATION IS WORKING CORRECTLY!")
            elif result.get('source') == 'memory':
                print("⚠️ Using memory storage - Supabase not connected")
            else:
                print(f"ℹ️ Using {result.get('source')} storage")
        
        print("\n" + "=" * 50)
        print("✅ Supabase task integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Supabase Task Integration Test")
    print("Make sure your backend server is running!")
    print()
    
    asyncio.run(test_supabase_tasks()) 