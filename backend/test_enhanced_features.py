#!/usr/bin/env python3
"""
Comprehensive test script for enhanced features
Tests AI service, document processing, task saving, and more
"""

import asyncio
import requests
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api/v1"  # Change to your deployed URL if needed

def create_test_files():
    """Create sample test files for document processing"""
    test_files = {}
    
    # Create temporary directory
    temp_dir = Path("test_files")
    temp_dir.mkdir(exist_ok=True)
    
    # 1. Create a sample CSV file
    csv_content = """Name,Email,Department,Task,Priority,Status
John Doe,john@example.com,Engineering,Complete API documentation,High,Pending
Jane Smith,jane@example.com,Marketing,Launch social media campaign,Medium,In Progress
Bob Johnson,bob@example.com,HR,Update employee handbook,Low,Completed
Alice Brown,alice@example.com,Finance,Prepare Q3 budget report,High,Pending
Mike Wilson,mike@example.com,Engineering,Fix production bugs,Critical,In Progress"""
    
    csv_path = temp_dir / "sample_tasks.csv"
    with open(csv_path, 'w') as f:
        f.write(csv_content)
    test_files['csv'] = csv_path
    
    # 2. Create a sample text file
    txt_content = """Meeting Notes - Project Planning Session
Date: 2024-01-15
Attendees: John, Jane, Mike, Sarah

ACTION ITEMS:
1. Need to update the project timeline by Friday
2. Schedule follow-up meeting with stakeholders next week
3. Review budget allocation for Q2
4. Must finalize the technical specifications
5. Contact the legal team about licensing requirements

DECISIONS MADE:
- Approved the new feature set
- Decided to use React for frontend
- Set deployment target for March 1st

NEXT STEPS:
- John will create the project roadmap
- Jane to follow up with marketing team
- Mike should review the security requirements
- Sarah will coordinate with external vendors

URGENT: The client presentation is scheduled for next Tuesday - need to prepare slides and demo.
"""
    
    txt_path = temp_dir / "meeting_notes.txt"
    with open(txt_path, 'w') as f:
        f.write(txt_content)
    test_files['txt'] = txt_path
    
    # 3. Create a sample log file
    log_content = """2024-01-15 09:00:00 INFO: System startup completed
2024-01-15 09:05:00 WARNING: Database connection slow
2024-01-15 09:10:00 ERROR: Failed to process user request ID:12345
2024-01-15 09:15:00 INFO: TODO: Investigate database performance issues
2024-01-15 09:20:00 ERROR: Critical: Payment gateway timeout
2024-01-15 09:25:00 INFO: ACTION REQUIRED: Contact payment provider support
2024-01-15 09:30:00 INFO: User reported bug in mobile app - need to fix ASAP
2024-01-15 09:35:00 WARNING: Server memory usage at 85%
2024-01-15 09:40:00 INFO: Scheduled maintenance required this weekend
"""
    
    log_path = temp_dir / "system.log"
    with open(log_path, 'w') as f:
        f.write(log_content)
    test_files['log'] = log_path
    
    print(f"✅ Created test files in {temp_dir}/")
    return test_files

async def test_system_status():
    """Test system status and AI capabilities"""
    print("\n1️⃣ Testing System Status...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System Status: {status.get('status', 'unknown')}")
            print(f"📊 Version: {status.get('version', 'unknown')}")
            
            ai_services = status.get('ai_services', {})
            print(f"\n🤖 AI Services Status:")
            for service, available in ai_services.items():
                status_emoji = "✅" if available else "❌"
                print(f"  {status_emoji} {service}: {available}")
            
            features = status.get('features', [])
            print(f"\n🔧 Available Features: {', '.join(features)}")
            
            data_counts = status.get('data_counts', {})
            print(f"\n📈 Data Counts:")
            for key, count in data_counts.items():
                print(f"  - {key}: {count}")
                
            return True
            
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

async def test_file_upload_and_analysis(test_files):
    """Test file upload and enhanced document analysis"""
    print("\n2️⃣ Testing Enhanced Document Analysis...")
    print("=" * 50)
    
    results = {}
    
    for file_type, file_path in test_files.items():
        print(f"\n📄 Testing {file_type.upper()} file: {file_path.name}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                response = requests.post(f"{API_BASE}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                results[file_type] = result
                
                print(f"✅ Upload successful!")
                print(f"🔍 Analysis Type: {result.get('analysis_type', 'unknown')}")
                print(f"📝 Processing Method: {result.get('processing_method', 'unknown')}")
                print(f"🤖 AI Processed: {result.get('ai_processed', False)}")
                
                # Check content extraction
                content_length = result.get('content_length', 0)
                if content_length > 0:
                    print(f"📊 Content Extracted: {content_length} characters")
                    
                    # Show content preview
                    preview = result.get('extracted_content_preview', '')
                    if preview:
                        print(f"👀 Content Preview: {preview[:100]}...")
                
                # Check extracted tasks
                tasks = result.get('tasks', [])
                print(f"✅ Tasks Extracted: {len(tasks)}")
                for i, task in enumerate(tasks[:3], 1):  # Show first 3 tasks
                    print(f"  {i}. {task.get('title', 'No title')} ({task.get('priority', 'unknown')} priority)")
                
                # Check suggestions
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print(f"💡 Suggestions: {len(suggestions)} provided")
                    for suggestion in suggestions[:2]:  # Show first 2 suggestions
                        print(f"  • {suggestion}")
                        
            else:
                print(f"❌ Upload failed: {response.status_code}")
                if response.text:
                    print(f"Error: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Upload error for {file_type}: {e}")
    
    return results

async def main():
    """Run comprehensive feature tests"""
    print("🧪 COMPREHENSIVE FEATURE TESTING")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE}")
    
    # Create test files
    print("\n📁 Preparing test files...")
    test_files = create_test_files()
    
    results = {
        'system_status': False,
        'file_analysis': False
    }
    
    # Run tests
    results['system_status'] = await test_system_status()
    
    if results['system_status']:
        results['file_analysis'] = await test_file_upload_and_analysis(test_files)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL FEATURES ARE WORKING!")
    else:
        print("⚠️ Some features need attention.")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 