import logging
import time
import os
import aiofiles
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from services.ai import ai_service
from services.postgres_db import database_service
from config.settings import settings, get_allowed_file_types

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[str] = Field(None, description="Optional conversation context")
    user_id: Optional[str] = Field(None, description="Optional user ID for personalization")

class ChatResponse(BaseModel):
    response: str
    model: str
    response_time: float
    tokens_used: int
    status: str
    timestamp: float
    tasks: Optional[List[Dict[str, Any]]] = []

class TaskModel(BaseModel):
    id: Optional[int] = None
    summary: str
    category: Optional[str] = "general"
    priority: Optional[str] = "medium"
    status: Optional[str] = "pending"
    user_id: Optional[str] = None
    created_at: Optional[float] = None
    updated_at: Optional[float] = None

class TasksResponse(BaseModel):
    tasks: List[TaskModel]
    count: int
    status: str

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    upload_path: str
    status: str
    message: str
    file_id: str

class MultimodalRequest(BaseModel):
    message: Optional[str] = Field(None, description="Text message")
    image_file_id: Optional[str] = Field(None, description="Image file ID from upload")
    audio_file_id: Optional[str] = Field(None, description="Audio file ID from upload")
    context: Optional[str] = Field(None, description="Conversation context")
    task_type: Optional[str] = Field("general", description="Type of analysis for images")
    user_id: Optional[str] = Field(None, description="Optional user ID")

class MultimodalResponse(BaseModel):
    response: str
    processing_details: Dict[str, Any]
    inputs_processed: List[str]
    model_info: Dict[str, Any]
    status: str
    timestamp: float

@router.get("/tasks", response_model=TasksResponse)
async def get_tasks(user_id: Optional[str] = None):
    """
    Get all saved tasks
    
    Args:
        user_id (str, optional): Filter tasks by user ID
        
    Returns:
        TasksResponse: List of tasks with metadata
    """
    try:
        logger.info(f"Fetching tasks for user: {user_id or 'all users'}")
        
        # Use Supabase database service
        tasks_data = await database_service.get_tasks(user_id)
        
        # Convert to TaskModel objects
        tasks = [TaskModel(**task) for task in tasks_data]
        
        return TasksResponse(
            tasks=tasks,
            count=len(tasks),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch tasks",
                "message": "Unable to retrieve tasks. Please try again later."
            }
        )

@router.post("/tasks", response_model=TaskModel)
async def create_task(task: TaskModel):
    """
    Create a new task
    
    Args:
        task (TaskModel): Task data
        
    Returns:
        TaskModel: Created task with ID
    """
    try:
        logger.info(f"Creating task: {task.summary[:50]}...")
        
        # Convert to dict for database
        task_data = task.model_dump(exclude_none=True)
        
        # Use Supabase database service
        created_task = await database_service.create_task(task_data)
        
        if created_task:
            return TaskModel(**created_task)
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to create task",
                    "message": "Task creation failed. Please try again."
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create task",
                "message": "Unable to create task. Please try again later."
            }
        )

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, updates: Dict[str, Any]):
    """
    Update an existing task
    
    Args:
        task_id (int): Task ID to update
        updates (dict): Fields to update
        
    Returns:
        TaskModel: Updated task
    """
    try:
        logger.info(f"Updating task: {task_id}")
        
        # Use Supabase database service
        updated_task = await database_service.update_task(task_id, updates)
        
        if updated_task:
            return TaskModel(**updated_task)
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Task not found",
                    "message": f"Task with ID {task_id} not found."
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update task",
                "message": "Unable to update task. Please try again later."
            }
        )

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """
    Delete a specific task
    
    Args:
        task_id (int): Task ID to delete
        
    Returns:
        dict: Success message
    """
    try:
        logger.info(f"Deleting task: {task_id}")
        
        # Use Supabase database service
        success = await database_service.delete_task(task_id)
        
        if success:
            return {
                "message": f"Task {task_id} deleted successfully",
                "status": "success"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Task not found",
                    "message": f"Task with ID {task_id} not found."
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete task",
                "message": "Unable to delete task. Please try again later."
            }
        )

