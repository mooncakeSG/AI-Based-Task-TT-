#!/usr/bin/env python3
"""
AI-Enhanced FastAPI backend for IntelliAssist
Supports chat, multimodal processing, file uploads, and task extraction
"""

import os
import logging
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import asyncio
import aiofiles
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="IntelliAssist AI Backend",
    version="2.0.0",
    description="AI-powered task management with multimodal capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
tasks_db = []
files_db = {}
conversations_db = []

# Pydantic models
class ChatMessage(BaseModel):
    message: Optional[str] = None
    image_file_id: Optional[str] = None
    audio_file_id: Optional[str] = None

class Task(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = "medium"
    category: str = "general"
    status: str = "pending"

# Utility functions
def extract_tasks_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract tasks from text using simple keyword matching"""
    tasks = []
    
    # Simple task extraction based on keywords
    task_indicators = [
        "need to", "have to", "must", "should", "todo", "to do",
        "task:", "action:", "reminder:", "deadline:", "due:",
        "schedule", "plan", "organize", "complete", "finish"
    ]
    
    sentences = text.lower().split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(indicator in sentence for indicator in task_indicators):
            # Extract priority
            priority = "medium"
            if any(word in sentence for word in ["urgent", "asap", "immediately", "critical"]):
                priority = "high"
            elif any(word in sentence for word in ["later", "sometime", "eventually", "optional"]):
                priority = "low"
            
            # Extract category
            category = "general"
            if any(word in sentence for word in ["meeting", "call", "presentation"]):
                category = "meetings"
            elif any(word in sentence for word in ["email", "message", "contact"]):
                category = "communication"
            elif any(word in sentence for word in ["research", "learn", "study"]):
                category = "learning"
            elif any(word in sentence for word in ["buy", "purchase", "order"]):
                category = "shopping"
            
            # Create task
            task = {
                "title": sentence[:50] + "..." if len(sentence) > 50 else sentence,
                "description": sentence,
                "priority": priority,
                "category": category,
                "status": "pending",
                "extracted": True,
                "source": "chat"
            }
            tasks.append(task)
    
    return tasks

def analyze_image_content(filename: str) -> Dict[str, Any]:
    """Simulate image analysis"""
    return {
        "description": f"Image analysis for {filename}",
        "objects_detected": ["document", "text", "workspace"],
        "text_extracted": "Sample extracted text from image",
        "suggestions": [
            "Review document content",
            "Extract action items from notes",
            "Organize workspace"
        ],
        "tasks": [
            {
                "title": "Review uploaded image content",
                "description": f"Analyze and process content from {filename}",
                "priority": "medium",
                "category": "review",
                "status": "pending"
            }
        ]
    }

def analyze_audio_content(filename: str) -> Dict[str, Any]:
    """Simulate audio transcription and analysis"""
    return {
        "transcription": "This is a simulated transcription of the audio file.",
        "sentiment": "neutral",
        "key_topics": ["meeting", "project", "deadline"],
        "suggestions": [
            "Follow up on meeting action items",
            "Schedule project review",
            "Set deadline reminders"
        ],
        "tasks": [
            {
                "title": "Follow up on audio notes",
                "description": f"Process action items from {filename}",
                "priority": "high",
                "category": "meetings",
                "status": "pending"
            }
        ]
    }

def analyze_document_content(filename: str) -> Dict[str, Any]:
    """Simulate document analysis"""
    return {
        "content_summary": f"Document analysis for {filename}",
        "key_points": ["Important information", "Action items", "Deadlines"],
        "suggestions": [
            "Create tasks from document",
            "Set reminders for deadlines",
            "Share with team members"
        ],
        "tasks": [
            {
                "title": "Process document content",
                "description": f"Review and extract tasks from {filename}",
                "priority": "medium",
                "category": "documents",
                "status": "pending"
            }
        ]
    }

def generate_ai_response(message: str, context: Dict[str, Any] = None) -> str:
    """Generate AI response based on message and context"""
    
    if not message and not context:
        return "I'm here to help! You can ask me questions, upload files for analysis, or let me help you organize your tasks."
    
    # Simple response generation based on keywords
    message_lower = message.lower() if message else ""
    
    if any(word in message_lower for word in ["hello", "hi", "hey"]):
        return "Hello! I'm IntelliAssist.AI. I can help you manage tasks, analyze files, and organize your work. What would you like to do today?"
    
    elif any(word in message_lower for word in ["task", "todo", "organize"]):
        return "I can help you create and organize tasks! You can tell me what you need to do, or upload files like images, documents, or audio recordings, and I'll extract actionable tasks for you."
    
    elif any(word in message_lower for word in ["upload", "file", "image", "document"]):
        return "Great! I can analyze various file types:\n• Images: Extract text and identify tasks\n• Audio: Transcribe speech and find action items\n• Documents: Analyze content and suggest tasks\n\nJust upload your file and I'll process it for you!"
    
    elif any(word in message_lower for word in ["help", "what", "how"]):
        return "I'm your AI assistant for task management! Here's what I can do:\n\n📝 Task Management: Create, organize, and track tasks\n🖼️ Image Analysis: Extract text and tasks from images\n🎵 Audio Processing: Transcribe voice notes and meetings\n📄 Document Analysis: Process PDFs and text files\n💬 Smart Chat: Natural conversation about your work\n\nHow can I help you be more productive today?"
    
    else:
        # Extract tasks from the message
        tasks = extract_tasks_from_text(message)
        
        if tasks:
            task_summary = f"I found {len(tasks)} potential task(s) in your message! "
            return f"{task_summary}I can help you organize these into your task list. Would you like me to save them?"
        else:
            return f"I understand you're telling me about: '{message}'. How can I help you turn this into actionable tasks or organize your work better?"

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "IntelliAssist AI Backend",
        "version": "2.0.0",
        "features": ["chat", "multimodal", "file_upload", "task_extraction"],
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_features": "enabled",
        "timestamp": time.time()
    }

# Chat endpoints
@app.post("/api/v1/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """Enhanced chat with AI processing"""
    try:
        logger.info(f"Chat request: {chat_data}")
        
        context = {}
        
        # Process attached files if any
        if chat_data.image_file_id and chat_data.image_file_id in files_db:
            file_info = files_db[chat_data.image_file_id]
            context["image"] = analyze_image_content(file_info["filename"])
            
        if chat_data.audio_file_id and chat_data.audio_file_id in files_db:
            file_info = files_db[chat_data.audio_file_id]
            context["audio"] = analyze_audio_content(file_info["filename"])
        
        # Generate AI response
        ai_response = generate_ai_response(chat_data.message, context)
        
        # Extract tasks from message
        tasks = []
        if chat_data.message:
            tasks = extract_tasks_from_text(chat_data.message)
        
        # Add tasks from file analysis
        if context.get("image", {}).get("tasks"):
            tasks.extend(context["image"]["tasks"])
        if context.get("audio", {}).get("tasks"):
            tasks.extend(context["audio"]["tasks"])
        
        # Store conversation
        conversation = {
            "id": len(conversations_db) + 1,
            "message": chat_data.message,
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "tasks_extracted": len(tasks),
            "context": context
        }
        conversations_db.append(conversation)
        
        return {
            "response": ai_response,
            "tasks": tasks,
            "context": context,
            "conversation_id": conversation["id"],
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/api/v1/multimodal")
async def multimodal_endpoint(request: Request):
    """Multimodal processing endpoint"""
    try:
        # Parse form data manually to handle mixed content
        form = await request.form()
        
        message = form.get("message", "")
        image_file_id = form.get("image_file_id")
        audio_file_id = form.get("audio_file_id")
        
        logger.info(f"Multimodal request - message: {message}, image: {image_file_id}, audio: {audio_file_id}")
        
        context = {}
        all_tasks = []
        
        # Process image if provided
        if image_file_id and image_file_id in files_db:
            file_info = files_db[image_file_id]
            image_analysis = analyze_image_content(file_info["filename"])
            context["image"] = image_analysis
            all_tasks.extend(image_analysis.get("tasks", []))
        
        # Process audio if provided
        if audio_file_id and audio_file_id in files_db:
            file_info = files_db[audio_file_id]
            audio_analysis = analyze_audio_content(file_info["filename"])
            context["audio"] = audio_analysis
            all_tasks.extend(audio_analysis.get("tasks", []))
        
        # Process text message
        if message:
            text_tasks = extract_tasks_from_text(message)
            all_tasks.extend(text_tasks)
        
        # Generate comprehensive AI response
        response_parts = []
        
        if context.get("image"):
            response_parts.append(f"📸 Image Analysis: {context['image']['description']}")
            
        if context.get("audio"):
            response_parts.append(f"🎵 Audio Transcription: {context['audio']['transcription']}")
            
        if message:
            response_parts.append(f"💬 Your message: {message}")
        
        if all_tasks:
            response_parts.append(f"✅ I found {len(all_tasks)} actionable task(s) from your input!")
        
        ai_response = "\n\n".join(response_parts) if response_parts else "I've processed your multimodal input successfully!"
        
        return {
            "response": ai_response,
            "tasks": all_tasks,
            "analysis": context,
            "processing_summary": {
                "text_processed": bool(message),
                "image_processed": bool(context.get("image")),
                "audio_processed": bool(context.get("audio")),
                "tasks_found": len(all_tasks)
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Multimodal processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Multimodal processing failed: {str(e)}")

# File upload endpoints
@app.post("/api/v1/upload")
async def upload_file_endpoint(file: UploadFile = File(...)):
    """File upload and analysis"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save file
        file_id = f"file_{int(time.time())}_{file.filename}"
        file_path = UPLOAD_DIR / file_id
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Store file info
        file_info = {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "path": str(file_path),
            "uploaded_at": datetime.now().isoformat()
        }
        files_db[file_id] = file_info
        
        # Analyze file based on type
        analysis = {}
        if file.content_type and file.content_type.startswith("image/"):
            analysis = analyze_image_content(file.filename)
        elif file.content_type and file.content_type.startswith("audio/"):
            analysis = analyze_audio_content(file.filename)
        else:
            analysis = analyze_document_content(file.filename)
        
        response_message = f"File '{file.filename}' uploaded and analyzed successfully!"
        
        return {
            "message": response_message,
            "response": response_message,
            "file_id": file_id,
            "file_info": file_info,
            "processing_details": {
                "file_analysis": analysis,
                "processing_time": "1.2s",
                "ai_insights_enabled": True
            },
            "tasks": analysis.get("tasks", []),
            "suggestions": analysis.get("suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/v1/upload/audio")
async def upload_audio_endpoint(file: UploadFile = File(...)):
    """Audio upload and transcription"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Save audio file
        file_id = f"audio_{int(time.time())}_{file.filename}"
        file_path = UPLOAD_DIR / file_id
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Store file info
        file_info = {
            "id": file_id,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "path": str(file_path),
            "uploaded_at": datetime.now().isoformat()
        }
        files_db[file_id] = file_info
        
        # Analyze audio
        audio_analysis = analyze_audio_content(file.filename)
        
        return {
            "transcription": audio_analysis["transcription"],
            "file_id": file_id,
            "analysis": audio_analysis,
            "tasks": audio_analysis.get("tasks", []),
            "processing_time": "2.1s"
        }
        
    except Exception as e:
        logger.error(f"Audio upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(e)}")

# Task management endpoints
@app.get("/api/v1/tasks")
def get_tasks():
    """Get all tasks"""
    return {
        "tasks": tasks_db,
        "count": len(tasks_db),
        "status": "success"
    }

@app.post("/api/v1/tasks")
async def create_task(task: Task):
    """Create a new task"""
    try:
        new_task = {
            "id": len(tasks_db) + 1,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "category": task.category,
            "status": task.status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        tasks_db.append(new_task)
        
        return {
            "task": new_task,
            "message": "Task created successfully",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Task creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")

@app.put("/api/v1/tasks/{task_id}")
async def update_task(task_id: int, task_updates: Dict[str, Any]):
    """Update a task"""
    try:
        # Find task
        task_index = None
        for i, task in enumerate(tasks_db):
            if task["id"] == task_id:
                task_index = i
                break
        
        if task_index is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task
        tasks_db[task_index].update(task_updates)
        tasks_db[task_index]["updated_at"] = datetime.now().isoformat()
        
        return {
            "task": tasks_db[task_index],
            "message": "Task updated successfully",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Task update error: {e}")
        raise HTTPException(status_code=500, detail=f"Task update failed: {str(e)}")

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task"""
    try:
        # Find and remove task
        task_index = None
        for i, task in enumerate(tasks_db):
            if task["id"] == task_id:
                task_index = i
                break
        
        if task_index is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        deleted_task = tasks_db.pop(task_index)
        
        return {
            "message": "Task deleted successfully",
            "deleted_task": deleted_task,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Task deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Task deletion failed: {str(e)}")

@app.delete("/api/v1/tasks")
async def clear_all_tasks():
    """Clear all tasks"""
    try:
        count = len(tasks_db)
        tasks_db.clear()
        
        return {
            "message": f"Cleared {count} tasks successfully",
            "deleted_count": count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Clear tasks error: {e}")
        raise HTTPException(status_code=500, detail=f"Clear tasks failed: {str(e)}")

# Debug and monitoring endpoints
@app.get("/api/v1/status")
def get_status():
    """Get system status"""
    return {
        "status": "operational",
        "ai_features": "enabled",
        "tasks_count": len(tasks_db),
        "files_count": len(files_db),
        "conversations_count": len(conversations_db),
        "uptime": "running",
        "version": "2.0.0"
    }

@app.get("/api/v1/files")
def get_files():
    """Get uploaded files"""
    return {
        "files": list(files_db.values()),
        "count": len(files_db)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 