#!/usr/bin/env python3

import asyncio
import httpx
import os
import sys

# Add the current directory to Python path
sys.path.append('.')

from config.settings import settings

async def test_hf_api():
    """Test HuggingFace Whisper API directly"""
    
    print("🔍 Testing HuggingFace Audio Transcription API")
    print("=" * 50)
    
    # Check API key
    if not settings.hf_api_key:
        print("❌ No HuggingFace API key found!")
        print("💡 Make sure HF_API_KEY is set in your .env file")
        return
    
    print(f"✅ API Key: {settings.hf_api_key[:10]}...")
    print(f"🌐 Base URL: {settings.hf_base_url}")
    
    # Test the API endpoint
    model_name = "openai/whisper-large-v3"
    url = f"{settings.hf_base_url}/models/{model_name}"
    
    headers = {
        "Authorization": f"Bearer {settings.hf_api_key}",
    }
    
    print(f"📡 Testing URL: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, test with a simple GET request to check auth
            print("\n🧪 Step 1: Testing API authentication...")
            
            # Try to get model info
            info_response = await client.get(url, headers=headers)
            print(f"Model info response: {info_response.status_code}")
            
            if info_response.status_code == 200:
                print("✅ API authentication successful!")
            elif info_response.status_code == 401:
                print("❌ API key authentication failed!")
                return
            elif info_response.status_code == 404:
                print("⚠️  Model not found, but API key seems valid")
            else:
                print(f"⚠️  Unexpected response: {info_response.status_code}")
                print(f"Response: {info_response.text[:200]}")
            
            # Test with a minimal audio request
            print("\n🧪 Step 2: Testing audio endpoint...")
            
            # Create minimal test audio data (this will fail but show us the error format)
            test_data = b"RIFF\x00\x00\x00\x00WAVE"  # Minimal WAV header
            
            audio_response = await client.post(
                url,
                content=test_data,
                headers=headers
            )
            
            print(f"Audio API response: {audio_response.status_code}")
            print(f"Response content: {audio_response.text[:500]}")
            
            if audio_response.status_code == 422:
                print("✅ API accepts requests! (422 = invalid audio format)")
                print("🎯 The API is working, we just need proper audio format")
            elif audio_response.status_code == 503:
                print("⏳ Model is loading, try again in a moment")
            elif audio_response.status_code == 200:
                print("✅ API call successful!")
                try:
                    result = audio_response.json()
                    print(f"Result: {result}")
                except:
                    print("Response is not JSON")
            else:
                print(f"❌ Unexpected error: {audio_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    asyncio.run(test_hf_api()) 