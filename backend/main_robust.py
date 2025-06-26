# Version 3.5 - Standard Starlette CORSMiddleware with proper configuration
import logging
import sys
import time
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.info("🚀 Starting IntelliAssist.AI backend v2 with CORS fixes...")

# ========================================
# 🔒 SAFE ENVIRONMENT VARIABLE LOADING
# ========================================

class EnvConfig:
    """Safe environment variable configuration"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Load and validate environment variables
        self.PORT = int(os.getenv("PORT", "8000"))
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = self.ENVIRONMENT != "production"
        
        # Database/Supabase (optional for now)
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
        self.SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
        
        # AI Services (optional for now)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.HF_API_KEY = os.getenv("HF_API_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        # CORS origins (explicit domains work better than wildcards)
        self.CORS_ORIGINS = [
            "https://intelliassist-frontend-idaidfoq4-mooncakesgs-projects.vercel.app",
            "https://intelliassist-frontend-9pniapdi0-mooncakesgs-projects.vercel.app",
            "https://intelliassist-frontend-mjr0irfwc-mooncakesgs-projects.vercel.app",
            "https://intelliassist-frontend-git-main-mooncakesgs-projects.vercel.app",
            "https://intelliassist-frontend-mooncakesgs-projects.vercel.app"
        ]
        
        # Add development origins in non-production environments
        if self.ENVIRONMENT != "production":
            self.CORS_ORIGINS.extend([
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ])
        
        # Validate critical environment variables
        self._validate_env_vars()
    
    def _validate_env_vars(self):
        """Validate environment variables and log issues"""
        
        # Check database configuration
        if not self.SUPABASE_URL or not self.SUPABASE_ANON_KEY:
            self.warnings.append("Supabase not configured - database features disabled")
        
        # Check AI services
        if not self.GROQ_API_KEY and not self.OPENAI_API_KEY and not self.HF_API_KEY:
            self.warnings.append("No AI API keys configured - AI features disabled")
        
        # Log results
        if self.errors:
            for error in self.errors:
                logger.error(f"⚠️ ENV ERROR: {error}")
        
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"⚠️ ENV WARNING: {warning}")
        
        logger.info(f"✅ Environment: {self.ENVIRONMENT}")
        logger.info(f"✅ Port: {self.PORT}")
        logger.info(f"✅ Debug: {self.DEBUG}")
    
    @property
    def has_database(self) -> bool:
        """Check if database is configured"""
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)
    
    @property
    def has_ai_services(self) -> bool:
        """Check if AI services are configured"""
        return bool(self.GROQ_API_KEY or self.OPENAI_API_KEY or self.HF_API_KEY)

# Initialize configuration safely
try:
    config = EnvConfig()
    logger.info("✅ Configuration loaded successfully")
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to load configuration: {e}")
    sys.exit(1)

# ========================================
# 🌐 SERVICES INITIALIZATION (OPTIONAL)
# ========================================

class ServiceManager:
    """Manages optional services"""
    
    def __init__(self):
        self.supabase = None
        self.ai_service = None
        self.services_loaded = {
            'database': False,
            'ai': False
        }
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize services if configuration is available"""
        
        # Initialize database service
        if config.has_database:
            try:
                logger.info("🔄 Initializing database service...")
                # We'll add this later
                self.services_loaded['database'] = True
                logger.info("✅ Database service initialized")
            except Exception as e:
                logger.error(f"❌ Database service failed: {e}")
        
        # Initialize AI service
        if config.has_ai_services:
            try:
                logger.info("🔄 Initializing AI service...")
                # We'll add this later
                self.services_loaded['ai'] = True
                logger.info("✅ AI service initialized")
            except Exception as e:
                logger.error(f"❌ AI service failed: {e}")

# Initialize service manager
service_manager = ServiceManager()

# ========================================
# 📊 DATA MODELS
# ========================================

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
    database_connected: bool

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str
    timestamp: float
    ai_service_used: Optional[str] = None

# In-memory storage (will be replaced with database)
tasks_storage: List[Dict[str, Any]] = []

# ========================================
# 🚀 FASTAPI APPLICATION
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Application starting up...")
    logger.info(f"📊 Services loaded: {service_manager.services_loaded}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")

# Create FastAPI app
app = FastAPI(
    title="IntelliAssist.AI",
    version="1.0.0",
    description="AI-powered task assistant with multimodal capabilities",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=lifespan
)

