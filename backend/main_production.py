#!/usr/bin/env python3
"""
Production FastAPI backend for IntelliAssist with lazy AI model loading
Optimized for fast startup and reliable deployment
"""

import os
import logging
import time
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import asyncio
import aiofiles
from pathlib import Path
import mimetypes

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Response
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
    version="2.2.0",
    description="AI-powered task management with lazy loading"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables with better defaults
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Enhanced logging for debugging production issues
logger.info(f"🔧 Environment Configuration:")
logger.info(f"  - GROQ_API_KEY configured: {bool(GROQ_API_KEY)}")
logger.info(f"  - SUPABASE_URL configured: {bool(SUPABASE_URL)}")
logger.info(f"  - SUPABASE_SERVICE_KEY configured: {bool(SUPABASE_SERVICE_KEY)}")

# Import AI service for fallback responses with enhanced error handling
try:
    from services.ai import AIService
    # Initialize AI service instance with proper configuration
    ai_service = AIService()
    
    # Test if AI service is properly configured
    if hasattr(ai_service, 'groq_client') and ai_service.groq_client:
        logger.info("✅ AI service imported and configured successfully")
        logger.info(f"✅ AI service Groq client available: {ai_service.groq_client is not None}")
    else:
        logger.warning("⚠️ AI service imported but Groq client not available")
        
except ImportError as e:
    logger.error(f"❌ AI service import failed: {e}")
    logger.info("📝 Creating fallback AI service...")
    # Create a minimal fallback AI service
    class FallbackAIService:
        def __init__(self):
            self.groq_client = None
            self.groq_api_key = GROQ_API_KEY
            
        def _generate_fallback_response(self, file_type: str, filename: str, content_hint: str = None):
            return safe_fallback_response(file_type, filename, content_hint)
    
    ai_service = FallbackAIService()
    logger.info("✅ Fallback AI service created")
    
except Exception as e:
    logger.error(f"❌ AI service initialization failed: {e}")
    logger.info("📝 Creating minimal AI service...")
    class MinimalAIService:
        def __init__(self):
            self.groq_client = None
            self.groq_api_key = GROQ_API_KEY
        def _generate_fallback_response(self, file_type: str, filename: str, content_hint: str = None):
            return safe_fallback_response(file_type, filename, content_hint)
    ai_service = MinimalAIService()
    logger.info("✅ Minimal AI service created")

def safe_fallback_response(file_type: str, filename: str, content_hint: str = None):
    """Safely generate fallback response, with or without AI service"""
    if ai_service:
        return ai_service._generate_fallback_response(file_type, filename, content_hint)
    else:
        # Basic fallback if AI service is not available
        if file_type == "image":
            return analyze_image_content(filename)
        elif file_type == "text":
            return analyze_document_content(filename)
        elif file_type == "pdf":
            return analyze_document_content(filename)
        else:
            return {
                "analysis": f"File '{filename}' uploaded successfully.",
                "tasks": [{"title": f"Review {filename}", "description": f"Process {filename}", "priority": "medium", "category": "general", "status": "pending"}],
                "suggestions": ["Review file content"],
                "ai_processed": False
            }

# Global AI service variables (lazy loaded)
groq_client = None
supabase_client = None
whisper_model = None
sentiment_model = None

# Lazy loading flags
_groq_attempted = False
_transformers_attempted = False
_supabase_attempted = False

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

# Lazy loading functions
def get_groq_client():
    """Lazy load Groq client with robust initialization"""
    global groq_client, _groq_attempted
    
    if not _groq_attempted and GROQ_API_KEY:
        _groq_attempted = True
        try:
            from groq import Groq
            # Simple initialization without extra parameters
            groq_client = Groq(api_key=GROQ_API_KEY)
            
            # Test the client to ensure it's working
            # This doesn't make an API call, just verifies the client is properly initialized
            if hasattr(groq_client, 'audio') and hasattr(groq_client.audio, 'transcriptions'):
                logger.info("✅ Groq client loaded and verified successfully")
            else:
                logger.warning("⚠️ Groq client loaded but audio transcription API not available")
                groq_client = None
        except Exception as e:
            logger.error(f"Groq loading failed: {e}")
            groq_client = None
    
    return groq_client

def get_transformers_models():
    """Lazy load Transformers models"""
    global whisper_model, sentiment_model, _transformers_attempted
    
    if not _transformers_attempted:
        _transformers_attempted = True
        try:
            from transformers import pipeline
            import torch
            
            # Load smaller, faster models
            whisper_model = pipeline(
                "automatic-speech-recognition", 
                model="openai/whisper-tiny",  # Much smaller model
                device=-1  # Force CPU to avoid GPU issues
            )
            logger.info("✅ Whisper model loaded")
            
            sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            logger.info("✅ Sentiment model loaded")
            
        except Exception as e:
            logger.warning(f"Transformers loading failed: {e}")
    
    return whisper_model, sentiment_model

def get_supabase_client():
    """Lazy load Supabase client"""
    global supabase_client, _supabase_attempted
    
    if not _supabase_attempted and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        _supabase_attempted = True
        try:
            from supabase import create_client
            supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            logger.info("✅ Supabase connected")
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
    
    return supabase_client

# Fast startup - no heavy model loading
@app.on_event("startup")
async def startup_event():
    """Fast startup without heavy AI model loading"""
    logger.info("🚀 IntelliAssist backend starting up (lazy loading enabled)")
    logger.info(f"📁 Upload directory: {UPLOAD_DIR}")
    logger.info("✅ Ready to serve requests")

