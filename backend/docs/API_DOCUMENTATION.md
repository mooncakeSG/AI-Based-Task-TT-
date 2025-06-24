# IntelliAssist.AI API Documentation

## Overview

IntelliAssist.AI is a comprehensive AI-powered task management application that integrates multiple AI technologies including natural language processing, speech recognition, and computer vision.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses API key-based authentication for external AI services:

- **Groq API**: Requires `GROQ_API_KEY` environment variable
- **HuggingFace**: Requires `HF_API_KEY` environment variable  
- **Supabase**: Requires `SUPABASE_URL` and `SUPABASE_ANON_KEY` environment variables

## Rate Limiting

The API implements intelligent rate limiting:

- **Groq API**: 30 requests per minute
- **HuggingFace API**: 1000 requests per minute
- **Supabase**: 1000 requests per minute

Rate limit status monitored via `/api/v1/monitoring/rate-limits`

## Core Endpoints

### Health & Status

#### GET `/ping`
Basic health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "app": "IntelliAssist.AI",
  "version": "1.0.0",
  "timestamp": 1703123456.789
}
```

### Chat & AI Interaction

#### POST `/api/v1/chat`
Process text messages with AI task extraction.

**Request:**
```json
{
  "message": "I need to buy groceries and call my mom tomorrow",
  "context": "daily_planning"
}
```

**Response:**
```json
{
  "response": "I can help you organize those tasks!",
  "model": "llama3-8b-8192", 
  "response_time": 2.34,
  "tokens_used": 156,
  "status": "success",
  "tasks": [
    {
      "title": "Buy groceries",
      "summary": "Purchase groceries for the week",
      "priority": "medium",
      "category": "personal", 
      "status": "pending"
    }
  ]
}
```

#### POST `/api/v1/multimodal`
Process multimodal input (text, image, audio).

#### POST `/api/v1/upload/audio`
Upload and transcribe audio files (WAV, MP3, WebM).

**File Requirements:**
- Max size: 5MB
- Supported: WAV, MP3, WebM, OGG
- Returns transcription + AI analysis

### Task Management

#### GET `/api/v1/tasks`
Retrieve all tasks with optional filtering.

#### POST `/api/v1/tasks`
Create new task.

#### PUT `/api/v1/tasks/{task_id}`
Update existing task.

#### DELETE `/api/v1/tasks/{task_id}`
Delete task.

## Monitoring & Analytics

### GET `/api/v1/monitoring/health`
System health status with service metrics.

### GET `/api/v1/monitoring/dashboard`
Comprehensive monitoring dashboard.

### GET `/api/v1/monitoring/metrics?minutes=60`
Recent API metrics and performance data.

### GET `/api/v1/monitoring/service/{service_name}`
Individual service health (groq, huggingface, supabase).

## Error Handling

Consistent error format:

```json
{
  "error": "Error Type",
  "message": "Human-readable description",
  "status_code": 400,
  "details": {}
}
```

**Common Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Python SDK Example

```python
import requests

class IntelliAssistClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def chat(self, message, context=None):
        """Send chat message and get AI response with tasks"""
        url = f"{self.base_url}/api/v1/chat"
        payload = {"message": message}
        if context:
            payload["context"] = context
            
        response = requests.post(url, json=payload)
        return response.json()
    
    def upload_audio(self, file_path):
        """Upload audio file for transcription"""
        url = f"{self.base_url}/api/v1/upload/audio"
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        return response.json()
    
    def get_system_health(self):
        """Check system health and monitoring"""
        url = f"{self.base_url}/api/v1/monitoring/health"
        response = requests.get(url)
        return response.json()

# Usage
client = IntelliAssistClient()

# Chat interaction
result = client.chat("I need to organize my schedule for next week")
print(f"AI Response: {result['response']}")

# Check extracted tasks
if result['tasks']:
    print("Extracted Tasks:")
    for task in result['tasks']:
        print(f"- {task['summary']} ({task['priority']})")

# Upload audio
audio_result = client.upload_audio("recording.wav")
print(f"Transcription: {audio_result['processing_details']['transcription']['text']}")

# Monitor system health
health = client.get_system_health()
print(f"System Status: {health['health']}")
```

## JavaScript Example

```javascript
class IntelliAssistClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message, context = null) {
        const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, context })
        });
        return response.json();
    }
    
    async uploadAudio(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/api/v1/upload/audio`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }
    
    async getSystemHealth() {
        const response = await fetch(`${this.baseUrl}/api/v1/monitoring/health`);
        return response.json();
    }
}

// Usage
const client = new IntelliAssistClient();

// Chat interaction
client.chat("Help me plan my day tomorrow").then(result => {
    console.log('AI Response:', result.response);
    if (result.tasks.length > 0) {
        console.log('Extracted Tasks:');
        result.tasks.forEach(task => {
            console.log(`- ${task.summary} (${task.priority})`);
        });
    }
});
```

## Performance Features

### Monitoring & Metrics
- Real-time API performance tracking
- Service health monitoring
- Rate limit management
- Error rate tracking
- Response time analytics

### Scalability
- Async request processing
- Connection pooling
- Intelligent rate limiting
- Error recovery mechanisms
- Performance logging

## Security Features

### Input Validation
- File type validation
- Size limits (5MB)
- Content sanitization
- SQL injection prevention
- XSS protection

### API Security
- Rate limiting
- CORS configuration
- Error message sanitization
- Secure file upload handling

## Deployment Notes

### Required Environment Variables
```env
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_huggingface_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
DEBUG=false
LOG_LEVEL=INFO
```

### Production Considerations
- Configure CORS origins
- Set up SSL/TLS
- Implement caching
- Monitor rate limits
- Set up log aggregation
- Configure backup strategies

## Support & Troubleshooting

### Health Checks
1. `/ping` - Basic connectivity
2. `/api/v1/monitoring/health` - System health
3. `/api/v1/monitoring/dashboard` - Detailed metrics

### Common Issues
- **503 Service Unavailable**: Check API key configuration
- **429 Rate Limited**: Monitor `/api/v1/monitoring/rate-limits`
- **422 Validation Error**: Check request format
- **500 Server Error**: Review logs and monitoring dashboard

### Performance Optimization
- Use connection pooling
- Implement response caching
- Monitor service health
- Optimize file upload sizes
- Use appropriate rate limits
