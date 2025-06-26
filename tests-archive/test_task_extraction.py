#!/usr/bin/env python3

import requests
import json
import time

def test_task_extraction():
    """Test the task extraction functionality"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test message with clear task structure
    test_message = """I need to plan my week. Here's what I need to do:
    
1. Schedule dentist appointment for next Tuesday
2. Finish the project report by Friday
3. Call mom this weekend
4. Buy groceries on Monday
5. Exercise daily for 30 minutes

Can you help me organize these tasks?"""

    print("🧠 Testing AI Task Extraction...")
    print(f"📝 Test message: {test_message[:100]}...")
    
    try:
        # Test chat endpoint
        response = requests.post(
            f"{base_url}/chat",
            json={"message": test_message},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat response received")
            print(f"📊 Response length: {len(result.get('response', ''))}")
            print(f"🎯 Tasks extracted: {len(result.get('tasks', []))}")
            
            if result.get('tasks'):
                print("\n📋 Extracted Tasks:")
                for i, task in enumerate(result['tasks'], 1):
                    print(f"   {i}. {task.get('title', task.get('summary', 'Unknown'))}")
                    print(f"      Category: {task.get('category', 'N/A')}")
                    print(f"      Priority: {task.get('priority', 'N/A')}")
                    print(f"      Status: {task.get('status', 'N/A')}")
                    print()
            else:
                print("⚠️  No tasks were extracted from the response")
                
            print(f"🤖 AI Response: {result.get('response', '')[:200]}...")
            
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing task extraction: {e}")
    
    # Test tasks endpoint
    print(f"\n📋 Testing Tasks Endpoint...")
    try:
        response = requests.get(f"{base_url}/tasks", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tasks endpoint working")
            print(f"📊 Total tasks in database: {result.get('count', 0)}")
            
            if result.get('tasks'):
                print("\n💾 Saved Tasks:")
                for i, task in enumerate(result['tasks'][:5], 1):  # Show first 5
                    print(f"   {i}. {task.get('summary', 'Unknown')[:50]}...")
                    print(f"      Status: {task.get('status', 'N/A')}")
                    print()
        else:
            print(f"❌ Tasks request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing tasks endpoint: {e}")

if __name__ == "__main__":
    test_task_extraction() 