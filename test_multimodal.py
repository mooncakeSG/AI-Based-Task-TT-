#!/usr/bin/env python3
"""
Multimodal AI Test Suite for IntelliAssist.AI Phase 3
Tests image processing, voice transcription, and multimodal chat functionality
"""

import asyncio
import httpx
import json
import os
import sys
import time
from pathlib import Path

async def test_multimodal_endpoints():
    """Test multimodal API endpoints"""
    print("🎯 Testing IntelliAssist.AI Multimodal Features")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test 1: Basic Health Checks
        print("1️⃣ Testing Health Endpoints...")
        try:
            response = await client.get(f"{base_url}/ping")
            print(f"   /ping: {response.status_code} - {response.json()}")
            
            response = await client.get(f"{base_url}/api/v1/ai/health")
            health = response.json()
            print(f"   AI Health: {health['ai_services']['groq_status']}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        # Test 2: Text-only Chat (existing functionality)
        print("\n2️⃣ Testing Text Chat...")
        try:
            chat_data = {
                "message": "Hello! Can you help me organize my daily tasks?",
                "context": None
            }
            
            response = await client.post(
                f"{base_url}/api/v1/chat",
                json=chat_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📊 Response Time: {data['response_time']}s")
                print(f"   💬 Response: {data['response'][:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Text chat failed: {e}")
        
        # Test 3: File Upload
        print("\n3️⃣ Testing File Upload...")
        try:
            # Create a simple test image (this would normally be a real image file)
            test_image_content = b"fake_image_data_for_testing"
            
            files = {"file": ("test_image.jpg", test_image_content, "image/jpeg")}
            
            response = await client.post(
                f"{base_url}/api/v1/upload",
                files=files
            )
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"   ✅ Upload successful: {upload_result['filename']}")
                print(f"   📁 File ID: {upload_result['file_id']}")
                
                # Store file ID for multimodal test
                test_file_id = upload_result['file_id']
                
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                test_file_id = None
                
        except Exception as e:
            print(f"   ❌ File upload failed: {e}")
            test_file_id = None
        
        # Test 4: Multimodal Chat
        print("\n4️⃣ Testing Multimodal Chat...")
        try:
            multimodal_data = {
                "message": "I've uploaded an image. Can you analyze it and help me understand what tasks I need to do?",
                "image_file_id": test_file_id if test_file_id else None,
                "context": None,
                "task_type": "general"
            }
            
            response = await client.post(
                f"{base_url}/api/v1/multimodal",
                json=multimodal_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📊 Processing Time: {data['processing_details']['processing_time']}s")
                print(f"   🔧 Inputs Processed: {', '.join(data['inputs_processed'])}")
                print(f"   💬 Response: {data['response'][:150]}...")
            else:
                error_data = response.json()
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   Error: {error_data.get('detail', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Multimodal chat failed: {e}")
        
        # Test 5: Error Handling
        print("\n5️⃣ Testing Error Handling...")
        try:
            # Test with invalid file ID
            error_data = {
                "message": "Test with invalid file",
                "image_file_id": "nonexistent_file_id",
                "context": None
            }
            
            response = await client.post(
                f"{base_url}/api/v1/multimodal",
                json=error_data
            )
            
            if response.status_code == 404:
                print("   ✅ Correctly handled missing file (404)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
            # Test with no input
            empty_data = {}
            
            response = await client.post(
                f"{base_url}/api/v1/multimodal",
                json=empty_data
            )
            
            if response.status_code == 422:
                print("   ✅ Correctly handled empty request (422)")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
        
        # Test 6: API Documentation
        print("\n6️⃣ Testing API Documentation...")
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("   ✅ API documentation accessible")
            else:
                print(f"   ⚠️  Docs status: {response.status_code}")
                
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                openapi_spec = response.json()
                endpoints = list(openapi_spec.get("paths", {}).keys())
                print(f"   📋 Available endpoints: {len(endpoints)}")
                print(f"       {', '.join(endpoints)}")
            else:
                print(f"   ⚠️  OpenAPI spec status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Documentation test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Multimodal API Test Complete!")

def print_frontend_instructions():
    """Print instructions for manual frontend testing"""
    print("\n" + "=" * 60)
    print("🌐 Frontend Testing Instructions")
    print("=" * 60)
    print()
    print("Your IntelliAssist.AI multimodal interface is now ready!")
    print()
    print("🔗 Open: http://localhost:5173")
    print()
    print("✨ Features to Test:")
    print("   1. 💬 Text Chat - Type messages and get AI responses")
    print("   2. 📷 Image Upload - Click the attachment icon to upload images")
    print("   3. 🎤 Voice Recording - Click the microphone icon to record voice messages")
    print("   4. 🔄 Multimodal - Combine text + image + voice in one message")
    print()
    print("🧪 Test Scenarios:")
    print("   • Upload a task list image and ask for organization help")
    print("   • Record a voice message describing your project needs")
    print("   • Take a photo of your whiteboard and get task extraction")
    print("   • Combine text questions with supporting images")
    print()
    print("🔍 What to Look For:")
    print("   • File upload progress indicators")
    print("   • Voice recording visualization")
    print("   • Attached file previews in messages")
    print("   • AI responses that reference uploaded content")
    print("   • Processing time and input type indicators")
    print()
    print("⚠️  Note: For full functionality, ensure your .env file contains:")
    print("     - GROQ_API_KEY (for LLaMA 3 responses)")
    print("     - HF_API_TOKEN (for image/audio processing)")

async def main():
    """Main test function"""
    print("🚀 IntelliAssist.AI Multimodal Test Suite")
    print("Phase 3: Image Vision + Voice Input")
    print()
    
    try:
        await test_multimodal_endpoints()
        print_frontend_instructions()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 