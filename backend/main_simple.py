#!/usr/bin/env python3
"""
Ultra-minimal FastAPI app with bulletproof CORS
This is to test if our complex setup is causing the CORS issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="IntelliAssist Simple", version="1.0.0")

# Bulletproof CORS - Allow everything for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "IntelliAssist Simple API", "status": "working"}

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "cors": "enabled"}

@app.get("/api/v1/tasks")
def get_tasks():
    """Get tasks - minimal implementation"""
    logger.info("GET /api/v1/tasks called")
    return {
        "tasks": [],
        "count": 0,
        "status": "success"
    }

@app.post("/api/v1/tasks")
def create_task():
    """Create task - minimal implementation"""
    logger.info("POST /api/v1/tasks called")
    return {
        "id": 2,
        "summary": "New task",
        "status": "pending"
    }

@app.get("/api/v1/chat")
def chat():
    """Chat endpoint - minimal implementation"""
    logger.info("GET /api/v1/chat called")
    return {
        "response": "Hello from simple API",
        "status": "success",
        "timestamp": 1234567890
    }

@app.post("/api/v1/chat")
def chat_post():
    """Chat POST - minimal implementation"""
    logger.info("POST /api/v1/chat called")
    return {
        "response": "Message received",
        "status": "success",
        "timestamp": 1234567890
    }

# Explicit OPTIONS handlers as backup
@app.options("/{path:path}")
def options_handler():
    """Universal OPTIONS handler"""
    logger.info("OPTIONS request received")
    return JSONResponse(
        status_code=200,
        content={"message": "OPTIONS OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 