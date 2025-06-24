import asyncio
import httpx
import os
from config.settings import settings

async def test_hf_audio_api():
    """Test HuggingFace audio transcription API"""
    
    # Check if API key is configured
    if not settings.hf_api_key:
        print("❌ HuggingFace API key not configured")
        print("💡 Add HF_API_KEY to your .env file")
        return False
    
    print(f"✅ HuggingFace API key configured: {settings.hf_api_key[:10]}...")
    
    # Test API with a simple request
    url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {
        "Authorization": f"Bearer {settings.hf_api_key}",
    }
    
    # Test with minimal audio data or just check the endpoint
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url.replace("/models", "/status"))
            print(f"📡 HuggingFace API status: {response.status_code}")
            
            # If status endpoint doesn't work, try a test request
            if response.status_code != 200:
                # Create a minimal test request
                test_response = await client.post(
                    url, 
                    headers=headers,
                    content=b"test"  # Minimal content to test headers
                )
                print(f"🧪 Test API response: {test_response.status_code}")
                if test_response.status_code == 422:
                    print("✅ API accepts requests (422 = invalid audio format, but auth works)")
                    return True
                elif test_response.status_code == 401:
                    print("❌ API key invalid")
                    return False
                else:
                    print(f"📝 API response: {test_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True

async def main():
    print("🎤 Testing HuggingFace Audio Transcription API")
    print("=" * 50)
    
    success = await test_hf_audio_api()
    
    if success:
        print("\n✅ Audio transcription should work!")
        print("🎯 Try uploading an audio file to test real transcription")
    else:
        print("\n❌ Audio transcription needs configuration")
        print("💡 Check your HF_API_KEY in the .env file")

if __name__ == "__main__":
    asyncio.run(main()) 