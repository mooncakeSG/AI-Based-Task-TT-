# IntelliAssist.AI Backend

FastAPI-based backend for the IntelliAssist.AI application, providing AI-powered chat functionality and multimodal file processing capabilities.

## 🚀 Features

- **Chat API**: LLaMA 3 integration via Groq API
- **File Upload**: Support for images, audio, and PDFs
- **Multimodal Processing**: Image analysis and audio transcription via Hugging Face
- **CORS Support**: Configured for React frontend integration
- **Comprehensive Logging**: Request/response timing and error tracking
- **Error Handling**: Friendly JSON error responses
- **Health Monitoring**: Built-in health check endpoints

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── routes/
│   ├── __init__.py
│   └── chat.py            # Chat and upload endpoints
├── services/
│   ├── __init__.py
│   └── ai.py              # AI service integration
├── config/
│   ├── __init__.py
│   └── settings.py        # Application configuration
└── uploads/               # File upload directory (created automatically)
```

## 🛠 Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the backend directory with:
   ```env
   # App Configuration
   APP_NAME=IntelliAssist.AI
   DEBUG=true
   
   # API Keys (optional for testing)
   GROQ_API_KEY=your_groq_api_key_here
   HF_API_KEY=your_huggingface_api_key_here
   
   # File Upload
   MAX_FILE_SIZE=10485760  # 10MB
   UPLOAD_DIR=uploads
   ```

## 🚦 Running the Application

1. **Development mode**:
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Production mode**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/ping
- **API Documentation**: http://localhost:8000/docs (development only)
- **Alternative Docs**: http://localhost:8000/redoc (development only)

## 📚 API Endpoints

### Health & Status

- **GET** `/ping` - Health check
- **GET** `/` - Root endpoint with API info
- **GET** `/api/v1/status` - Detailed API status

### Chat & AI

- **POST** `/api/v1/chat` - Send message to AI
  ```json
  {
    "message": "Hello, how can you help me?",
    "context": "Optional conversation context"
  }
  ```

### File Upload

- **POST** `/api/v1/upload` - Upload files (images, audio, PDFs)
  - Form data with `file` field
  - Optional `description` field
  - Returns file info and processing status

- **GET** `/api/v1/files/{file_id}` - Get uploaded file info

## 🔧 Configuration

All configuration is managed in `config/settings.py` using Pydantic settings:

- **CORS Origins**: Configure allowed frontend URLs
- **File Upload**: Set max file size and allowed types
- **AI Models**: Configure Groq and Hugging Face settings
- **Logging**: Set log levels and formats

## 🤖 AI Integration

### Current Status (Placeholder Mode)
- Chat responses simulate actual AI interaction
- File processing returns placeholder results
- Ready for production API integration

### Future Integration

#### Groq API (LLaMA 3)
```python
# Uncomment in services/ai.py
from groq import Groq
client = Groq(api_key=settings.groq_api_key)
completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=1024
)
```

#### Hugging Face APIs
- **Image Analysis**: Vision transformers for image description
- **Audio Processing**: Whisper for speech-to-text
- **Document Processing**: OCR and text extraction

## 📝 Logging

The application logs to:
- **Console**: Colored output for development
- **File**: `intelliassist.log` for persistent logging

Log entries include:
- Request/response timing
- Error traces with full context
- API key usage (without exposing keys)
- File upload/processing events

## 🔒 Security Features

- **CORS Protection**: Restricted to configured origins
- **File Validation**: Type and size checking
- **Input Sanitization**: Pydantic model validation
- **Error Handling**: No sensitive data in error responses
- **File Upload Safety**: Unique naming and path validation

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/ping
```

### Chat API
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello IntelliAssist!"}'
```

### File Upload
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@example.jpg" \
  -F "description=Test image upload"
```

## 🔄 Integration with Frontend

The backend is configured to work with the React frontend:
- **CORS**: Allows requests from `http://localhost:5173`
- **JSON Responses**: Consistent format for easy frontend consumption
- **Error Handling**: User-friendly error messages
- **File Upload**: Compatible with FormData from frontend

## 📊 Monitoring

- **Health Endpoint**: `/ping` for load balancer checks
- **Status Endpoint**: `/api/v1/status` for detailed system info
- **Response Headers**: `X-Process-Time` for performance monitoring
- **Structured Logging**: JSON-compatible log format for analysis

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all `__init__.py` files exist
2. **Permission Errors**: Check upload directory permissions
3. **CORS Issues**: Verify frontend URL in settings
4. **File Upload Fails**: Check file size and type restrictions

### Debug Mode

Set `DEBUG=true` in environment to enable:
- Detailed error traces
- API documentation endpoints
- Auto-reload on code changes
- Verbose logging

## 🚀 Deployment

For production deployment:

1. Set `DEBUG=false`
2. Configure proper CORS origins
3. Set up environment variables
4. Use a production ASGI server (uvicorn, gunicorn)
5. Set up reverse proxy (nginx)
6. Configure logging aggregation
7. Set up monitoring and health checks

## 📋 Dependencies

- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Groq**: LLaMA 3 API client
- **Aiofiles**: Async file operations
- **Python-multipart**: File upload support
- **Pillow**: Image processing
- **HTTPX**: HTTP client for API calls

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper logging to new endpoints
3. Include error handling for all operations
4. Update this README for new features
5. Test with both development and production configs 