import logging
import time
import asyncio
import base64
import os
from typing import Dict, Any, Optional, List
import httpx
from groq import Groq
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
import io
from config.settings import settings
from .monitoring import track_groq_call, track_huggingface_call

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.groq_api_key = settings.groq_api_key
        self.hf_api_key = settings.hf_api_key
        self.groq_model = settings.groq_model
        self.groq_client = None
        
        # Hugging Face API endpoints
        self.hf_base_url = "https://api-inference.huggingface.co/models"
        self.vision_models = {
            "image_captioning": "Salesforce/blip-image-captioning-large",
            "document_qa": "microsoft/DialoGPT-medium",  # Can be upgraded to better models
            "chart_analysis": "microsoft/pix2struct-base",
            "general_vision": "Salesforce/blip-image-captioning-large"  # Use BLIP for general vision too
        }
        self.audio_models = {
            "speech_to_text": "openai/whisper-large-v3"
        }
        
        # Initialize Groq client if API key is available
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("Groq API key not provided - using placeholder responses")
            
        # Check Hugging Face configuration
        if not self.hf_api_key:
            logger.warning("Hugging Face API key not provided - multimodal features will be limited")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for IntelliAssist.AI"""
        return """You are IntelliAssist.AI, an intelligent task management assistant designed to help users organize, prioritize, and complete their tasks efficiently.

Your capabilities include:
- Creating and organizing task lists
- Setting priorities and deadlines
- Breaking down complex projects into manageable steps
- Providing productivity tips and time management advice
- Analyzing uploaded documents, images, and audio files
- Offering smart suggestions based on user context

Your personality:
- Professional yet friendly
- Concise but thorough when needed
- Proactive in offering helpful suggestions
- Patient and encouraging
- Always focused on productivity and organization

Guidelines:
- Always be helpful and constructive
- Provide actionable advice
- Ask clarifying questions when needed
- Keep responses focused and relevant
- Use bullet points and structure when organizing information
- Encourage good productivity habits

