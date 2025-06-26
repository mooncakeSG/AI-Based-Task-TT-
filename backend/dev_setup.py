#!/usr/bin/env python3
"""
IntelliAssist.AI Backend Development Setup Script
Helps configure environment variables and start the development server.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from the example template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from env.example")
        print("📝 Please edit .env file to add your API keys:")
        print("   - GROQ_API_KEY: Get from https://console.groq.com/")
        print("   - HF_API_KEY: Get from https://huggingface.co/settings/tokens")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Core dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def create_upload_directory():
    """Create uploads directory if it doesn't exist"""
    upload_dir = Path("uploads")
    try:
        upload_dir.mkdir(exist_ok=True)
        print("✅ Upload directory created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create upload directory: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 IntelliAssist.AI Backend Development Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    success = True
    
    # Setup steps
    success &= check_dependencies()
    success &= create_env_file()
    success &= create_upload_directory()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Development setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python main.py")
        print("3. Open: http://localhost:8000/docs")
        print("\n📚 API Endpoints:")
        print("- Health: GET /ping")
        print("- Chat: POST /api/v1/chat")
        print("- Upload: POST /api/v1/upload")
    else:
        print("❌ Setup encountered some issues")
        print("Please fix the issues above and run setup again")
        sys.exit(1)

if __name__ == "__main__":
    main() 