# ✅ CORS Middleware - Added FIRST before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
    max_age=86400  # Cache preflight for 24h
)

# ✅ Request logging middleware AFTER CORS
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    origin = request.headers.get("origin", "No origin")
    logger.info(f"📥 {request.method} {request.url.path} - Origin: {origin}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"📤 {response.status_code} - {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Request failed: {e} - {process_time:.3f}s")
        raise

# ========================================
# 🏥 HEALTH & STATUS ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Welcome to IntelliAssist.AI API",
        "version": "1.0.0",
        "status": "operational",
        "environment": config.ENVIRONMENT,
        "services": service_manager.services_loaded,
        "endpoints": {
            "health": "/health",
            "ping": "/ping",
            "debug": "/debug",
            "api_status": "/api/v1/status",
            "tasks": "/api/v1/tasks",
            "chat": "/api/v1/chat"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for Render"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "app": "IntelliAssist.AI",
        "version": "1.0.0",
        "services": service_manager.services_loaded
    }

@app.get("/ping")
async def ping():
    """Simple ping test"""
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": time.time()
    }

@app.get("/debug")
async def debug_info():
    """Debug information"""
    return {
        "environment": config.ENVIRONMENT,
        "debug_mode": config.DEBUG,
        "port": config.PORT,
        "services_loaded": service_manager.services_loaded,
        "cors_origins": config.CORS_ORIGINS,
        "environment_vars": {
            "supabase_configured": config.has_database,
            "ai_services_configured": config.has_ai_services,
            "supabase_url_set": bool(config.SUPABASE_URL),
            "groq_key_set": bool(config.GROQ_API_KEY),
            "hf_key_set": bool(config.HF_API_KEY),
            "openai_key_set": bool(config.OPENAI_API_KEY)
        }
    }

# ========================================
# 📋 API V1 ENDPOINTS
# ========================================

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": time.time(),
        "services": service_manager.services_loaded,
        "database_connected": service_manager.services_loaded['database'],
        "ai_services_available": service_manager.services_loaded['ai']
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """API connection test"""
    return {
        "status": "success",
        "message": "API connection working perfectly!",
        "timestamp": time.time(),
        "cors_enabled": True,
        "services": service_manager.services_loaded
    }

@app.get("/api/v1/tasks", response_model=TasksResponse)
async def get_tasks():
    """Get all tasks"""
    logger.info(f"📋 GET /api/v1/tasks - returning {len(tasks_storage)} tasks")
    
    return TasksResponse(
        tasks=[TaskModel(**task) for task in tasks_storage],
        count=len(tasks_storage),
        status="success",
        database_connected=service_manager.services_loaded['database']
    )

@app.post("/api/v1/tasks", response_model=TaskModel)
async def create_task(task: TaskModel):
    """Create a new task"""
    logger.info(f"📋 POST /api/v1/tasks - creating: {task.summary}")
    
    # Generate ID
    task_id = len(tasks_storage) + 1
    task_data = task.model_dump()
    task_data["id"] = task_id
    
    tasks_storage.append(task_data)
    logger.info(f"✅ Task created with ID: {task_id}")
    
    return TaskModel(**task_data)

@app.delete("/api/v1/tasks")
async def clear_tasks():
    """Clear all tasks"""
    count = len(tasks_storage)
    tasks_storage.clear()
    logger.info(f"🗑️ Cleared {count} tasks")
    
    return {
        "message": f"Cleared {count} tasks",
        "status": "success"
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint with AI integration"""
    logger.info(f"💬 POST /api/v1/chat - message: {request.message[:50]}...")
    
    # For now, simple echo (will be replaced with AI service)
    if service_manager.services_loaded['ai']:
        response = f"AI Response: {request.message}"
        ai_service_used = "mock_ai_service"
    else:
        response = f"Echo (AI not configured): {request.message}"
        ai_service_used = None
    
    return ChatResponse(
        response=response,
        status="success",
        timestamp=time.time(),
        ai_service_used=ai_service_used
    )

# ✅ OPTIONS Route Backup (Failsafe) - Catch-all for any missed preflight requests
@app.options("/{full_path:path}")
async def preflight_handler():
    """Universal OPTIONS handler for CORS preflight"""
    return JSONResponse(status_code=200, content={"message": "CORS preflight OK"})

logger.info("✅ FastAPI application setup complete")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting server on port {config.PORT}")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT) 