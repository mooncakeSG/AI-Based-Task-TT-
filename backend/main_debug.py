import logging
import time
import sys
import traceback
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting application...")

# Test imports step by step
try:
    logger.info("Importing config settings...")
    from config.settings import settings, get_cors_origins, get_allowed_file_types
    logger.info(f"Config loaded successfully. Debug: {settings.debug}, Port: {settings.api_port}")
except Exception as e:
    logger.error(f"Failed to import config: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test service imports
services_loaded = {}

try:
    logger.info("Importing AI service...")
    from services.ai import ai_service
    services_loaded['ai'] = True
    logger.info("AI service imported successfully")
except Exception as e:
    logger.error(f"Failed to import AI service: {e}")
    services_loaded['ai'] = False
    traceback.print_exc()

try:
    logger.info("Importing database service...")
    from services.postgres_db import database_service
    services_loaded['database'] = True
    logger.info("Database service imported successfully")
except Exception as e:
    logger.error(f"Failed to import database service: {e}")
    services_loaded['database'] = False
    traceback.print_exc()

try:
    logger.info("Importing auth service...")
    from services.auth import auth_service, get_current_user, require_auth
    services_loaded['auth'] = True
    logger.info("Auth service imported successfully")
except Exception as e:
    logger.error(f"Failed to import auth service: {e}")
    services_loaded['auth'] = False
    traceback.print_exc()

# Test route imports
routers_loaded = {}

try:
    logger.info("Importing auth router...")
    from routes.auth import router as auth_router
    routers_loaded['auth'] = True
    logger.info("Auth router imported successfully")
except Exception as e:
    logger.error(f"Failed to import auth router: {e}")
    routers_loaded['auth'] = False
    traceback.print_exc()

try:
    logger.info("Importing chat router...")
    from routes.chat import router as chat_router
    routers_loaded['chat'] = True
    logger.info("Chat router imported successfully")
except Exception as e:
    logger.error(f"Failed to import chat router: {e}")
    routers_loaded['chat'] = False
    traceback.print_exc()

try:
    logger.info("Importing monitoring router...")
    from routes.monitoring import router as monitoring_router
    routers_loaded['monitoring'] = True
    logger.info("Monitoring router imported successfully")
except Exception as e:
    logger.error(f"Failed to import monitoring router: {e}")
    routers_loaded['monitoring'] = False
    traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Services loaded: {services_loaded}")
    logger.info(f"Routers loaded: {routers_loaded}")
    logger.info(f"CORS origins: {get_cors_origins()}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered task assistant with multimodal capabilities (Debug Mode)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and response times"""
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"- Error: {str(e)} - Time: {process_time:.3f}s",
            exc_info=True
        )
        raise

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with friendly messages"""
    logger.warning(f"Validation error for {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request data is invalid",
            "details": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    logger.warning(f"HTTP exception for {request.url.path}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected error for {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

# Health check routes
@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time(),
        "services_loaded": services_loaded,
        "routers_loaded": routers_loaded
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name} API (Debug Mode)",
        "version": settings.app_version,
        "services_loaded": services_loaded,
        "routers_loaded": routers_loaded,
        "docs": "/docs",
        "health": "/ping"
    }

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Debug information endpoint"""
    return {
        "services_loaded": services_loaded,
        "routers_loaded": routers_loaded,
        "cors_origins": get_cors_origins(),
        "debug_mode": settings.debug,
        "environment_vars": {
            "supabase_url": bool(settings.supabase_url),
            "supabase_anon_key": bool(settings.supabase_anon_key),
            "groq_api_key": bool(settings.groq_api_key),
            "hf_api_key": bool(settings.hf_api_key)
        }
    }

# Include routers conditionally
if routers_loaded.get('auth'):
    logger.info("Including auth router...")
    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    logger.info("Auth router included successfully")

if routers_loaded.get('chat'):
    logger.info("Including chat router...")
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat & Upload"])
    logger.info("Chat router included successfully")

if routers_loaded.get('monitoring'):
    logger.info("Including monitoring router...")
    app.include_router(monitoring_router, tags=["Monitoring"])
    logger.info("Monitoring router included successfully")

# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """Get API status and configuration"""
    return {
        "status": "operational",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug_mode": settings.debug,
        "cors_origins": get_cors_origins(),
        "services_loaded": services_loaded,
        "routers_loaded": routers_loaded,
        "max_file_size_mb": settings.max_file_size // (1024 * 1024) if hasattr(settings, 'max_file_size') else "unknown",
        "allowed_file_types": get_allowed_file_types() if callable(get_allowed_file_types) else "unknown",
        "groq_model": settings.groq_model if hasattr(settings, 'groq_model') else "unknown",
        "upload_dir": settings.upload_dir if hasattr(settings, 'upload_dir') else "unknown"
    }

# Conditional health endpoints
if services_loaded.get('ai'):
    @app.get("/api/v1/ai/health")
    async def ai_health():
        """Check AI service health"""
        try:
            health_status = await ai_service.health_check()
            return {
                "timestamp": time.time(),
                "ai_services": health_status
            }
        except Exception as e:
            logger.error(f"AI health check failed: {str(e)}", exc_info=True)
            return {
                "timestamp": time.time(),
                "ai_services": {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}"
                }
            }

if services_loaded.get('database'):
    @app.get("/api/v1/database/health")
    async def database_health():
        """Check database connection health"""
        try:
            health_status = await database_service.health_check()
            return {
                "timestamp": time.time(),
                "database": health_status
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}", exc_info=True)
            return {
                "timestamp": time.time(),
                "database": {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}"
                }
            }

logger.info("Application setup complete")

if __name__ == "__main__":
    # Run the application
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "main_debug:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level.lower() if hasattr(settings, 'log_level') else "info"
    ) 