@router.delete("/tasks")
async def clear_tasks(user_id: Optional[str] = None):
    """
    Clear all tasks
    
    Args:
        user_id (str, optional): Clear tasks only for specific user
    
    Returns:
        dict: Success message
    """
    try:
        logger.info(f"Clearing tasks for user: {user_id or 'all users'}")
        
        # Use Supabase database service
        cleared_count = await database_service.clear_all_tasks(user_id)
        
        return {
            "message": f"Successfully cleared {cleared_count} tasks",
            "status": "success",
            "count": cleared_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to clear tasks",
                "message": "Unable to clear tasks. Please try again later."
            }
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process user message and return AI response
    
    Args:
        request (ChatRequest): User message and optional context
        
    Returns:
        ChatResponse: AI response with metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received chat request - Message length: {len(request.message)}")
        
        # Validate message
        if not request.message.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid input",
                    "message": "Message cannot be empty"
                }
            )
        
        # Generate AI response
        ai_result = await ai_service.generate_response(request.message, request.context)
        
        # Save chat message to database
        try:
            chat_data = {
                "user_id": request.user_id,
                "message": request.message,
                "response": ai_result["response"],
                "model": ai_result["model"],
                "response_time": ai_result["response_time"],
                "tokens_used": ai_result["tokens_used"],
                "context": request.context
            }
            await database_service.save_chat_message(chat_data)
        except Exception as chat_error:
            logger.warning(f"Failed to save chat message: {str(chat_error)}")
        
        # Auto-create task if the message seems task-related
        message_lower = request.message.lower()
        task_keywords = ['task', 'todo', 'remind', 'schedule', 'plan', 'organize', 'deadline', 'project']
        
        if any(keyword in message_lower for keyword in task_keywords):
            try:
                # Create a simple task from the message
                task_data = {
                    "summary": request.message[:100] + "..." if len(request.message) > 100 else request.message,
                    "category": "auto-generated",
                    "priority": "medium",
                    "status": "pending",
                    "user_id": request.user_id
                }
                created_task = await database_service.create_task(task_data)
                if created_task:
                    logger.info(f"Auto-created task from chat message: {created_task.get('id')}")
            except Exception as task_error:
                logger.warning(f"Failed to auto-create task: {str(task_error)}")
        
        # Log response time
        total_time = time.time() - start_time
        logger.info(f"Chat request processed in {total_time:.3f}s")
        
        return ChatResponse(
            response=ai_result["response"],
            model=ai_result["model"],
            response_time=ai_result["response_time"],
            tokens_used=ai_result["tokens_used"],
            status=ai_result["status"],
            timestamp=time.time(),
            tasks=ai_result.get("tasks", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Unable to process your request. Please try again later."
            }
        )

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Handle file uploads (images, audio, PDFs)
    
    Args:
        file (UploadFile): Uploaded file
        description (str, optional): File description
        
    Returns:
        FileUploadResponse: Upload result with file info
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received file upload - Filename: {file.filename}, Content-Type: {file.content_type}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid file",
                    "message": "Filename is required"
                }
            )
        
        # Check content type
        allowed_types = get_allowed_file_types()
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Unsupported file type",
                    "message": f"Allowed types: {', '.join(allowed_types)}"
                }
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "File too large",
                    "message": f"Maximum file size: {settings.max_file_size // (1024*1024)}MB"
                }
            )
        
        # Generate unique filename
        file_id = f"{int(time.time())}_{file.filename}"
        upload_path = os.path.join(settings.upload_dir, file_id)
        
        # Save file
        async with aiofiles.open(upload_path, 'wb') as f:
            await f.write(file_content)
        
        # Process file based on type
        processing_result = None
        if file.content_type.startswith('image/'):
            processing_result = await ai_service.process_image(upload_path)
        elif file.content_type.startswith('audio/'):
            processing_result = await ai_service.process_audio(upload_path)
        
        # Log upload time
        total_time = time.time() - start_time
        logger.info(f"File upload processed in {total_time:.3f}s")
        
        response_message = f"File uploaded successfully"
        if processing_result:
            response_message += f". Processing status: {processing_result['status']}"
        
        return FileUploadResponse(
            filename=file.filename,
            size=file_size,
            content_type=file.content_type,
            upload_path=upload_path,
            status="success",
            message=response_message,
            file_id=file_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "message": "Unable to process file upload. Please try again later."
            }
        )

