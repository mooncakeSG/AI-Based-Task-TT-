import logging
import time
import asyncio
import base64
import os
from typing import Dict, Any, Optional, List
import httpx
from groq import Groq
from PIL import Image
import io
from config.settings import settings

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
            "general_vision": "Salesforce/blip2-opt-2.7b"
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
    
    async def _call_huggingface_api(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API call to Hugging Face Inference API
        
        Args:
            model_name (str): HuggingFace model name
            payload (dict): Request payload
            
        Returns:
            Dict[str, Any]: API response
        """
        if not self.hf_api_key:
            return {
                "error": "Hugging Face API key not configured",
                "status": "not_configured"
            }
        
        url = f"{self.hf_base_url}/{model_name}"
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    return {"data": response.json(), "status": "success"}
                elif response.status_code == 503:
                    return {"error": "Model is loading, please wait", "status": "loading"}
                else:
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
    
    async def process_image(self, image_path: str, task_type: str = "general") -> Dict[str, Any]:
        """
        Process image using Hugging Face vision models
        
        Args:
            image_path (str): Path to image file
            task_type (str): Type of analysis (general, document, chart, caption)
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing image: {image_path}, task: {task_type}")
            
            # Select appropriate model based on task
            model_map = {
                "caption": "image_captioning",
                "document": "document_qa", 
                "chart": "chart_analysis",
                "general": "general_vision"
            }
            
            model_key = model_map.get(task_type, "general_vision")
            model_name = self.vision_models[model_key]
            
            # Encode image
            image_b64 = self._encode_image_to_base64(image_path)
            
            # Prepare payload based on model type
            if task_type == "caption":
                # For image captioning
                payload = {"inputs": image_b64}
            else:
                # For VQA models
                payload = {
                    "inputs": {
                        "image": image_b64,
                        "question": self._get_vision_prompt(task_type)
                    }
                }
            
            # Call Hugging Face API
            result = await self._call_huggingface_api(model_name, payload)
            
            if result["status"] == "success":
                # Process the response
                analysis = self._process_vision_response(result["data"], task_type)
                
                # Generate contextual response using LLaMA
                if analysis.get("description"):
                    llama_response = await self.generate_response(
                        f"I've analyzed an image and found: {analysis['description']}. Please provide helpful insights about this in the context of task management and productivity.",
                        context="Image analysis for task management"
                    )
                    
                    analysis["ai_insights"] = llama_response.get("response", "")
                
                processing_time = time.time() - start_time
                
                return {
                    "status": "success",
                    "analysis": analysis,
                    "model_used": model_name,
                    "task_type": task_type,
                    "processing_time": round(processing_time, 3)
                }
            else:
                return {
                    "status": result["status"],
                    "error": result.get("error", "Unknown error"),
                    "processing_time": round(time.time() - start_time, 3)
                }
                
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": round(time.time() - start_time, 3)
            }
    
    def _get_vision_prompt(self, task_type: str) -> str:
        """Get appropriate prompt for vision tasks"""
        prompts = {
            "document": "What text and important information can you extract from this document?",
            "chart": "Describe this chart or diagram. What data does it show?",
            "general": "What do you see in this image? Focus on any tasks, notes, or work-related content."
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
    
    async def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Process audio using Hugging Face Whisper model for speech-to-text
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            Dict[str, Any]: Transcription results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing audio: {audio_path}")
            
            # Check if file exists and get file info
            if not os.path.exists(audio_path):
                return {
                    "status": "error",
                    "error": "Audio file not found",
                    "processing_time": 0
                }
            
            file_size = os.path.getsize(audio_path)
            if file_size > 25 * 1024 * 1024:  # 25MB limit for most APIs
                return {
                    "status": "error", 
                    "error": "Audio file too large (max 25MB)",
                    "processing_time": round(time.time() - start_time, 3)
                }
            
            # Read and encode audio file
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_b64 = base64.b64encode(audio_data).decode()
            
            # Use Whisper model for transcription
            model_name = self.audio_models["speech_to_text"]
            payload = {"inputs": audio_b64}
            
            # Call Hugging Face API
            result = await self._call_huggingface_api(model_name, payload)
            
            if result["status"] == "success":
                # Process transcription result
                transcription = self._process_audio_response(result["data"])
                
                if transcription.get("text"):
                    # Generate AI response based on transcribed text
                    llama_response = await self.generate_response(
                        transcription["text"],
                        context="Voice message transcription"
                    )
                    
                    processing_time = time.time() - start_time
                    
                    return {
                        "status": "success",
                        "transcription": transcription,
                        "ai_response": llama_response,
                        "model_used": model_name,
                        "processing_time": round(processing_time, 3)
                    }
                else:
                    return {
                        "status": "error",
                        "error": "No transcription generated",
                        "processing_time": round(time.time() - start_time, 3)
                    }
            else:
                return {
                    "status": result["status"],
                    "error": result.get("error", "Unknown error"),
                    "processing_time": round(time.time() - start_time, 3)
                }
                
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
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
                audio_result = await self.process_audio(audio_path)
                results["audio_processing"] = audio_result
                results["inputs_processed"].append("audio")
                
                if audio_result.get("status") == "success":
                    transcribed_text = audio_result["transcription"]["text"]
                    combined_content += f"Voice message: {transcribed_text}\n"
                    logger.info(f"Transcribed audio: {transcribed_text[:100]}...")
            
            # Process image
            if image_path:
                image_result = await self.process_image(image_path, "general")
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
                        'status': 'todo',
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
                'status': 'todo',
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
        try:
            logger.info(f"Generating AI response for prompt length: {len(prompt)}")
            start_time = time.time()
            
            # If no Groq client available, use placeholder
            if not self.groq_client:
                logger.warning("Groq client not available, using placeholder response")
                await asyncio.sleep(0.5)  # Simulate delay
                ai_response = f"[PLACEHOLDER MODE] You said: {prompt}\n\nI'm IntelliAssist.AI, ready to help with your tasks! To enable full AI capabilities, please add your Groq API key to the .env file."
                
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
                # Fallback to a helpful error message
                ai_response = "I'm experiencing some technical difficulties connecting to my AI systems. Please try again in a moment, or check that your API credentials are properly configured."
                
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
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "model": self.groq_model,
                "response_time": 0,
                "tokens_used": 0,
                "status": "error",
                "error": str(e),
                "tasks": []
            }
    
    async def process_image(self, image_path: str, prompt: str = "Describe this image") -> Dict[str, Any]:
        """
        Process image using Hugging Face Vision API (placeholder implementation)
        
        Args:
            image_path (str): Path to uploaded image
            prompt (str): Optional prompt for image analysis
            
        Returns:
            Dict[str, Any]: Image analysis result
        """
        try:
            logger.info(f"Processing image: {image_path}")
            start_time = time.time()
            
            # Simulate processing delay
            await asyncio.sleep(1.0)
            
            # TODO: Replace with actual Hugging Face API call
            # import requests
            # headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            # with open(image_path, "rb") as f:
            #     data = f.read()
            # response = requests.post(HF_IMAGE_API_URL, headers=headers, data=data)
            
            # Placeholder response
            analysis_result = f"Image analysis placeholder: This appears to be an uploaded image. Ready for integration with Hugging Face Vision APIs for detailed analysis."
            
            response_time = time.time() - start_time
            
            result = {
                "analysis": analysis_result,
                "confidence": 0.95,
                "response_time": round(response_time, 3),
                "status": "success"
            }
            
            logger.info(f"Image processed successfully in {response_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return {
                "analysis": "Unable to process image at this time.",
                "confidence": 0.0,
                "response_time": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Process audio using Hugging Face Speech-to-Text API (placeholder implementation)
        
        Args:
            audio_path (str): Path to uploaded audio file
            
        Returns:
            Dict[str, Any]: Audio transcription result
        """
        try:
            logger.info(f"Processing audio: {audio_path}")
            start_time = time.time()
            
            # Simulate processing delay
            await asyncio.sleep(1.5)
            
            # TODO: Replace with actual Hugging Face API call
            # Similar to image processing but for audio transcription
            
            # Placeholder response
            transcription = "Audio transcription placeholder: Ready for integration with Hugging Face Speech-to-Text APIs."
            
            response_time = time.time() - start_time
            
            result = {
                "transcription": transcription,
                "confidence": 0.92,
                "response_time": round(response_time, 3),
                "status": "success"
            }
            
            logger.info(f"Audio processed successfully in {response_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}", exc_info=True)
            return {
                "transcription": "Unable to process audio at this time.",
                "confidence": 0.0,
                "response_time": 0,
                "status": "error",
                "error": str(e)
            }

# Global AI service instance
ai_service = AIService() 