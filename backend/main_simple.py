import logging
import sys
import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IntelliAssist.AI",
    version="1.0.0",
    description="AI-powered task assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://intelliassist-frontend-9pniapdi0-mooncakesgs-projects.vercel.app",
    "https://intelliassist-frontend-mjr0irfwc-mooncakesgs-projects.vercel.app",
    "https://*.vercel.app",
    "https://*.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models
class TaskModel(BaseModel):
    id: Optional[int] = None
    summary: str
    description: Optional[str] = None
    category: str = "general"
    priority: str = "medium"
    status: str = "pending"
    user_id: Optional[str] = None

class TasksResponse(BaseModel):
    tasks: List[TaskModel]
    count: int
    status: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str
    timestamp: float

# In-memory storage for testing
tasks_storage: List[Dict[str, Any]] = []

# Health check routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to IntelliAssist.AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "ping": "/ping",
            "tasks": "/api/v1/tasks",
            "chat": "/api/v1/chat",
            "test": "/api/v1/test"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for Render"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "app": "IntelliAssist.AI",
        "version": "1.0.0"
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": time.time()
    }

# API v1 routes
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "endpoints_available": [
            "/api/v1/test",
            "/api/v1/tasks",
            "/api/v1/chat"
        ],
        "cors_origins": CORS_ORIGINS,
        "timestamp": time.time()
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "status": "success",
        "message": "API connection working perfectly!",
        "timestamp": time.time(),
        "cors_enabled": True
    }

@app.get("/api/v1/tasks", response_model=TasksResponse)
async def get_tasks():
    """Get all tasks"""
    logger.info(f"GET /api/v1/tasks called - returning {len(tasks_storage)} tasks")
    
    return TasksResponse(
        tasks=[TaskModel(**task) for task in tasks_storage],
        count=len(tasks_storage),
        status="success"
    )

@app.post("/api/v1/tasks", response_model=TaskModel)
async def create_task(task: TaskModel):
    """Create a new task"""
    logger.info(f"POST /api/v1/tasks called - creating task: {task.summary}")
    
    # Generate ID
    task_id = len(tasks_storage) + 1
    task_data = task.model_dump()
    task_data["id"] = task_id
    
    tasks_storage.append(task_data)
    
    return TaskModel(**task_data)

@app.delete("/api/v1/tasks")
async def clear_tasks():
    """Clear all tasks"""
    logger.info("DELETE /api/v1/tasks called - clearing all tasks")
    
    count = len(tasks_storage)
    tasks_storage.clear()
    
    return {
        "message": f"Cleared {count} tasks",
        "status": "success"
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Simple chat endpoint"""
    logger.info(f"POST /api/v1/chat called - message: {request.message[:50]}...")
    
    # Simple echo response for testing
    response = f"Echo: {request.message}"
    
    return ChatResponse(
        response=response,
        status="success",
        timestamp=time.time()
    )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

logger.info("FastAPI app initialized successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 