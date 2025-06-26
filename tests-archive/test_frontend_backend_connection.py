#!/usr/bin/env python3
"""
Frontend-Backend Connection Test
Verify that the frontend can properly communicate with the backend
"""

import asyncio
import httpx
import json

async def test_connection():
    """Test frontend-backend connection"""
    print("🔗 Testing Frontend-Backend Connection")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: Backend Health
        print("1️⃣ Testing Backend Health...")
        try:
            response = await client.get(f"{backend_url}/ping")
            if response.status_code == 200:
                print("   ✅ Backend is running")
                print(f"   📊 Response: {response.json()}")
            else:
                print(f"   ❌ Backend error: {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ Backend not reachable: {e}")
            return
        
        # Test 2: CORS Configuration
        print("\n2️⃣ Testing CORS Configuration...")
        try:
            response = await client.options(
                f"{backend_url}/api/v1/chat",
                headers={
                    "Origin": frontend_url,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            if response.status_code == 200:
                allow_origin = response.headers.get("access-control-allow-origin")
                if allow_origin == frontend_url:
                    print("   ✅ CORS properly configured")
                else:
                    print(f"   ⚠️  CORS origin mismatch: {allow_origin}")
            else:
                print(f"   ❌ CORS preflight failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ CORS test failed: {e}")
        
        # Test 3: Chat Endpoint
        print("\n3️⃣ Testing Chat Endpoint...")
        try:
            chat_data = {
                "message": "Hello! This is a connection test.",
                "context": None
            }
            
            response = await client.post(
                f"{backend_url}/api/v1/chat",
                json=chat_data,
                headers={
                    "Content-Type": "application/json",
                    "Origin": frontend_url
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Chat endpoint working")
                print(f"   🤖 Response preview: {result['response'][:100]}...")
                print(f"   ⏱️  Response time: {result['response_time']}s")
            else:
                print(f"   ❌ Chat endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Chat test failed: {e}")
        
        # Test 4: Frontend Accessibility
        print("\n4️⃣ Testing Frontend Accessibility...")
        try:
            response = await client.get(frontend_url)
            if response.status_code == 200:
                print("   ✅ Frontend is accessible")
                if "AI Task Assistant" in response.text:
                    print("   ✅ Frontend loaded correctly")
                else:
                    print("   ⚠️  Frontend content unexpected")
            else:
                print(f"   ❌ Frontend error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Frontend not reachable: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Connection Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Refresh your browser at http://localhost:5173")
    print("   2. Try typing a message like 'Hello!'")
    print("   3. You should now get real AI responses")
    print("   4. Test the file upload and voice recording features")

async def main():
    """Main test function"""
    print("🚀 IntelliAssist.AI Connection Test")
    print("Verifying Frontend ↔ Backend Communication")
    print()
    
    try:
        await test_connection()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 