Remember: You're here to make users more productive and organized. Always think about how you can help them achieve their goals efficiently."""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of AI services"""
        try:
            if not self.groq_client:
                return {
                    "groq_status": "not_configured",
                    "message": "Groq API key not provided"
                }
            
            # Test Groq connection with a simple request
            start_time = time.time()
            test_completion = await asyncio.create_task(
                asyncio.to_thread(
                    self.groq_client.chat.completions.create,
                    model=self.groq_model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
            )
            
            response_time = time.time() - start_time
            
            return {
                "groq_status": "healthy",
                "model": self.groq_model,
                "response_time": round(response_time, 3),
                "test_response": test_completion.choices[0].message.content[:50] if test_completion.choices else "No response"
            }
            
        except Exception as e:
            logger.error(f"AI health check failed: {str(e)}")
            return {
                "groq_status": "error",
                "error": str(e)
            }
    
    def _truncate_context(self, context: str, max_length: int = 500) -> str:
        """Truncate context to prevent token limit issues"""
        if len(context) <= max_length:
            return context
        return context[:max_length] + "... [truncated]"
    
    async def _call_huggingface_api(self, model_name: str, payload: Any, is_audio: bool = False) -> Dict[str, Any]:
        """
        Make API call to Hugging Face Inference API
        
        Args:
            model_name (str): HuggingFace model name
            payload: Request payload (dict for JSON, bytes for audio)
            is_audio (bool): Whether this is an audio API call
            
        Returns:
            Dict[str, Any]: API response
        """
        if not self.hf_api_key:
            logger.warning("HuggingFace API key not configured - returning placeholder response")
            return {
                "error": "HuggingFace API key not configured. Please add HF_API_KEY to your .env file.",
                "status": "not_configured",
                "suggestion": "Get a free API key from https://huggingface.co/settings/tokens"
            }
        
        url = f"{self.hf_base_url}/{model_name}"
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
        }
        
        # Set content type based on request type
        if is_audio:
            headers["Content-Type"] = "audio/webm"
        else:
            headers["Content-Type"] = "application/json"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for audio
                if is_audio:
                    response = await client.post(url, content=payload, headers=headers)
                else:
                    response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    return {"data": response.json(), "status": "success"}
                elif response.status_code == 503:
                    return {"error": "Model is loading, please wait", "status": "loading"}
                else:
                    logger.error(f"HF API error {response.status_code}: {response.text}")
                    return {
                        "error": f"API error: {response.status_code}",
                        "status": "error",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Hugging Face API call failed: {str(e)}")
            return {"error": str(e), "status": "error"}
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is not available. Please install with: pip install Pillow")
        
        try:
            # Optimize image size for API
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for most vision models)
                max_size = 1024
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return img_str
                
        except Exception as e:
            logger.error(f"Failed to encode image: {str(e)}")
            raise
    
    async def process_image(self, image_path: str, task_type: str = "general", include_chat_direction: bool = True) -> Dict[str, Any]:
        """
        Process image using vision AI models
        
        Args:
            image_path (str): Path to the image file
            task_type (str): Type of analysis (general, document, chart, meeting, planning)
            include_chat_direction (bool): Whether to add chat direction to the response
            
        Returns:
            Dict[str, Any]: Processing results with analysis and metadata
        """
        tracker = await track_huggingface_call("image_processing")
        async with tracker:
            try:
                logger.info(f"Processing image: {image_path} with task type: {task_type}")
                start_time = time.time()
                
                # Check if file exists
                if not os.path.exists(image_path):
                    return {
                        "status": "error",
                        "error": f"Image file not found: {image_path}"
                    }
                
                # Set request size (approximate file size)
                try:
                    file_size = os.path.getsize(image_path)
                    tracker.set_request_size(file_size)
                except:
                    pass
                
                # Try Hugging Face API first, fallback to local processing
                try:
                    result = await self._process_image_with_hf_api(image_path, task_type, include_chat_direction)
                    if result["status"] == "success":
                        tracker.set_status(200)
                        return result
                    else:
                        logger.warning(f"HF API failed: {result.get('error', 'Unknown error')}")
                except Exception as hf_error:
                    logger.warning(f"HF API processing failed: {str(hf_error)}")
                
                # Fallback to local processing
                logger.info("Falling back to local image processing")
                result = await self._process_image_locally(image_path, task_type, include_chat_direction)
                
                # Track response size
                if result.get("ai_insights"):
                    tracker.set_response_size(len(str(result["ai_insights"]).encode('utf-8')))
                
                tracker.set_status(200 if result["status"] == "success" else 500)
                return result
                
            except Exception as e:
                logger.error(f"Image processing failed: {str(e)}")
                tracker.set_status(500, str(e))
                return {
                    "status": "error",
                    "error": str(e),
                    "processing_time": 0
                }
    
    async def _process_image_locally(self, image_path: str, task_type: str, include_chat_direction: bool) -> Dict[str, Any]:
        """
        Process image locally using transformers library (if available)
        """
        try:
            # Try to import transformers and PIL
            from transformers import BlipProcessor, BlipForConditionalGeneration
            from PIL import Image
            import torch
            
            logger.info("Attempting local image processing...")
            
            # Load the model (this will be cached after first load)
            if not hasattr(self, '_blip_processor'):
                logger.info("Loading BLIP model for local image processing...")
                try:
                    # Use the base model for reliability
                    self._blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                    self._blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                    
                    # Use GPU if available
                    if torch.cuda.is_available():
                        self._blip_model = self._blip_model.to("cuda")
                        logger.info("BLIP model loaded on GPU")
                    else:
                        logger.info("BLIP model loaded on CPU")
                        
                    logger.info("✅ BLIP model loaded successfully")
                    
                except Exception as model_error:
                    logger.error(f"Failed to load BLIP model: {model_error}")
                    raise Exception(f"Model loading failed: {str(model_error)}")
            
            # Load and process the image
            try:
                image = Image.open(image_path).convert('RGB')
                logger.info(f"Image loaded: {image.size}")
            except Exception as img_error:
                logger.error(f"Failed to load image: {img_error}")
                raise Exception(f"Image loading failed: {str(img_error)}")
            
            # Process the image
            try:
                inputs = self._blip_processor(image, return_tensors="pt")
                
                # Move to GPU if available
                if torch.cuda.is_available() and hasattr(self._blip_model, 'device'):
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                # Generate caption
                with torch.no_grad():
                    generated_ids = self._blip_model.generate(**inputs, max_new_tokens=50, do_sample=False)
                    caption = self._blip_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                
                logger.info(f"Generated caption: {caption}")
                
                if caption and len(caption) > 0:
                    # Determine enhanced context based on image content
                    enhanced_task_type = self._determine_image_context(caption, task_type)
                    
                    # Generate AI insights using the enhanced vision prompt
                    vision_prompt = self._get_vision_prompt(enhanced_task_type)
                    insight_prompt = f"""Image Analysis: "{caption}"

{vision_prompt}

Based on this image content, provide structured, actionable recommendations that would help with task management and productivity. Be specific and practical."""

                    # Generate AI insights
                    ai_insights = await self.generate_response(insight_prompt, context=f"Image analysis - {enhanced_task_type}")
                    
                    # Add chat direction to the response if requested
                    if include_chat_direction:
                        enhanced_response = self._add_chat_direction(ai_insights.get("response", ""), "image")
                    else:
                        enhanced_response = ai_insights.get("response", "")
                    
                    return {
                        "status": "success",
                        "description": caption,
                        "confidence": 0.9,  # Local processing is generally reliable
                        "type": "local_caption",
                        "model_used": "Salesforce/blip-image-captioning-base (local)",
                        "context_type": enhanced_task_type,
                        "ai_insights": enhanced_response,
                        "tasks": ai_insights.get("tasks", []),
                        "suggestions": self._extract_suggestions_from_response(ai_insights.get("response", "")),
                        "metadata": {
                            "original_task_type": task_type,
                            "detected_context": enhanced_task_type,
                            "caption_length": len(caption),
                            "processing_enhanced": True
                        }
                    }
                else:
                    raise Exception("Empty caption generated")
                    
            except Exception as proc_error:
                logger.error(f"Failed to process image: {proc_error}")
                raise Exception(f"Image processing failed: {str(proc_error)}")
            
        except ImportError as e:
            logger.debug(f"Local image processing dependencies not available: {e}")
            raise Exception("Local image processing not available - missing dependencies")
        except Exception as e:
            logger.error(f"Local image processing failed: {e}")
            raise Exception(f"Local image processing error: {str(e)}")
    
    def _get_vision_prompt(self, task_type: str) -> str:
        """Get appropriate prompt for vision tasks"""
        prompts = {
            "document": """Analyze this document and provide specific, actionable insights for task management:

1. CONTENT ANALYSIS: What are the key topics, decisions, or information presented?
2. ACTIONABLE TASKS: What specific tasks, deadlines, or action items can be extracted?
3. PRIORITIES: What appears to be most urgent or important?
4. NEXT STEPS: What logical next steps or follow-up actions should be taken?
5. ORGANIZATION: How can this information be best organized for productivity?

Focus on practical, implementable suggestions that would help someone be more productive and organized.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations.""",

            "chart": """Analyze this chart/diagram and provide task management insights:

1. DATA INSIGHTS: What key trends, patterns, or findings does this data show?
2. DECISION POINTS: What decisions or actions does this data suggest?
3. MONITORING TASKS: What metrics or areas should be tracked based on this data?
4. IMPROVEMENT OPPORTUNITIES: What areas for improvement or optimization are evident?
5. ACTION ITEMS: What specific tasks should be created based on these insights?

Provide specific, data-driven recommendations for task management and productivity.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations.""",

            "general": """Analyze this image comprehensively for task management and productivity insights:

1. VISUAL CONTENT: What do you see in this image? (objects, text, people, activities)
2. WORK-RELATED ELEMENTS: Identify any tasks, notes, schedules, or work-related content
3. ACTIONABLE INSIGHTS: What specific actions or tasks can be derived from this image?
4. PRODUCTIVITY SUGGESTIONS: How can this information be used to improve organization or efficiency?
5. CONTEXT CLUES: What context or situation does this image suggest, and what follow-up actions are needed?

Be specific and practical in your suggestions, focusing on actionable task management advice.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations.""",

            "meeting": """Analyze this meeting-related content and extract task management value:

1. MEETING CONTENT: What meeting information, agenda items, or discussion points are visible?
2. ACTION ITEMS: What specific tasks or assignments can be identified?
3. DEADLINES: Are there any dates, timelines, or deadlines mentioned?
4. RESPONSIBILITIES: Who is responsible for what actions?
5. FOLLOW-UP: What follow-up meetings, communications, or check-ins are needed?

Focus on extracting concrete, assignable tasks and organizational insights.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations.""",

            "planning": """Analyze this planning or organizational content:

1. PLANNING ELEMENTS: What planning information, schedules, or organizational content is shown?
2. TASK BREAKDOWN: How can larger goals be broken down into specific, manageable tasks?
3. TIMELINE: What is the suggested timeline or sequence of activities?
4. RESOURCE NEEDS: What resources, tools, or support might be needed?
5. MILESTONES: What key milestones or checkpoints should be established?

Provide structured, implementable planning and task management recommendations.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations."""
        }
        return prompts.get(task_type, prompts["general"])
    
    def _process_vision_response(self, data: Any, task_type: str) -> Dict[str, Any]:
        """Process vision model response into structured format"""
        try:
            if task_type == "caption" and isinstance(data, list) and len(data) > 0:
                # BLIP captioning response
                return {
                    "description": data[0].get("generated_text", ""),
                    "confidence": data[0].get("score", 0.0),
                    "type": "caption"
                }
            elif isinstance(data, list) and len(data) > 0:
                # VQA response
                return {
                    "description": data[0].get("answer", ""),
                    "confidence": data[0].get("score", 0.0),
                    "type": "analysis"
                }
            else:
                return {
                    "description": "Could not process image",
                    "confidence": 0.0,
                    "type": "error"
                }
        except Exception as e:
            logger.error(f"Failed to process vision response: {str(e)}")
            return {
                "description": f"Error processing response: {str(e)}",
                "confidence": 0.0,
                "type": "error"
            }
    
    async def process_audio(self, audio_path: str, include_chat_direction: bool = True) -> Dict[str, Any]:
        """
        Process audio using Hugging Face Whisper model for speech-to-text
        
        Args:
            audio_path (str): Path to the audio file
            include_chat_direction (bool): Whether to add chat direction to the response
        """
        tracker = await track_huggingface_call("whisper/speech-to-text")
        async with tracker:
            start_time = time.time()
            
            try:
                logger.info(f"Processing audio: {audio_path}")
                
                # Check if file exists
                if not os.path.exists(audio_path):
                    tracker.set_status(404, "Audio file not found")
                    return {
                        "status": "error",
                        "error": "Audio file not found",
                        "processing_time": 0
                    }
                
                file_size = os.path.getsize(audio_path)
                logger.info(f"Audio file size: {file_size} bytes")
                
                # Track request size
                tracker.set_request_size(file_size)
                
                if file_size > 25 * 1024 * 1024:  # 25MB absolute limit
                    tracker.set_status(413, "Audio file too large")
                    return {
                        "status": "error", 
                        "error": "Audio file too large (max 25MB)",
                        "processing_time": round(time.time() - start_time, 3)
                    }
                
                # Warn about potential timeout for larger files
                if file_size > 5 * 1024 * 1024:  # 5MB recommended limit
                    logger.warning(f"Large audio file ({file_size / (1024*1024):.1f}MB) - may timeout")
                
                # Check if HuggingFace API key is available
                if not self.hf_api_key:
                    logger.warning("HuggingFace API key not configured")
                    tracker.set_status(503, "HuggingFace API key not configured")
                    
                    helpful_response = await self.generate_response(
                        "The user uploaded an audio file. Please acknowledge this and explain that transcription requires HuggingFace API configuration.",
                        context="Audio upload - API not configured"
                    )
                    
                    response_data = {
                        "status": "success",
                        "transcription": {
                            "text": "Audio uploaded successfully! To enable transcription, please configure your HuggingFace API key.",
                            "confidence": 0.0,
                            "language": "unknown"
                        },
                        "ai_response": helpful_response,
                        "model_used": "placeholder",
                        "processing_time": round(time.time() - start_time, 3)
                    }
                    
                    tracker.set_response_size(len(str(response_data).encode('utf-8')))
                    return response_data
                
                # Read audio file
                with open(audio_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                # Call HuggingFace Whisper API
                model_name = self.audio_models["speech_to_text"]
                url = f"{self.hf_base_url}/{model_name}"
                
                # Determine content type based on file extension
                content_type = "audio/wav"  # Default
                if audio_path.lower().endswith('.mp3'):
                    content_type = "audio/mpeg"
                elif audio_path.lower().endswith('.wav'):
                    content_type = "audio/wav"
                elif audio_path.lower().endswith('.webm'):
                    content_type = "audio/webm"
                elif audio_path.lower().endswith('.ogg'):
                    content_type = "audio/ogg"
                elif audio_path.lower().endswith('.flac'):
                    content_type = "audio/flac"
                
                headers = {
                    "Authorization": f"Bearer {self.hf_api_key}",
                    "Content-Type": content_type
                }
                
                logger.info(f"Calling HuggingFace API: {url}")
                
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            url, 
                            content=audio_data, 
                            headers=headers
                        )
                        
                        logger.info(f"HuggingFace API response: {response.status_code}")
                        
                        # Track response
                        tracker.set_status(response.status_code)
                        
                        if response.status_code == 200:
                            data = response.json()
                            logger.info(f"Transcription response: {data}")
                            
                            # Track successful response size
                            tracker.set_response_size(len(response.content))
                            
                            # Process transcription result
                            transcription = self._process_audio_response(data)
                            
                            if transcription.get("text") and transcription["text"].strip():
                                # Generate AI response based on transcribed text with enhanced prompt
                                enhanced_audio_prompt = f"""The user provided an audio recording that was transcribed as: "{transcription['text']}"

Please analyze this transcribed content and provide comprehensive task management insights:

1. CONTENT SUMMARY: What is the main topic or purpose of this audio?
2. ACTION ITEMS: What specific tasks, assignments, or action items are mentioned?
3. DEADLINES & TIMELINES: Are there any dates, deadlines, or time-sensitive items?
4. PEOPLE & RESPONSIBILITIES: Who is mentioned and what are their responsibilities?
5. FOLLOW-UP ACTIONS: What follow-up actions, meetings, or check-ins are needed?
6. ORGANIZATION SUGGESTIONS: How can this information be best organized for productivity?

Focus on extracting actionable, specific tasks and providing practical productivity recommendations.

At the end of your response, encourage the user to use the Chat feature for further assistance with implementing these recommendations."""

                                llama_response = await self.generate_response(
                                    enhanced_audio_prompt,
                                    context="Voice message transcription - enhanced analysis"
                                )
                                
                                # Add chat direction to the response if requested
                                enhanced_llama_response = llama_response.copy()
                                if include_chat_direction:
                                    enhanced_llama_response["response"] = self._add_chat_direction(
                                        llama_response.get("response", ""), "audio"
                                    )
                                else:
                                    enhanced_llama_response["response"] = llama_response.get("response", "")
                                
                                processing_time = time.time() - start_time
                                
                                return {
                                    "status": "success",
                                    "transcription": transcription,
                                    "ai_response": enhanced_llama_response,
                                    "model_used": model_name,
                                    "processing_time": round(processing_time, 3),
                                    "suggestions": self._extract_suggestions_from_response(llama_response.get("response", "")),
                                    "metadata": {
                                        "transcription_length": len(transcription.get("text", "")),
                                        "analysis_enhanced": True,
                                        "audio_file_size": file_size
                                    }
                                }
                            else:
                                # Fallback if no text transcribed
                                helpful_response = await self.generate_response(
                                    "The user uploaded an audio file, but no speech was detected. Please provide helpful guidance.",
                                    context="Audio transcription - no speech detected"
                                )
                                
                                return {
                                    "status": "success",
                                    "transcription": {
                                        "text": "No speech detected in the audio file. Please try recording again with clearer audio.",
                                        "confidence": 0.0,
                                        "language": "unknown"
                                    },
                                    "ai_response": helpful_response,
                                    "model_used": model_name,
                                    "processing_time": round(time.time() - start_time, 3)
                                }
                        
                        elif response.status_code == 503:
                            # Model is loading
                            logger.info("HuggingFace model is loading")
                            tracker.set_response_size(len(response.content))
                            
                            helpful_response = await self.generate_response(
                                "The speech-to-text model is currently loading. Please try again in a moment.",
                                context="Model loading"
                            )
                            
                            return {
                                "status": "success",
                                "transcription": {
                                    "text": "The speech-to-text model is currently loading. Please try again in a moment.",
                                    "confidence": 0.0,
                                    "language": "unknown"
                                },
                                "ai_response": helpful_response,
                                "model_used": "loading",
                                "processing_time": round(time.time() - start_time, 3)
                            }
                            
                        else:
                            error_text = response.text
                            logger.error(f"HuggingFace API error {response.status_code}: {error_text}")
                            
                            tracker.set_response_size(len(response.content))
                            tracker.set_status(response.status_code, error_text)
                            
                            helpful_response = await self.generate_response(
                                f"There was an issue with the audio transcription service (error {response.status_code}). Please try again later.",
                                context="Transcription service error"
                            )
                            
                            return {
                                "status": "success",
                                "transcription": {
                                    "text": f"Audio transcription temporarily unavailable (service error {response.status_code}). Please try again later.",
                                    "confidence": 0.0,
                                    "language": "unknown"
                                },
                                "ai_response": helpful_response,
                                "model_used": "error",
                                "processing_time": round(time.time() - start_time, 3)
                            }
                            
                except httpx.TimeoutException:
                    logger.warning("Audio transcription timeout")
                    tracker.set_status(408, "Request timeout")
                    
                    helpful_response = await self.generate_response(
                        "The audio file took too long to process. This might be because it's too long or the service is busy.",
                        context="Transcription timeout"
                    )
                    
                    return {
                        "status": "success",
                        "transcription": {
                            "text": "Audio processing timeout - the file may be too long or the service is busy. Please try with a shorter audio clip.",
                            "confidence": 0.0,
                            "language": "unknown"
                        },
                        "ai_response": helpful_response,
                        "model_used": "timeout",
                        "processing_time": round(time.time() - start_time, 3)
                    }
                    
                except Exception as api_error:
                    logger.error(f"Audio API call failed: {str(api_error)}")
                    tracker.set_status(500, str(api_error))
                    
                    helpful_response = await self.generate_response(
                        "There was a technical issue with audio transcription. The file was uploaded successfully but couldn't be processed.",
                        context="Transcription technical error"
                    )
                    
                    return {
                        "status": "success",
                        "transcription": {
                            "text": f"Audio uploaded successfully, but transcription failed due to a technical issue: {str(api_error)}",
                            "confidence": 0.0,
                            "language": "unknown"
                        },
                        "ai_response": helpful_response,
                        "model_used": "error",
                        "processing_time": round(time.time() - start_time, 3)
                    }
                
            except Exception as e:
                logger.error(f"Audio processing failed: {str(e)}", exc_info=True)
                tracker.set_status(500, str(e))
                
                error_response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
                tracker.set_response_size(len(error_response.encode('utf-8')))
                
                return {
                    "status": "error",
                    "error": f"Audio processing failed: {str(e)}",
                    "processing_time": round(time.time() - start_time, 3)
                }
    
    def _process_audio_response(self, data: Any) -> Dict[str, Any]:
        """Process audio transcription response"""
        try:
            if isinstance(data, dict) and "text" in data:
                # Whisper direct response
                return {
                    "text": data["text"],
                    "confidence": data.get("confidence", 1.0),
                    "language": data.get("language", "unknown")
                }
            elif isinstance(data, list) and len(data) > 0:
                # Array response format
                first_result = data[0]
                if isinstance(first_result, dict):
                    return {
                        "text": first_result.get("text", ""),
                        "confidence": first_result.get("score", 1.0),
                        "language": first_result.get("language", "unknown")  
                    }
            elif isinstance(data, str):
                # Simple string response
                return {
                    "text": data,
                    "confidence": 1.0,
                    "language": "unknown"
                }
            
            return {
                "text": "",
                "confidence": 0.0,
                "language": "unknown",
                "error": "Could not parse transcription"
            }
            
        except Exception as e:
            logger.error(f"Failed to process audio response: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": "unknown", 
                "error": str(e)
            }
    
    async def process_multimodal_input(self, text: str = None, image_path: str = None, 
                                     audio_path: str = None, context: str = None) -> Dict[str, Any]:
        """
        Process multimodal input combining text, image, and/or audio
        
        Args:
            text (str): Text input
            image_path (str): Path to image file
            audio_path (str): Path to audio file
            context (str): Conversation context
            
        Returns:
            Dict[str, Any]: Combined processing results
        """
        start_time = time.time()
        results = {
            "status": "success",
            "inputs_processed": [],
            "combined_response": "",
            "processing_time": 0
        }
        
        try:
            logger.info(f"Processing multimodal input - Text: {bool(text)}, Image: {bool(image_path)}, Audio: {bool(audio_path)}")
            
            combined_content = ""
            
            # Process audio first (speech-to-text)
            if audio_path:
                audio_result = await self.process_audio(audio_path, include_chat_direction=False)
                results["audio_processing"] = audio_result
                results["inputs_processed"].append("audio")
                
                if audio_result.get("status") == "success":
                    transcribed_text = audio_result["transcription"]["text"]
                    combined_content += f"Voice message: {transcribed_text}\n"
                    logger.info(f"Transcribed audio: {transcribed_text[:100]}...")
            
            # Process image
            if image_path:
                image_result = await self.process_image(image_path, "general", include_chat_direction=False)
                results["image_processing"] = image_result
                results["inputs_processed"].append("image")
                
                if image_result.get("status") == "success":
                    image_description = image_result["analysis"]["description"]
                    combined_content += f"Image content: {image_description}\n"
                    logger.info(f"Analyzed image: {image_description[:100]}...")
            
            # Add text input
            if text:
                combined_content += f"Text message: {text}\n"
                results["inputs_processed"].append("text")
            
            # Generate combined AI response
            if combined_content:
                prompt = f"""I have received multimodal input from a user:

{combined_content}

Please provide a comprehensive response that addresses all the input types and relates them to task management and productivity. Be helpful and actionable."""

                ai_response = await self.generate_response(prompt, context)
                results["combined_response"] = ai_response.get("response", "")
                results["ai_metadata"] = {
                    "model": ai_response.get("model"),
                    "tokens_used": ai_response.get("tokens_used"),
                    "response_time": ai_response.get("response_time")
                }
            else:
                results["status"] = "error"
                results["error"] = "No valid input provided"
            
            results["processing_time"] = round(time.time() - start_time, 3)
            logger.info(f"Multimodal processing completed in {results['processing_time']}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Multimodal processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": round(time.time() - start_time, 3)
            }
        
    def _extract_tasks_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Extract task information from AI response text
        
        Args:
            response_text (str): AI response text
            
        Returns:
            List[Dict[str, Any]]: List of extracted tasks
        """
        tasks = []
        
        # Keywords that indicate task-related content
        task_indicators = [
            'plan', 'task', 'todo', 'step', 'action', 'schedule', 'organize',
            'deadline', 'project', 'complete', 'finish', 'work on', 'need to'
        ]
        
        # Check if response contains task-related content
        response_lower = response_text.lower()
        has_tasks = any(indicator in response_lower for indicator in task_indicators)
        
        if not has_tasks:
            return tasks
        
        # Split response into lines for processing
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered lists, bullet points, or task-like patterns
            task_patterns = [
                r'^\d+\.\s*(.+)',  # 1. Task description
                r'^[-*•]\s*(.+)',  # - Task description or * Task description
                r'^(?:task|step|action)(?:\s*\d+)?[:\s]+(.+)',  # Task: description
                r'(?:you should|need to|plan to|will)\s+(.+)',  # Action phrases
            ]
            
            for pattern in task_patterns:
                import re
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    task_text = match.group(1).strip()
                    
                    # Skip very short or generic text
                    if len(task_text) < 10 or task_text.lower() in ['continue', 'next', 'done']:
                        continue
                    
                    # Determine priority based on keywords
                    priority = 'medium'
                    if any(word in task_text.lower() for word in ['urgent', 'asap', 'critical', 'important']):
                        priority = 'high'
                    elif any(word in task_text.lower() for word in ['later', 'eventually', 'when possible']):
                        priority = 'low'
                    
                    # Determine category based on content
                    category = 'general'
                    if any(word in task_text.lower() for word in ['meeting', 'call', 'email', 'contact']):
                        category = 'communication'
                    elif any(word in task_text.lower() for word in ['research', 'analyze', 'study', 'learn']):
                        category = 'research'
                    elif any(word in task_text.lower() for word in ['create', 'build', 'develop', 'design']):
                        category = 'development'
                    elif any(word in task_text.lower() for word in ['plan', 'organize', 'schedule']):
                        category = 'planning'
                    
                    task = {
                        'title': task_text[:100],  # Limit title length
                        'summary': task_text,
                        'status': 'pending',
                        'priority': priority,
                        'category': category
                    }
                    tasks.append(task)
                    break  # Only match first pattern per line
        
        # If no structured tasks found but response seems task-related, create a general task
        if not tasks and has_tasks and len(response_text) > 20:
            # Create a summary task from the response
            summary = response_text[:200].strip()
            if summary.endswith('.'):
                summary = summary[:-1]
            
            task = {
                'title': f"Follow AI recommendations",
                'summary': summary + "...",
                'status': 'pending',
                'priority': 'medium',
                'category': 'ai-generated'
            }
            tasks.append(task)
        
        return tasks

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response using Groq API
        
        Args:
            prompt (str): User input prompt
            context (str, optional): Conversation context
            
        Returns:
            Dict[str, Any]: AI response with metadata and extracted tasks
        """
        tracker = await track_groq_call("chat/completions")
        async with tracker:
            try:
                logger.info(f"Generating AI response for prompt length: {len(prompt)}")
                start_time = time.time()
                
                # Track request size
                tracker.set_request_size(len(prompt.encode('utf-8')))
                
                # If no Groq client available, use placeholder
                if not self.groq_client:
                    logger.warning("Groq client not available, using placeholder response")
                    await asyncio.sleep(0.5)  # Simulate delay
                    ai_response = f"[PLACEHOLDER MODE] You said: {prompt}\n\nI'm IntelliAssist.AI, ready to help with your tasks! To enable full AI capabilities, please add your Groq API key to the .env file."
                    
                    tracker.set_response_size(len(ai_response.encode('utf-8')))
                    tracker.set_status(503, "Groq API key not configured")
                    
                    response_time = time.time() - start_time
                    return {
                        "response": ai_response,
                        "model": self.groq_model,
                        "response_time": round(response_time, 3),
                        "tokens_used": len(prompt.split()) + len(ai_response.split()),
                        "status": "placeholder",
                        "tasks": []
                    }
                
                # Prepare messages for the conversation
                messages = [
                    {"role": "system", "content": self._get_system_prompt()}
                ]
                
                # Add context if provided
                if context:
                    truncated_context = self._truncate_context(context)
                    messages.append({"role": "assistant", "content": f"Previous context: {truncated_context}"})
                
                # Add user message
                messages.append({"role": "user", "content": prompt})
                
                # Make the API call to Groq
                try:
                    completion = await asyncio.create_task(
                        asyncio.to_thread(
                            self.groq_client.chat.completions.create,
                            model=self.groq_model,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=1024,
                            top_p=1,
                            stop=None,
                            stream=False
                        )
                    )
                    
                    ai_response = completion.choices[0].message.content
                    tokens_used = completion.usage.total_tokens if completion.usage else 0
                    
                    # Track successful response
                    tracker.set_response_size(len(ai_response.encode('utf-8')))
                    tracker.set_status(200)
                    
                    response_time = time.time() - start_time
                    
                    # Extract tasks from the AI response
                    extracted_tasks = self._extract_tasks_from_response(ai_response)
                    
                    result = {
                        "response": ai_response,
                        "model": self.groq_model,
                        "response_time": round(response_time, 3),
                        "tokens_used": tokens_used,
                        "status": "success",
                        "tasks": extracted_tasks
                    }
                    
                    logger.info(f"Groq API response generated successfully in {response_time:.3f}s, tokens: {tokens_used}, tasks extracted: {len(extracted_tasks)}")
                    return result
                    
                except Exception as api_error:
                    logger.error(f"Groq API error: {str(api_error)}")
                    
                    # Track API error
                    tracker.set_status(500, str(api_error))
                    
                    # Fallback to a helpful error message
                    ai_response = "I'm experiencing some technical difficulties connecting to my AI systems. Please try again in a moment, or check that your API credentials are properly configured."
                    
                    tracker.set_response_size(len(ai_response.encode('utf-8')))
                    
                    response_time = time.time() - start_time
                    return {
                        "response": ai_response,
                        "model": self.groq_model,
                        "response_time": round(response_time, 3),
                        "tokens_used": 0,
                        "status": "api_error",
                        "error": str(api_error),
                        "tasks": []
                    }
                
            except Exception as e:
                logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
                
                # Track general error
                tracker.set_status(500, str(e))
                
                error_response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
                tracker.set_response_size(len(error_response.encode('utf-8')))
                
                return {
                    "response": error_response,
                    "model": self.groq_model,
                    "response_time": 0,
                    "tokens_used": 0,
                    "status": "error",
                    "error": str(e),
                    "tasks": []
                }

    def _determine_image_context(self, caption: str, original_task_type: str) -> str:
        """Determine more specific image context based on caption content"""
        caption_lower = caption.lower()
        
        # Check for meeting-related content
        meeting_keywords = ['meeting', 'presentation', 'slide', 'whiteboard', 'projector', 'conference', 'discussion']
        if any(keyword in caption_lower for keyword in meeting_keywords):
            return "meeting"
        
        # Check for planning/organizational content
        planning_keywords = ['calendar', 'schedule', 'plan', 'timeline', 'chart', 'graph', 'diagram', 'list', 'notes']
        if any(keyword in caption_lower for keyword in planning_keywords):
            return "planning"
        
        # Check for document content
        document_keywords = ['document', 'paper', 'text', 'book', 'report', 'form', 'contract']
        if any(keyword in caption_lower for keyword in document_keywords):
            return "document"
        
        # Check for chart/data visualization
        chart_keywords = ['chart', 'graph', 'data', 'statistics', 'numbers', 'percentage', 'bar', 'pie']
        if any(keyword in caption_lower for keyword in chart_keywords):
            return "chart"
        
        # Return original task type if no specific context detected
        return original_task_type

    def _extract_suggestions_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract structured suggestions from AI response"""
        suggestions = []
        
        if not response_text:
            return suggestions
        
        lines = response_text.split('\n')
        current_category = "general"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect category headers
            if any(header in line.upper() for header in ['CONTENT ANALYSIS', 'ACTIONABLE TASKS', 'PRIORITIES', 'NEXT STEPS', 'ORGANIZATION']):
                current_category = line.lower().replace(':', '').strip()
                continue
            elif any(header in line.upper() for header in ['DATA INSIGHTS', 'DECISION POINTS', 'MONITORING TASKS']):
                current_category = line.lower().replace(':', '').strip()
                continue
            elif any(header in line.upper() for header in ['VISUAL CONTENT', 'WORK-RELATED ELEMENTS', 'ACTIONABLE INSIGHTS']):
                current_category = line.lower().replace(':', '').strip()
                continue
            
            # Extract numbered or bulleted suggestions
            suggestion_patterns = [
                r'^\d+\.\s*(.+)',  # 1. Suggestion
                r'^[-*•]\s*(.+)',  # - Suggestion or * Suggestion
                r'^(?:suggestion|recommendation|action)(?:\s*\d+)?[:\s]+(.+)',  # Action: suggestion
            ]
            
            for pattern in suggestion_patterns:
                import re
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    suggestion_text = match.group(1).strip()
                    
                    if len(suggestion_text) > 15:  # Filter out very short suggestions
                        # Determine priority based on keywords
                        priority = 'medium'
                        if any(word in suggestion_text.lower() for word in ['urgent', 'immediately', 'asap', 'critical']):
                            priority = 'high'
                        elif any(word in suggestion_text.lower() for word in ['consider', 'eventually', 'when possible']):
                            priority = 'low'
                        
                        suggestion = {
                            'text': suggestion_text,
                            'category': current_category,
                            'priority': priority,
                            'actionable': any(word in suggestion_text.lower() for word in ['create', 'schedule', 'review', 'update', 'contact', 'organize'])
                        }
                        suggestions.append(suggestion)
                    break
        
        return suggestions

    def _add_chat_direction(self, response: str, content_type: str = "content") -> str:
        """Add chat direction at the end of AI responses to guide users to further assistance"""
        chat_directions = {
            "image": "💬 **Need more help?** Use the Chat feature to ask me specific questions about this image, create tasks from these insights, or get personalized recommendations for your workflow!",
            "audio": "💬 **Want to dive deeper?** Head over to the Chat section to discuss these transcription results, create action items, or get help organizing these insights into your task management system!",
            "document": "💬 **Ready for next steps?** Visit the Chat feature to ask follow-up questions about this document, get help implementing these recommendations, or create a detailed action plan!",
            "general": "💬 **Looking for more assistance?** Try the Chat feature to ask specific questions, get personalized task management advice, or explore how to implement these insights in your workflow!"
        }
        
        direction = chat_directions.get(content_type, chat_directions["general"])
        
        # Add some spacing and the direction
        if response.strip():
            return f"{response}\n\n---\n\n{direction}"
        else:
            return direction

# Global AI service instance
ai_service = AIService() 