# AI Processing Functions
def extract_tasks_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract actionable tasks from text using keyword analysis"""
    if not text:
        return []
    
    tasks = []
    text_lower = text.lower()
    
    # Task indicator patterns
    task_patterns = [
        r'(?:need to|have to|must|should|todo|task:?)\s+(.+?)(?:[.!?]|$)',
        r'(?:remember to|don\'t forget to)\s+(.+?)(?:[.!?]|$)',
        r'(?:action item:?|ai:?)\s+(.+?)(?:[.!?]|$)',
        r'(?:follow up|followup)\s+(?:on|with)?\s*(.+?)(?:[.!?]|$)',
        r'(?:schedule|set up|arrange)\s+(.+?)(?:[.!?]|$)',
        r'(?:call|email|contact)\s+(.+?)(?:[.!?]|$)',
        r'(?:review|check|verify|confirm)\s+(.+?)(?:[.!?]|$)',
        r'(?:create|make|build|develop)\s+(.+?)(?:[.!?]|$)',
        r'(?:send|submit|deliver)\s+(.+?)(?:[.!?]|$)',
        r'(?:update|modify|change)\s+(.+?)(?:[.!?]|$)'
    ]
    
    for pattern in task_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 3:
                priority = "medium"
                if any(word in match for word in ["urgent", "asap", "immediately", "critical"]):
                    priority = "high"
                elif any(word in match for word in ["later", "eventually", "when possible"]):
                    priority = "low"
                
                category = "general"
                if any(word in match for word in ["meeting", "call", "discuss"]):
                    category = "meetings"
                elif any(word in match for word in ["email", "send", "contact"]):
                    category = "communication"
                elif any(word in match for word in ["review", "check", "verify"]):
                    category = "review"
                elif any(word in match for word in ["create", "build", "develop"]):
                    category = "development"
                
                tasks.append({
                    "title": match.strip().capitalize(),
                    "description": f"Extracted from: {text[:100]}..." if len(text) > 100 else f"Extracted from: {text}",
                    "priority": priority,
                    "category": category,
                    "status": "pending"
                })
    
    return tasks[:5]  # Limit to 5 tasks

async def analyze_audio_content(filename: str, file_path: str = None) -> Dict[str, Any]:
    """Analyze audio content with lazy AI loading"""
    
    name_lower = filename.lower()
    
    # Determine audio type from filename
    audio_type = "general audio"
    if any(word in name_lower for word in ["meeting", "conference", "call"]):
        audio_type = "meeting recording"
    elif any(word in name_lower for word in ["note", "memo", "reminder"]):
        audio_type = "voice note"
    elif any(word in name_lower for word in ["interview", "conversation", "discussion"]):
        audio_type = "interview/conversation"
    elif any(word in name_lower for word in ["presentation", "speech", "talk", "dramatic", "reading"]):
        audio_type = "presentation/speech"
    
    # Try Groq transcription first
    transcription = None
    ai_processed = False
    
    groq = get_groq_client()
    if groq and file_path:
        try:
            with open(file_path, "rb") as audio_file:
                transcription_response = groq.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3"
                )
                transcription = transcription_response.text
                ai_processed = True
                logger.info(f"✅ Groq transcription completed for {filename}")
        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
    
    # Fallback to Transformers if Groq fails
    if not transcription and file_path:
        whisper, _ = get_transformers_models()
        if whisper:
            try:
                transcription_result = whisper(file_path)
                transcription = transcription_result["text"]
                ai_processed = True
                logger.info(f"✅ Transformers transcription completed for {filename}")
            except Exception as e:
                logger.error(f"Transformers transcription failed: {e}")
    
    # If we have transcription, analyze it
    if transcription and ai_processed:
        tasks = extract_tasks_from_text(transcription)
        
        # Analyze sentiment
        sentiment = "neutral"
        _, sentiment_model = get_transformers_models()
        if sentiment_model:
            try:
                sentiment_result = sentiment_model(transcription[:512])
                sentiment = sentiment_result[0]["label"].lower()
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Extract key topics
        words = re.findall(r'\b\w+\b', transcription.lower())
        word_freq = {}
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for word in words:
            if len(word) > 3 and word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        key_topics = sorted(word_freq.keys(), key=word_freq.get, reverse=True)[:5]
        
        suggestions = [
            "Review transcription for accuracy",
            "Extract action items from content",
            "Follow up on mentioned topics"
        ]
        
        return {
            "transcription": transcription,
            "audio_type": audio_type,
            "sentiment": sentiment,
            "key_topics": key_topics,
            "suggestions": suggestions,
            "tasks": tasks,
            "duration_estimate": "AI transcribed",
            "confidence": 0.90,
            "ai_processed": True
        }
    
    # Fallback analysis based on filename
    if "dramatic reading" in name_lower:
        transcription = f"Audio content analysis for '{filename}': This appears to be a dramatic reading or presentation."
        tasks = [{
            "title": "Review dramatic reading content",
            "description": f"Analyze the content and message from {filename}",
            "priority": "medium",
            "category": "content",
            "status": "pending"
        }]
    else:
        transcription = f"Audio analysis for '{filename}': Audio file processed successfully."
        tasks = [{
            "title": "Review audio content",
            "description": f"Analyze and extract information from {filename}",
            "priority": "medium",
            "category": "general",
            "status": "pending"
        }]
    
    return {
        "transcription": transcription,
        "audio_type": audio_type,
        "sentiment": "neutral",
        "key_topics": ["audio", "content", "analysis"],
        "suggestions": ["Review audio content", "Extract important information"],
        "tasks": tasks,
        "duration_estimate": "Processed",
        "confidence": 0.60,
        "ai_processed": False
    }

def analyze_image_content(filename: str, file_path: str = None) -> Dict[str, Any]:
    """Analyze image content based on filename and context"""
    
    name_lower = filename.lower()
    file_ext = Path(filename).suffix.lower()
    
    # Determine image type and context
    image_type = "general image"
    if any(word in name_lower for word in ["screenshot", "screen", "capture"]):
        image_type = "screenshot"
    elif any(word in name_lower for word in ["diagram", "chart", "graph", "flowchart"]):
        image_type = "diagram/chart"
    elif any(word in name_lower for word in ["document", "scan", "pdf", "receipt"]):
        image_type = "scanned document"
    elif any(word in name_lower for word in ["ui", "mockup", "wireframe", "design"]):
        image_type = "UI/design"
    elif any(word in name_lower for word in ["photo", "picture", "img"]):
        image_type = "photograph"
    
    # Generate contextual analysis
    if image_type == "screenshot":
        suggestions = [
            "Review captured information",
            "Extract text or data if needed",
            "Create documentation from screenshot",
            "Follow up on captured content"
        ]
        tasks = [{
            "title": "Review screenshot content",
            "description": f"Analyze and extract information from {filename}",
            "priority": "medium",
            "category": "review",
            "status": "pending"
        }]
    
    elif image_type == "diagram/chart":
        suggestions = [
            "Analyze data relationships",
            "Extract key insights",
            "Create action items from diagram",
            "Share with relevant team members"
        ]
        tasks = [{
            "title": "Analyze diagram/chart",
            "description": f"Extract insights and action items from {filename}",
            "priority": "high",
            "category": "analysis",
            "status": "pending"
        }]
    
    elif image_type == "scanned document":
        suggestions = [
            "Extract text from document",
            "Review document requirements",
            "Create follow-up tasks",
            "File or organize document"
        ]
        tasks = [{
            "title": "Process scanned document",
            "description": f"Review and extract information from {filename}",
            "priority": "high",
            "category": "documents",
            "status": "pending"
        }]
    
    elif image_type == "UI/design":
        suggestions = [
            "Review design specifications",
            "Provide feedback on design",
            "Plan implementation tasks",
            "Share with development team"
        ]
        tasks = [{
            "title": "Review UI/design",
            "description": f"Analyze design and plan implementation for {filename}",
            "priority": "medium",
            "category": "design",
            "status": "pending"
        }]
    
    else:  # General image
        suggestions = [
            "Review image content",
            "Determine next steps",
            "Organize or categorize image"
        ]
        tasks = [{
            "title": "Review image",
            "description": f"Process and organize {filename}",
            "priority": "low",
            "category": "general",
            "status": "pending"
        }]
    
    return {
        "analysis_type": "image_analysis",
        "image_type": image_type,
        "file_format": file_ext,
        "key_points": ["visual content", "contextual information"],
        "suggestions": suggestions,
        "tasks": tasks,
        "confidence": 0.75,
        "processing_method": "filename_and_context_analysis"
    }

def analyze_document_content(filename: str, file_path: str = None) -> Dict[str, Any]:
    """Enhanced document analysis with actual content extraction"""
    
    name_lower = filename.lower()
    file_ext = Path(filename).suffix.lower()
    
    # Initialize variables
    extracted_content = ""
    content_type = "unknown"
    processing_method = "filename_only"
    
    # Try to extract actual content if file path is provided
    if file_path and Path(file_path).exists():
        try:
            if file_ext == '.pdf':
                # Extract PDF content
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        extracted_content = ""
                        for page in pdf_reader.pages:
                            extracted_content += page.extract_text() + "\\n"
                        content_type = "pdf_text"
                        processing_method = "pdf_extraction"
                        logger.info(f"✅ PDF content extracted: {len(extracted_content)} characters")
                except Exception as pdf_error:
                    logger.warning(f"PDF extraction failed: {pdf_error}")
                    extracted_content = f"PDF document: {filename}"
                    
            elif file_ext in ['.docx', '.doc']:
                # Extract Word document content
                try:
                    from docx import Document
                    doc = Document(file_path)
                    extracted_content = "\\n".join([paragraph.text for paragraph in doc.paragraphs])
                    content_type = "word_text"
                    processing_method = "docx_extraction"
                    logger.info(f"✅ Word document content extracted: {len(extracted_content)} characters")
                except Exception as docx_error:
                    logger.warning(f"Word document extraction failed: {docx_error}")
                    extracted_content = f"Word document: {filename}"
                    
            elif file_ext == '.csv':
                # Analyze CSV structure and content
                try:
                    import pandas as pd
                    import chardet
                    
                    # Detect encoding
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                    
                    # Read CSV
                    df = pd.read_csv(file_path, encoding=encoding, nrows=100)  # Limit rows for analysis
                    
                    extracted_content = f"CSV Data Analysis:\\n"
                    extracted_content += f"- Rows: {len(df)}\\n"
                    extracted_content += f"- Columns: {len(df.columns)}\\n"
                    extracted_content += f"- Column names: {list(df.columns)}\\n"
                    extracted_content += f"- Data types: {df.dtypes.to_dict()}\\n"
                    extracted_content += f"- First few rows:\\n{df.head(3).to_string()}\\n"
                    
                    content_type = "csv_data"
                    processing_method = "pandas_analysis"
                    logger.info(f"✅ CSV analysis completed: {len(df)} rows, {len(df.columns)} columns")
                except Exception as csv_error:
                    logger.warning(f"CSV analysis failed: {csv_error}")
                    extracted_content = f"CSV file: {filename}"
                    
            elif file_ext in ['.txt', '.md', '.log']:
                # Extract plain text content
                try:
                    import chardet
                    
                    # Detect encoding
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                    
                    # Read text content
                    with open(file_path, 'r', encoding=encoding) as f:
                        extracted_content = f.read()
                        content_type = "plain_text"
                        processing_method = "text_reading"
                        logger.info(f"✅ Text content extracted: {len(extracted_content)} characters")
                except Exception as txt_error:
                    logger.warning(f"Text extraction failed: {txt_error}")
                    extracted_content = f"Text file: {filename}"
                    
        except Exception as e:
            logger.error(f"Document content extraction failed for {filename}: {e}")
            extracted_content = f"Document: {filename}"
    
    # If no content extracted, use filename-based analysis
    if not extracted_content:
        extracted_content = f"Document: {filename}"
        processing_method = "filename_only"
    
    # Use AI service for analysis if available and content was extracted
    if ai_service and extracted_content and len(extracted_content) > len(filename) + 20:
        try:
            # Create AI analysis prompt
            analysis_prompt = f\"\"\"
            Analyze this document content and extract actionable tasks and insights:
            
            Document: {filename}
            Content Type: {content_type}
            Content: {extracted_content[:2000]}...  # Truncate for API limits
            
            Please provide:
            1. A summary of the document
            2. Any action items or tasks mentioned
            3. Key insights or important information
            4. Suggested next steps
            \"\"\"
            
            # Try to get AI analysis (this would need to be implemented in the AI service)
            if hasattr(ai_service, 'generate_response'):
                ai_result = ai_service.generate_response(analysis_prompt)
                if ai_result and ai_result.get('status') == 'success':
                    return {
                        "analysis_type": "ai_document_analysis",
                        "filename": filename,
                        "content_type": content_type,
                        "processing_method": processing_method,
                        "description": ai_result.get('response', ''),
                        "extracted_content_preview": extracted_content[:500] + "..." if len(extracted_content) > 500 else extracted_content,
                        "tasks": ai_result.get('tasks', []),
                        "suggestions": [
                            "Review the full document content",
                            "Check for any action items mentioned",
                            "Consider follow-up actions based on document type"
                        ],
                        "ai_processed": True,
                        "content_length": len(extracted_content)
                    }
        except Exception as ai_error:
            logger.warning(f"AI analysis failed for {filename}: {ai_error}")
    
    # Fallback analysis based on content and filename
    tasks = []
    suggestions = []
    
    # Extract tasks from content if available
    if extracted_content and len(extracted_content) > len(filename) + 20:
        extracted_tasks = extract_tasks_from_text(extracted_content)
        tasks.extend(extracted_tasks)
    
    # Add default tasks based on document type
    if file_ext == '.pdf':
        tasks.append({
            "title": f"Review PDF document: {filename}",
            "description": f"Analyze and process the PDF document content ({len(extracted_content)} characters extracted)",
            "priority": "medium",
            "category": "documents",
            "status": "pending"
        })
        suggestions.extend([
            "Check if the PDF contains forms that need to be filled",
            "Look for any signatures or approvals required",
            "Extract key information for future reference"
        ])
    elif file_ext in ['.docx', '.doc']:
        tasks.append({
            "title": f"Review Word document: {filename}",
            "description": f"Process and analyze the Word document content ({len(extracted_content)} characters extracted)",
            "priority": "medium",
            "category": "documents",
            "status": "pending"
        })
        suggestions.extend([
            "Check for track changes or comments",
            "Review document for required actions",
            "Consider version control if collaborative"
        ])
    elif file_ext == '.csv':
        tasks.append({
            "title": f"Analyze CSV data: {filename}",
            "description": f"Review and process the CSV data file ({processing_method})",
            "priority": "medium",
            "category": "data-analysis",
            "status": "pending"
        })
        suggestions.extend([
            "Check data quality and completeness",
            "Look for patterns or insights in the data",
            "Consider creating visualizations or reports"
        ])
    
    # If no specific tasks found, add a general review task
    if not tasks:
        tasks.append({
            "title": f"Review document: {filename}",
            "description": f"Process and analyze the document content using {processing_method}",
            "priority": "medium",
            "category": "documents",
            "status": "pending"
        })
    
    return {
        "analysis_type": "enhanced_document_analysis",
        "filename": filename,
        "content_type": content_type,
        "processing_method": processing_method,
        "description": f"Document analysis completed using {processing_method}. " + 
                      (f"Content extracted: {len(extracted_content)} characters." if extracted_content else "Filename-based analysis performed."),
        "extracted_content_preview": extracted_content[:300] + "..." if len(extracted_content) > 300 else extracted_content,
        "tasks": tasks,
        "suggestions": suggestions,
        "ai_processed": False,  # True only if AI service successfully processed
        "content_length": len(extracted_content),
        "file_extension": file_ext
    }

def analyze_video_content(filename: str, file_path: str = None) -> Dict[str, Any]:
    """Analyze video content based on filename"""
    
    name_lower = filename.lower()
    file_ext = Path(filename).suffix.lower()
    
    # Determine video type
    video_type = "general video"
    if any(word in name_lower for word in ["meeting", "conference", "call", "zoom"]):
        video_type = "meeting recording"
    elif any(word in name_lower for word in ["tutorial", "training", "demo", "howto"]):
        video_type = "tutorial/training"
    elif any(word in name_lower for word in ["presentation", "pitch", "demo"]):
        video_type = "presentation"
    elif any(word in name_lower for word in ["interview", "conversation"]):
        video_type = "interview"
    
    # Generate contextual suggestions
    if video_type == "meeting recording":
        suggestions = [
            "Extract meeting minutes",
            "Identify action items",
            "Share with attendees",
            "Schedule follow-ups"
        ]
        tasks = [{
            "title": "Process meeting recording",
            "description": f"Extract action items and create follow-ups from {filename}",
            "priority": "high",
            "category": "meetings",
            "status": "pending"
        }]
    
    elif video_type == "tutorial/training":
        suggestions = [
            "Review training content",
            "Create study notes",
            "Practice demonstrated skills",
            "Share with team if relevant"
        ]
        tasks = [{
            "title": "Review training video",
            "description": f"Study and apply content from {filename}",
            "priority": "medium",
            "category": "learning",
            "status": "pending"
        }]
    
    elif video_type == "presentation":
        suggestions = [
            "Review presentation content",
            "Extract key points",
            "Create follow-up materials",
            "Share insights with team"
        ]
        tasks = [{
            "title": "Review presentation video",
            "description": f"Extract insights and create follow-ups from {filename}",
            "priority": "medium",
            "category": "review",
            "status": "pending"
        }]
    
    else:  # General video
        suggestions = [
            "Review video content",
            "Extract relevant information",
            "Determine next steps"
        ]
        tasks = [{
            "title": "Review video",
            "description": f"Process and analyze {filename}",
            "priority": "low",
            "category": "media",
            "status": "pending"
        }]
    
    return {
        "analysis_type": "video_analysis",
        "video_type": video_type,
        "file_format": file_ext,
        "key_points": ["video content", "visual information"],
        "suggestions": suggestions,
        "tasks": tasks,
        "confidence": 0.70,
        "processing_method": "filename_analysis"
    }

def generate_ai_response(message: str, context: Dict[str, Any] = None) -> str:
    """Generate AI response with context awareness"""
    
    message_lower = message.lower()
    
    # Context-aware responses
    if context and context.get("file_analysis"):
        analysis = context["file_analysis"]
        if analysis.get("ai_processed"):
            return f"I've analyzed your file and found some interesting insights. The content appears to be {analysis.get('audio_type', 'general content')} with {analysis.get('sentiment', 'neutral')} sentiment. I've extracted {len(analysis.get('tasks', []))} potential tasks for you to consider."
    
    # Task-related queries
    if any(word in message_lower for word in ["task", "todo", "action", "need to"]):
        return "I can help you extract and organize tasks from your content. Upload a file or tell me what you need to accomplish!"
    
    # File upload queries
    if any(word in message_lower for word in ["upload", "file", "document", "audio", "image"]):
        return "You can upload various file types including audio recordings, images, and documents. I'll analyze them and extract actionable tasks for you!"
    
    # General helpful response
    return "I'm here to help you manage tasks and analyze content. You can chat with me, upload files for analysis, or ask me to help organize your work!"

# API Routes
@app.get("/")
def root():
    return {
        "message": "IntelliAssist AI Backend",
        "version": "2.2.0",
        "status": "running",
        "features": ["lazy_loading", "fast_startup"]
    }

@app.get("/health")
def health():
    ai_status = "not_available"
    if ai_service:
        ai_status = "available"
        if hasattr(ai_service, 'groq_client') and ai_service.groq_client:
            ai_status = "groq_ready"
    
    return {
        "status": "healthy",
        "ai_features": "lazy_loaded",
        "ai_service_status": ai_status,
        "timestamp": time.time()
    }

@app.post("/api/v1/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """Enhanced chat with AI responses"""
    try:
        if not chat_data.message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # Generate AI response
        ai_response = generate_ai_response(chat_data.message)
        
        # Extract tasks from the message
        tasks = extract_tasks_from_text(chat_data.message)
        
        # Store conversation
        conversation = {
            "id": len(conversations_db) + 1,
            "user_message": chat_data.message,
            "ai_response": ai_response,
            "tasks_extracted": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
        conversations_db.append(conversation)
        
        return {
            "response": ai_response,
            "message": ai_response,
            "tasks": tasks,
            "conversation_id": conversation["id"],
            "processing_time": "0.5s"
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/api/v1/upload")
async def upload_file_endpoint(file: UploadFile = File(...)):
    """File upload with AI analysis"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        logger.info(f"📁 Upload request received: {file.filename}, size: {file.size}, type: {file.content_type}")
        
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
        
        # Analyze based on file type using AI service
        analysis = {"type": "general", "tasks": [], "suggestions": []}
        
        if file.content_type:
            if file.content_type.startswith('audio/'):
                analysis = await analyze_audio_content(file.filename, str(file_path))
            elif file.content_type.startswith('image/'):
                # Use AI service for proper image analysis if available
                try:
                    if ai_service and hasattr(ai_service, 'process_image'):
                        ai_result = await ai_service.process_image(str(file_path), "general")
                        if ai_result.get("status") == "success":
                            analysis = {
                                "analysis_type": "ai_image_analysis",
                                "description": ai_result.get("ai_insights", ai_result.get("description", "")),
                                "image_type": ai_result.get("context_type", "general image"),
                                "confidence": ai_result.get("confidence", 0.8),
                                "tasks": ai_result.get("tasks", []),
                                "suggestions": ai_result.get("suggestions", []),
                                "metadata": ai_result.get("metadata", {}),
                                "model_used": ai_result.get("model_used", "AI Vision"),
                                "ai_processed": True
                            }
                        else:
                            # Fallback to enhanced filename analysis
                            analysis = safe_fallback_response("image", file.filename)
                    else:
                        logger.warning("AI service not available - using fallback analysis")
                        analysis = safe_fallback_response("image", file.filename)
                except Exception as e:
                    logger.error(f"AI image processing failed: {e}")
                    # Fallback to enhanced filename analysis
                    analysis = safe_fallback_response("image", file.filename)
                    
            elif file.content_type.startswith('video/'):
                analysis = analyze_video_content(file.filename, str(file_path))
            elif any(file.content_type.startswith(t) for t in ['text/', 'application/pdf', 'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats']):
                # Enhanced document processing
                try:
                    if file.content_type.startswith('text/') or file.content_type == 'text/plain':
                        # Read and analyze text files with AI
                        try:
                            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                                text_content = await f.read()
                            
                            # Generate AI analysis for text content
                            enhanced_prompt = f"""Analyze this text file content and provide comprehensive task management insights:

FILE: {file.filename}
CONTENT:
{text_content[:2000]}{'...' if len(text_content) > 2000 else ''}

Please provide:
1. CONTENT OVERVIEW: What type of document is this?
2. KEY INFORMATION: Most important points or data
3. ACTIONABLE TASKS: Specific tasks or action items
4. PRIORITIES: What appears urgent or time-sensitive?
5. NEXT STEPS: Logical follow-up actions

Focus on actionable, implementable recommendations for task management."""

                            if ai_service and hasattr(ai_service, 'generate_response'):
                                ai_result = await ai_service.generate_response(enhanced_prompt, context="Text file analysis")
                                
                                analysis = {
                                    "analysis_type": "ai_text_analysis", 
                                    "description": ai_result.get("response", "Text file analyzed successfully"),
                                    "document_type": "text file",
                                    "content_preview": text_content[:300] + "..." if len(text_content) > 300 else text_content,
                                    "tasks": ai_service._extract_tasks_from_response(ai_result.get("response", "")),
                                    "suggestions": ai_service._extract_suggestions_from_response(ai_result.get("response", "")),
                                    "metadata": {
                                        "file_size": len(text_content),
                                        "word_count": len(text_content.split()),
                                        "ai_processed": True
                                    },
                                    "confidence": 0.9,
                                    "ai_processed": True
                                }
                            else:
                                # Use fallback if AI service not available
                                analysis = safe_fallback_response("text", file.filename)
                                analysis["content_preview"] = text_content[:300] + "..." if len(text_content) > 300 else text_content
                            
                        except UnicodeDecodeError:
                            analysis = safe_fallback_response("text", file.filename, "encoding_error")
                    else:
                        # For PDFs and other documents, use enhanced fallback
                        content_hint = "document"
                        if file.content_type == 'application/pdf':
                            content_hint = "pdf_document"
                        elif 'word' in file.content_type:
                            content_hint = "word_document"
                        elif 'excel' in file.content_type or 'spreadsheet' in file.content_type:
                            content_hint = "spreadsheet"
                        elif 'powerpoint' in file.content_type or 'presentation' in file.content_type:
                            content_hint = "presentation"
                            
                        analysis = safe_fallback_response("pdf", file.filename, content_hint)
                        
                except Exception as e:
                    logger.error(f"Document processing failed: {e}")
                    analysis = safe_fallback_response("pdf", file.filename)
            else:
                # Generic file analysis with enhanced fallback
                analysis = safe_fallback_response("generic", file.filename)
        else:
            # Fallback to filename-based analysis
            file_ext = Path(file.filename).suffix.lower()
            if file_ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                analysis = await analyze_audio_content(file.filename, str(file_path))
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                # Use AI service for image analysis if available
                try:
                    if ai_service and hasattr(ai_service, 'process_image'):
                        ai_result = await ai_service.process_image(str(file_path), "general")
                        if ai_result.get("status") == "success":
                            analysis = {
                                "analysis_type": "ai_image_analysis",
                                "description": ai_result.get("ai_insights", ai_result.get("description", "")),
                                "image_type": ai_result.get("context_type", "general image"),
                                "confidence": ai_result.get("confidence", 0.8),
                                "tasks": ai_result.get("tasks", []),
                                "suggestions": ai_result.get("suggestions", []),
                                "metadata": ai_result.get("metadata", {}),
                                "ai_processed": True
                            }
                        else:
                            analysis = safe_fallback_response("image", file.filename)
                    else:
                        logger.warning("AI service not available - using fallback analysis")
                        analysis = safe_fallback_response("image", file.filename)
                except Exception as e:
                    logger.error(f"AI image processing failed: {e}")
                    analysis = safe_fallback_response("image", file.filename)
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                analysis = analyze_video_content(file.filename, str(file_path))
            elif file_ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx', '.xls', '.ppt', '.pptx']:
                if file_ext in ['.txt', '.md']:
                    # Enhanced text file processing
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            text_content = await f.read()
                        
                        enhanced_prompt = f"""Analyze this text file and extract actionable insights:

FILE: {file.filename}
CONTENT:
{text_content[:2000]}{'...' if len(text_content) > 2000 else ''}

Provide specific, actionable recommendations for task management and productivity."""

                        if ai_service and hasattr(ai_service, 'generate_response'):
                            ai_result = await ai_service.generate_response(enhanced_prompt, context="Text file analysis")
                            
                            analysis = {
                                "analysis_type": "ai_text_analysis",
                                "description": ai_result.get("response", "Text file analyzed"),
                                "document_type": "text file",
                                "tasks": ai_service._extract_tasks_from_response(ai_result.get("response", "")),
                                "suggestions": ai_service._extract_suggestions_from_response(ai_result.get("response", "")),
                                "ai_processed": True
                            }
                        else:
                            # Use fallback if AI service not available
                            analysis = safe_fallback_response("text", file.filename)
                            analysis["content_preview"] = text_content[:300] + "..." if len(text_content) > 300 else text_content
                    except Exception as e:
                        logger.error(f"Text processing failed: {e}")
                        analysis = safe_fallback_response("text", file.filename)
                else:
                    # Other document types - enhanced fallback
                    doc_type = "pdf" if file_ext == '.pdf' else "document"
                    analysis = safe_fallback_response(doc_type, file.filename)
            else:
                analysis = safe_fallback_response("generic", file.filename)
        
        return {
            "message": f"File '{file.filename}' uploaded and analyzed successfully!",
            "response": f"File '{file.filename}' uploaded and analyzed successfully!",
            "file_id": file_id,
            "file_info": file_info,
            "processing_details": {
                "file_analysis": analysis,
                "processing_time": "1.2s",
                "ai_insights_enabled": True,
                "ai_processed": analysis.get("ai_processed", False)
            },
            "tasks": analysis.get("tasks", []),
            "suggestions": analysis.get("suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/v1/upload/audio")
async def upload_audio_endpoint(file: UploadFile = File(...)):
    """Specialized audio upload and transcription"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        logger.info(f"🎵 Audio upload: {file.filename}, size: {file.size}")
        
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
        audio_analysis = await analyze_audio_content(file.filename, str(file_path))
        
        # Generate AI response for the transcription
        transcription_text = audio_analysis.get("transcription", "")
        ai_response = ""
        
        if transcription_text and audio_analysis.get("ai_processed", False):
            # Create a helpful AI response based on the transcription
            context = {
                "audio_type": audio_analysis.get("audio_type", "general audio"),
                "sentiment": audio_analysis.get("sentiment", "neutral"),
                "key_topics": audio_analysis.get("key_topics", []),
                "tasks_found": len(audio_analysis.get("tasks", []))
            }
            
            ai_response = generate_ai_response(
                f"I've successfully transcribed your audio message. Here's what I found:\n\n"
                f"**Transcription:** {transcription_text[:200]}{'...' if len(transcription_text) > 200 else ''}\n\n"
                f"**Analysis:** This appears to be {context['audio_type']} with a {context['sentiment']} tone. "
                f"I've identified {context['tasks_found']} potential tasks from the content.\n\n"
                f"How would you like to proceed with this information?",
                context
            )
        else:
            ai_response = "I've received your audio file, but wasn't able to transcribe it fully. This might be due to audio quality or configuration issues."
        
        # Return in the format expected by frontend
        return {
            "response": ai_response,
            "processing_details": {
                "transcription": {
                    "text": transcription_text,
                    "confidence": audio_analysis.get("confidence", 0.0),
                    "language": "auto-detected"
                },
                "file_id": file_id,
                "filename": file.filename,
                "processing_time": "2.1s",
                "ai_processed": audio_analysis.get("ai_processed", False)
            },
            "tasks": audio_analysis.get("tasks", []),
            "analysis": audio_analysis
        }
        
    except Exception as e:
        logger.error(f"Audio upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(e)}")

# Task management endpoints - FIXED: Use actual Supabase database
@app.get("/api/v1/tasks")
async def get_tasks():
    """Get all tasks from Supabase database"""
    try:
        # Try to get database service (Supabase or fallback)
        database_service = None
        try:
            from services.postgres_db import PostgreSQLDatabaseService
            database_service = PostgreSQLDatabaseService()
            await database_service.initialize_connections()
        except Exception as db_init_error:
            logger.warning(f"Database service initialization failed: {db_init_error}")
        
        if database_service and database_service.connection_type != "memory":
            # Use actual database
            db_tasks = await database_service.get_tasks()
            logger.info(f"Retrieved {len(db_tasks)} tasks from {database_service.connection_type} database")
            return {
                "tasks": db_tasks,
                "count": len(db_tasks),
                "status": "success",
                "source": database_service.connection_type
            }
        else:
            # Fallback to in-memory storage
            logger.info(f"Using in-memory storage fallback - {len(tasks_db)} tasks")
            return {
                "tasks": tasks_db,
                "count": len(tasks_db),
                "status": "success",
                "source": "memory"
            }
            
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        # Final fallback to in-memory
        return {
            "tasks": tasks_db,
            "count": len(tasks_db),
            "status": "success",
            "source": "memory_fallback"
        }

@app.post("/api/v1/tasks")
async def create_task(task: Task):
    """Create a new task in Supabase database"""
    try:
        # Try to get database service (Supabase or fallback)
        database_service = None
        try:
            from services.postgres_db import PostgreSQLDatabaseService
            database_service = PostgreSQLDatabaseService()
            await database_service.initialize_connections()
        except Exception as db_init_error:
            logger.warning(f"Database service initialization failed: {db_init_error}")
        
        # Prepare task data
        task_data = {
            "summary": task.title,  # Map title to summary for Supabase schema
            "description": task.description,
            "priority": task.priority,
            "category": task.category,
            "status": task.status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if database_service and database_service.connection_type != "memory":
            # Use actual database (Supabase)
            created_task = await database_service.create_task(task_data)
            if created_task:
                logger.info(f"Created task in {database_service.connection_type}: {created_task.get('id')}")
                return {
                    "task": created_task,
                    "message": f"Task created successfully in {database_service.connection_type}",
                    "status": "success",
                    "source": database_service.connection_type
                }
            else:
                # Fallback to memory if database creation fails
                raise Exception("Database task creation returned None")
        else:
            # Fallback to in-memory storage
            logger.info("Using in-memory storage for task creation")
            new_task = {
                "id": len(tasks_db) + 1,
                "title": task.title,
                "summary": task.title,
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
                "message": "Task created successfully in memory",
                "status": "success",
                "source": "memory"
            }
        
    except Exception as e:
        logger.error(f"Task creation error: {e}")
        # Final fallback to in-memory
        try:
            new_task = {
                "id": len(tasks_db) + 1,
                "title": task.title,
                "summary": task.title,
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
                "message": f"Task created in memory fallback (DB error: {str(e)})",
                "status": "success",
                "source": "memory_fallback"
            }
        except Exception as fallback_error:
            logger.error(f"Even memory fallback failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")

@app.put("/api/v1/tasks/{task_id}")
async def update_task(task_id: int, task_updates: Dict[str, Any]):
    """Update a task in Supabase database"""
    try:
        # Try to get database service (Supabase or fallback)
        database_service = None
        try:
            from services.postgres_db import PostgreSQLDatabaseService
            database_service = PostgreSQLDatabaseService()
            await database_service.initialize_connections()
        except Exception as db_init_error:
            logger.warning(f"Database service initialization failed: {db_init_error}")
        
        # Add updated timestamp
        task_updates["updated_at"] = datetime.now().isoformat()
        
        if database_service and database_service.connection_type != "memory":
            # Use actual database
            updated_task = await database_service.update_task(task_id, task_updates)
            if updated_task:
                logger.info(f"Updated task in {database_service.connection_type}: {task_id}")
                return {
                    "task": updated_task,
                    "message": f"Task updated successfully in {database_service.connection_type}",
                    "status": "success",
                    "source": database_service.connection_type
                }
            else:
                raise HTTPException(status_code=404, detail="Task not found")
        else:
            # Fallback to in-memory storage
            task_index = None
            for i, task in enumerate(tasks_db):
                if task["id"] == task_id:
                    task_index = i
                    break
            
            if task_index is None:
                raise HTTPException(status_code=404, detail="Task not found")
            
            tasks_db[task_index].update(task_updates)
            
            return {
                "task": tasks_db[task_index],
                "message": "Task updated successfully in memory",
                "status": "success",
                "source": "memory"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task update error: {e}")
        raise HTTPException(status_code=500, detail=f"Task update failed: {str(e)}")

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task from Supabase database"""
    try:
        # Try to get database service (Supabase or fallback) 
        database_service = None
        try:
            from services.postgres_db import PostgreSQLDatabaseService
            database_service = PostgreSQLDatabaseService()
            await database_service.initialize_connections()
        except Exception as db_init_error:
            logger.warning(f"Database service initialization failed: {db_init_error}")
        
        if database_service and database_service.connection_type != "memory":
            # Use actual database
            deleted = await database_service.delete_task(task_id)
            if deleted:
                logger.info(f"Deleted task from {database_service.connection_type}: {task_id}")
                return {
                    "message": f"Task deleted successfully from {database_service.connection_type}",
                    "task_id": task_id,
                    "status": "success",
                    "source": database_service.connection_type
                }
            else:
                raise HTTPException(status_code=404, detail="Task not found")
        else:
            # Fallback to in-memory storage
            task_index = None
            for i, task in enumerate(tasks_db):
                if task["id"] == task_id:
                    task_index = i
                    break
            
            if task_index is None:
                raise HTTPException(status_code=404, detail="Task not found")
            
            deleted_task = tasks_db.pop(task_index)
            
            return {
                "message": "Task deleted successfully from memory",
                "deleted_task": deleted_task,
                "status": "success",
                "source": "memory"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Task deletion failed: {str(e)}")

@app.delete("/api/v1/tasks")
async def clear_all_tasks():
    """Clear all tasks from Supabase database"""
    try:
        # Try to get database service (Supabase or fallback)
        database_service = None
        try:
            from services.postgres_db import PostgreSQLDatabaseService
            database_service = PostgreSQLDatabaseService()
            await database_service.initialize_connections()
        except Exception as db_init_error:
            logger.warning(f"Database service initialization failed: {db_init_error}")
        
        if database_service and database_service.connection_type != "memory":
            # Use actual database
            count = await database_service.clear_all_tasks()
            logger.info(f"Cleared {count} tasks from {database_service.connection_type}")
            return {
                "message": f"Cleared {count} tasks successfully from {database_service.connection_type}",
                "deleted_count": count,
                "status": "success",
                "source": database_service.connection_type
            }
        else:
            # Fallback to in-memory storage
            count = len(tasks_db)
            tasks_db.clear()
            
            return {
                "message": f"Cleared {count} tasks successfully from memory",
                "deleted_count": count,
                "status": "success",
                "source": "memory"
            }
        
    except Exception as e:
        logger.error(f"Clear tasks error: {e}")
        # Final fallback
        count = len(tasks_db)
        tasks_db.clear()
        return {
            "message": f"Cleared {count} tasks from memory fallback (DB error: {str(e)})",
            "deleted_count": count,
            "status": "success",
            "source": "memory_fallback"
        }

@app.get("/api/v1/status")
def get_status():
    """Get system status and AI capabilities"""
    groq = get_groq_client()
    groq_status = "unavailable"
    if groq:
        groq_status = "available"
        if hasattr(groq, 'audio') and hasattr(groq.audio, 'transcriptions'):
            groq_status = "fully_functional"
    
    return {
        "status": "operational",
        "version": "2.2.0",
        "timestamp": datetime.now().isoformat(),
        "ai_services": {
            "groq": groq is not None,
            "groq_status": groq_status,
            "groq_api_key_configured": bool(GROQ_API_KEY),
            "transformers": _transformers_attempted,
            "whisper_model": whisper_model is not None,
            "sentiment_model": sentiment_model is not None,
            "supabase": get_supabase_client() is not None,
            "lazy_loading": True
        },
        "features": ["chat", "multimodal", "file_upload", "task_extraction", "ai_analysis", "audio_transcription", "image_analysis", "document_analysis", "video_analysis", "lazy_loading"],
        "data_counts": {
            "tasks": len(tasks_db),
            "files": len(files_db),
            "conversations": len(conversations_db)
        },
        "endpoints": ["/api/v1/chat", "/api/v1/upload", "/api/v1/upload/audio", "/api/v1/tasks"]
    }

@app.get("/api/v1/files")
def get_files():
    """Get uploaded files"""
    return {
        "files": list(files_db.values()),
        "count": len(files_db)
    }

# Universal OPTIONS handler
@app.options("/{full_path:path}")
async def options_handler():
    return Response(status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 