@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """
    Get information about an uploaded file
    
    Args:
        file_id (str): File identifier
        
    Returns:
        Dict: File information
    """
    try:
        file_path = os.path.join(settings.upload_dir, file_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "File not found",
                    "message": f"File with ID '{file_id}' does not exist"
                }
            )
        
        file_stats = os.stat(file_path)
        
        return {
            "file_id": file_id,
            "size": file_stats.st_size,
            "created_at": file_stats.st_ctime,
            "modified_at": file_stats.st_mtime,
            "status": "available"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Unable to retrieve file information"
            }
        )

@router.post("/multimodal", response_model=MultimodalResponse)
async def multimodal_chat_endpoint(request: MultimodalRequest):
    """
    Process multimodal input (text + image + audio)
    
    Args:
        request (MultimodalRequest): Multimodal input request
        
    Returns:
        MultimodalResponse: AI response with processing details
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received multimodal request - Text: {bool(request.message)}, Image: {bool(request.image_file_id)}, Audio: {bool(request.audio_file_id)}")
        
        # Validate that at least one input is provided
        if not any([request.message, request.image_file_id, request.audio_file_id]):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid input",
                    "message": "At least one input type (text, image, or audio) is required"
                }
            )
        
        # Get file paths if file IDs are provided
        image_path = None
        audio_path = None
        
        if request.image_file_id:
            image_path = os.path.join(settings.upload_dir, request.image_file_id)
            if not os.path.exists(image_path):
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "File not found",
                        "message": f"Image file {request.image_file_id} not found"
                    }
                )
        
        if request.audio_file_id:
            audio_path = os.path.join(settings.upload_dir, request.audio_file_id)
            if not os.path.exists(audio_path):
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "File not found", 
                        "message": f"Audio file {request.audio_file_id} not found"
                    }
                )
        
        # Process multimodal input
        result = await ai_service.process_multimodal_input(
            text=request.message,
            image_path=image_path,
            audio_path=audio_path,
            context=request.context
        )
        
        # Log processing time
        total_time = time.time() - start_time
        logger.info(f"Multimodal request processed in {total_time:.3f}s")
        
        if result["status"] == "success":
            return MultimodalResponse(
                response=result["combined_response"],
                processing_details={
                    "image_processing": result.get("image_processing"),
                    "audio_processing": result.get("audio_processing"),
                    "processing_time": result["processing_time"]
                },
                inputs_processed=result["inputs_processed"],
                model_info=result.get("ai_metadata", {}),
                status="success",
                timestamp=time.time()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Processing failed",
                    "message": result.get("error", "Unknown error occurred"),
                    "details": result
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multimodal endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Unable to process multimodal request. Please try again later."
            }
        )

@router.post("/upload/audio", response_model=MultimodalResponse)
async def upload_audio(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload and process audio file with transcription and AI analysis
    
    Args:
        file (UploadFile): Audio file to process
        description (str, optional): Optional description
        
    Returns:
        MultimodalResponse: Transcription and AI analysis
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received audio upload: {file.filename}, size: {file.size}, type: {file.content_type}")
        
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid file type",
                    "message": "Only audio files are supported for this endpoint"
                }
            )
        
        # Validate file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "File too large",
                    "message": "Audio file must be smaller than 10MB"
                }
            )
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.webm'
        file_id = f"audio_{int(time.time())}_{hash(file.filename or 'audio')}{file_extension}"
        upload_path = os.path.join(settings.upload_dir, file_id)
        
        # Save file
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process audio with AI service
        processing_result = await ai_service.process_audio(upload_path)
        
        if processing_result["status"] == "success":
            # Save to database if available
            try:
                file_data = {
                    "filename": file.filename or "audio_recording",
                    "file_path": upload_path,
                    "file_size": file.size,
                    "content_type": file.content_type,
                    "file_id": file_id,
                    "description": description,
                    "processing_result": processing_result
                }
                await database_service.save_uploaded_file(file_data)
            except Exception as db_error:
                logger.warning(f"Failed to save file to database: {str(db_error)}")
            
            total_time = time.time() - start_time
            
            return MultimodalResponse(
                response=processing_result.get("ai_response", {}).get("response", "Audio processed successfully"),
                processing_details={
                    "transcription": processing_result.get("transcription", {}),
                    "processing_time": processing_result["processing_time"],
                    "total_time": round(total_time, 3)
                },
                inputs_processed=["audio"],
                model_info=processing_result.get("ai_response", {}),
                status="success",
                timestamp=time.time()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Audio processing failed",
                    "message": processing_result.get("error", "Unknown error occurred"),
                    "details": processing_result
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audio upload endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "message": "Unable to process audio upload. Please try again later."
            }
        )

@router.post("/upload/file", response_model=MultimodalResponse)
async def upload_file_analysis(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload and analyze files (images, documents, text files)
    
    Args:
        file (UploadFile): File to analyze
        description (str, optional): Optional description
        
    Returns:
        MultimodalResponse: File analysis results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received file upload for analysis: {file.filename}, size: {file.size}, type: {file.content_type}")
        
        # Validate file size (50MB limit)
        if file.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "File too large",
                    "message": "File must be smaller than 50MB"
                }
            )
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.bin'
        file_id = f"file_{int(time.time())}_{hash(file.filename or 'file')}{file_extension}"
        upload_path = os.path.join(settings.upload_dir, file_id)
        
        # Save file
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process file based on type
        processing_result = None
        inputs_processed = []
        
        if file.content_type.startswith('image/'):
            processing_result = await ai_service.process_image(upload_path)
            inputs_processed = ["image"]
        elif file.content_type.startswith('text/') or file.filename.endswith(('.txt', '.md', '.csv')):
            # Read text file content
            try:
                async with aiofiles.open(upload_path, 'r', encoding='utf-8') as f:
                    text_content = await f.read()
                
                # Generate AI analysis of text content
                ai_result = await ai_service.generate_response(
                    f"Please analyze and summarize this text content:\n\n{text_content[:2000]}...",
                    context="Text file analysis"
                )
                
                processing_result = {
                    "status": "success",
                    "analysis": ai_result["response"],
                    "processing_time": ai_result["response_time"],
                    "ai_response": ai_result
                }
                inputs_processed = ["text_file"]
                
            except UnicodeDecodeError:
                processing_result = {
                    "status": "error",
                    "error": "Unable to read text file - encoding not supported"
                }
        else:
            # Fallback for unsupported file types
            processing_result = {
                "status": "partial",
                "analysis": f"File '{file.filename}' uploaded successfully. This file type ({file.content_type}) requires manual review.",
                "processing_time": 0.1
            }
            inputs_processed = ["file"]
        
        if not processing_result:
            processing_result = {
                "status": "error",
                "error": "Unsupported file type for analysis"
            }
        
        # Save to database if available
        try:
            file_data = {
                "filename": file.filename or "uploaded_file",
                "file_path": upload_path,
                "file_size": file.size,
                "content_type": file.content_type,
                "file_id": file_id,
                "description": description,
                "processing_result": processing_result
            }
            await database_service.save_uploaded_file(file_data)
        except Exception as db_error:
            logger.warning(f"Failed to save file to database: {str(db_error)}")
        
        total_time = time.time() - start_time
        
        return MultimodalResponse(
            response=processing_result.get("analysis", processing_result.get("ai_response", {}).get("response", "File processed")),
            processing_details={
                "file_analysis": processing_result,
                "processing_time": processing_result.get("processing_time", 0),
                "total_time": round(total_time, 3)
            },
            inputs_processed=inputs_processed,
            model_info=processing_result.get("ai_response", {}),
            status=processing_result.get("status", "success"),
            timestamp=time.time()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in file upload endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "message": "Unable to process file upload. Please try again later."
            }
        ) 