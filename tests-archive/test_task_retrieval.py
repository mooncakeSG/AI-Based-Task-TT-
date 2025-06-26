#!/usr/bin/env python3
"""
Test Task Retrieval from Supabase
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_task_operations():
    """Test task creation and retrieval"""
    print("🧪 Testing Task Operations...")
    
    try:
        from services.postgres_db import database_service
        
        # Test database health
        health = await database_service.health_check()
        print(f"Database Health: {health}")
        
        # Test task creation
        print("\n📝 Testing Task Creation...")
        test_task = {
            "summary": "Test task from debug script",
            "category": "testing",
            "priority": "high",
            "status": "pending",
            "user_id": None
        }
        
        created_task = await database_service.create_task(test_task)
        if created_task:
            print(f"✅ Task created: {created_task}")
        else:
            print("❌ Task creation failed")
        
        # Test task retrieval
        print("\n📋 Testing Task Retrieval...")
        tasks = await database_service.get_tasks()
        print(f"Retrieved {len(tasks)} tasks:")
        for i, task in enumerate(tasks):
            print(f"  {i+1}. {task}")
        
        return len(tasks) > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Task Retrieval Test\n")
    success = asyncio.run(test_task_operations())
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}") 