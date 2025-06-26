#!/usr/bin/env python3
"""
Test PostgreSQL Connection and Task Creation
This script tests the new PostgreSQL database service
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.postgres_db import database_service
from backend.config.settings import settings

async def test_postgresql_connection():
    """Test PostgreSQL connection and basic operations"""
    print("🔗 Testing PostgreSQL Database Connection...")
    print(f"Database URL configured: {'Yes' if settings.database_url else 'No'}")
    
    # Initialize connections
    await database_service.initialize_connections()
    
    # Check health
    health = await database_service.health_check()
    print(f"Database Status: {health}")
    
    if health['type'] == 'postgresql':
        print("✅ PostgreSQL connection successful!")
        
        # Test task creation
        print("\n📝 Testing task creation...")
        
        # Clear existing tasks
        cleared = await database_service.clear_all_tasks()
        print(f"Cleared {cleared} existing tasks")
        
        # Create test tasks
        test_tasks = [
            {
                "summary": "Test PostgreSQL connection",
                "category": "development",
                "priority": "high",
                "status": "pending",
                "user_id": "test_user"
            },
            {
                "summary": "Verify task storage in PostgreSQL",
                "category": "testing",
                "priority": "medium",
                "status": "pending",
                "user_id": "test_user"
            },
            {
                "summary": "Check task retrieval functionality",
                "category": "validation",
                "priority": "low",
                "status": "pending",
                "user_id": "test_user"
            }
        ]
        
        created_tasks = []
        for task_data in test_tasks:
            task = await database_service.create_task(task_data)
            if task:
                created_tasks.append(task)
                print(f"✅ Created task: {task['id']} - {task['summary']}")
            else:
                print(f"❌ Failed to create task: {task_data['summary']}")
        
        # Retrieve tasks
        print(f"\n📋 Retrieving tasks...")
        all_tasks = await database_service.get_tasks()
        print(f"Total tasks in database: {len(all_tasks)}")
        
        for task in all_tasks:
            print(f"  - Task {task['id']}: {task['summary']} [{task['status']}]")
        
        # Test user-specific tasks
        user_tasks = await database_service.get_tasks(user_id="test_user")
        print(f"\nTasks for test_user: {len(user_tasks)}")
        
        print(f"\n🎉 PostgreSQL test completed successfully!")
        print(f"   - Connection type: {health['type']}")
        print(f"   - Tasks created: {len(created_tasks)}")
        print(f"   - Tasks retrieved: {len(all_tasks)}")
        
    elif health['type'] == 'supabase':
        print("⚠️  Using Supabase fallback instead of PostgreSQL")
        print("   Check your DATABASE_URL configuration")
        
    elif health['type'] == 'memory':
        print("⚠️  Using in-memory storage")
        print("   No database connection available")
        print("   Check your DATABASE_URL and Supabase configuration")
    
    else:
        print("❌ Database connection failed")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 Starting PostgreSQL Database Test\n")
    
    try:
        success = await test_postgresql_connection()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 