import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio

# PostgreSQL/SQLAlchemy imports
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import declarative_base, Mapped, mapped_column
    from sqlalchemy import Column, Integer, String, Text, Float, DateTime, select, delete, update
    from sqlalchemy.dialects.postgresql import UUID
    import uuid
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Supabase imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Models
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class Task(Base):
        __tablename__ = "tasks"
        
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        summary: Mapped[str] = mapped_column(Text, nullable=False)
        category: Mapped[str] = mapped_column(String(100), default="general")
        priority: Mapped[str] = mapped_column(String(20), default="medium")
        status: Mapped[str] = mapped_column(String(20), default="pending")
        user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class ChatHistory(Base):
        __tablename__ = "chat_history"
        
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
        message: Mapped[str] = mapped_column(Text, nullable=False)
        response: Mapped[str] = mapped_column(Text, nullable=False)
        model: Mapped[str] = mapped_column(String(100), nullable=True)
        response_time: Mapped[float] = mapped_column(Float, default=0.0)
        tokens_used: Mapped[int] = mapped_column(Integer, default=0)
        context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.async_session = None
        self.supabase: Optional[Client] = None
        self.connection_type = "none"
        
        # In-memory storage fallback
        self.memory_storage = {
            'tasks': [],
            'chat_history': [],
            'uploaded_files': [],
            'users': []
        }
        self.next_id = 1
        self.initialized = False
    
    async def initialize_connections(self):
        """Initialize database connections in order of preference"""
        
        # 1. Try PostgreSQL direct connection first
        if await self._try_postgresql():
            return
        
        # 2. Try Supabase as fallback
        if await self._try_supabase():
            return
        
        # 3. Use in-memory storage
        logger.warning("No database connection available - using in-memory storage")
        self.connection_type = "memory"
    
    async def _try_postgresql(self) -> bool:
        """Try to connect to PostgreSQL directly"""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available - cannot use PostgreSQL direct connection")
            return False
        
        if not settings.database_url or settings.database_url.strip() == "":
            logger.info("No PostgreSQL DATABASE_URL configured")
            return False
        
        try:
            # Convert postgresql:// to postgresql+asyncpg://
            db_url = settings.database_url
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif not db_url.startswith("postgresql+asyncpg://"):
                logger.error("Invalid database URL format. Must start with postgresql://")
                return False
            
            # Create async engine
            self.engine = create_async_engine(
                db_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Create session factory
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Test a simple query
            async with self.async_session() as session:
                result = await session.execute(select(Task).limit(1))
                result.fetchall()
            
            self.connection_type = "postgresql"
            logger.info("PostgreSQL connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.engine = None
            self.async_session = None
            return False
    
    async def _try_supabase(self) -> bool:
        """Try to connect to Supabase"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not available")
            return False
        
        if (not settings.supabase_url or settings.supabase_url.strip() == "" or
            settings.supabase_url == "https://your-project-id.supabase.co" or
            not settings.supabase_anon_key or settings.supabase_anon_key.strip() == "" or
            settings.supabase_anon_key == "your-anon-public-key-here"):
            logger.info("Supabase credentials not properly configured")
            return False
        
        try:
            self.supabase = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            
            # Test connection
            test_result = self.supabase.table('tasks').select('count').limit(1).execute()
            
            self.connection_type = "supabase"
            logger.info("Supabase connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        if self.connection_type == "postgresql":
            try:
                async with self.async_session() as session:
                    result = await session.execute(select(Task).limit(1))
                    result.fetchall()
                return {
                    "status": "connected",
                    "type": "postgresql",
                    "message": "PostgreSQL database connection healthy",
                    "timestamp": time.time()
                }
            except Exception as e:
                return {
                    "status": "error",
                    "type": "postgresql",
                    "message": f"PostgreSQL connection failed: {str(e)}",
                    "timestamp": time.time()
                }
        
        elif self.connection_type == "supabase":
            try:
                result = self.supabase.table('tasks').select('count').limit(1).execute()
                return {
                    "status": "connected",
                    "type": "supabase",
                    "message": "Supabase database connection healthy",
                    "timestamp": time.time()
                }
            except Exception as e:
                return {
                    "status": "error",
                    "type": "supabase",
                    "message": f"Supabase connection failed: {str(e)}",
                    "timestamp": time.time()
                }
        
        else:
            return {
                "status": "development_mode",
                "type": "memory",
                "message": "Using in-memory storage (no database configured)",
                "timestamp": time.time(),
                "tasks_count": len(self.memory_storage['tasks'])
            }

    # ==========================================
    # TASKS OPERATIONS
    # ==========================================
    
    async def get_tasks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks, optionally filtered by user"""
        
        if self.connection_type == "postgresql":
            try:
                async with self.async_session() as session:
                    query = select(Task).order_by(Task.created_at.desc())
                    if user_id:
                        query = query.where(Task.user_id == user_id)
                    
                    result = await session.execute(query)
                    tasks = result.scalars().all()
                    
                    return [
                        {
                            "id": task.id,
                            "summary": task.summary,
                            "category": task.category,
                            "priority": task.priority,
                            "status": task.status,
                            "user_id": task.user_id,
                            "created_at": task.created_at.timestamp(),
                            "updated_at": task.updated_at.timestamp()
                        }
                        for task in tasks
                    ]
            except Exception as e:
                logger.error(f"Failed to fetch tasks from PostgreSQL: {e}")
                return []
        
        elif self.connection_type == "supabase":
            try:
                query = self.supabase.table('tasks').select('*').order('created_at', desc=True)
                if user_id:
                    query = query.eq('user_id', user_id)
                result = query.execute()
                return result.data if result.data else []
            except Exception as e:
                logger.error(f"Failed to fetch tasks from Supabase: {e}")
                return []
        
        else:
            # Memory storage
            tasks = self.memory_storage['tasks']
            if user_id:
                tasks = [task for task in tasks if task.get('user_id') == user_id]
            tasks.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            return tasks

    async def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new task"""
        
        if self.connection_type == "postgresql":
            try:
                async with self.async_session() as session:
                    task = Task(
                        summary=task_data.get('summary', ''),
                        category=task_data.get('category', 'general'),
                        priority=task_data.get('priority', 'medium'),
                        status=task_data.get('status', 'pending'),
                        user_id=task_data.get('user_id')
                    )
                    
                    session.add(task)
                    await session.commit()
                    await session.refresh(task)
                    
                    logger.info(f"Created task in PostgreSQL: {task.id} - {task.summary[:50]}")
                    
                    return {
                        "id": task.id,
                        "summary": task.summary,
                        "category": task.category,
                        "priority": task.priority,
                        "status": task.status,
                        "user_id": task.user_id,
                        "created_at": task.created_at.timestamp(),
                        "updated_at": task.updated_at.timestamp()
                    }
            except Exception as e:
                logger.error(f"Failed to create task in PostgreSQL: {e}")
                return None
        
        elif self.connection_type == "supabase":
            try:
                if 'created_at' not in task_data:
                    task_data['created_at'] = time.time()
                
                result = self.supabase.table('tasks').insert(task_data).execute()
                if result.data:
                    logger.info(f"Created task in Supabase: {result.data[0].get('id')}")
                    return result.data[0]
                return None
            except Exception as e:
                logger.error(f"Failed to create task in Supabase: {e}")
                return None
        
        else:
            # Memory storage
            task = task_data.copy()
            task['id'] = self.next_id
            task['created_at'] = task.get('created_at', time.time())
            task['updated_at'] = time.time()
            
            self.memory_storage['tasks'].append(task)
            self.next_id += 1
            
            logger.info(f"Created task in memory: {task['id']} - {task.get('summary', 'No summary')[:50]}")
            return task

    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing task"""
        if not self.initialized:
            # Use in-memory storage
            for task in self.memory_storage['tasks']:
                if task['id'] == task_id:
                    task.update(updates)
                    task['updated_at'] = time.time()
                    logger.info(f"Updated task in memory: {task_id}")
                    return task
            return None
        
        try:
            updates['updated_at'] = time.time()
            
            result = self.supabase.table('tasks').update(updates).eq('id', task_id).execute()
            
            if result.data:
                logger.info(f"Updated task: {task_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return None

    async def delete_task(self, task_id: int) -> bool:
        """Delete a specific task"""
        if not self.initialized:
            # Use in-memory storage
            original_count = len(self.memory_storage['tasks'])
            self.memory_storage['tasks'] = [
                task for task in self.memory_storage['tasks'] 
                if task['id'] != task_id
            ]
            deleted = len(self.memory_storage['tasks']) < original_count
            if deleted:
                logger.info(f"Deleted task from memory: {task_id}")
            return deleted
        
        try:
            result = self.supabase.table('tasks').delete().eq('id', task_id).execute()
            logger.info(f"Deleted task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    async def clear_all_tasks(self, user_id: Optional[str] = None) -> int:
        """Clear all tasks, optionally for a specific user"""
        
        if self.connection_type == "postgresql":
            try:
                async with self.async_session() as session:
                    if user_id:
                        result = await session.execute(delete(Task).where(Task.user_id == user_id))
                    else:
                        result = await session.execute(delete(Task))
                    
                    await session.commit()
                    count = result.rowcount
                    logger.info(f"Cleared {count} tasks from PostgreSQL")
                    return count
            except Exception as e:
                logger.error(f"Failed to clear tasks from PostgreSQL: {e}")
                return 0
        
        elif self.connection_type == "supabase":
            try:
                query = self.supabase.table('tasks').delete()
                if user_id:
                    query = query.eq('user_id', user_id)
                else:
                    query = query.neq('id', 0)
                
                result = query.execute()
                count = len(result.data) if result.data else 0
                logger.info(f"Cleared {count} tasks from Supabase")
                return count
            except Exception as e:
                logger.error(f"Failed to clear tasks from Supabase: {e}")
                return 0
        
        else:
            # Memory storage
            original_count = len(self.memory_storage['tasks'])
            if user_id:
                self.memory_storage['tasks'] = [
                    task for task in self.memory_storage['tasks'] 
                    if task.get('user_id') != user_id
                ]
            else:
                self.memory_storage['tasks'] = []
            
            cleared_count = original_count - len(self.memory_storage['tasks'])
            logger.info(f"Cleared {cleared_count} tasks from memory")
            return cleared_count

    # ==========================================
    # CHAT HISTORY OPERATIONS
    # ==========================================
    
    async def save_chat_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a chat message to history"""
        
        if self.connection_type == "postgresql":
            try:
                async with self.async_session() as session:
                    chat = ChatHistory(
                        user_id=message_data.get('user_id'),
                        message=message_data.get('message', ''),
                        response=message_data.get('response', ''),
                        model=message_data.get('model'),
                        response_time=message_data.get('response_time', 0.0),
                        tokens_used=message_data.get('tokens_used', 0),
                        context=message_data.get('context')
                    )
                    
                    session.add(chat)
                    await session.commit()
                    await session.refresh(chat)
                    
                    return {
                        "id": chat.id,
                        "user_id": chat.user_id,
                        "message": chat.message,
                        "response": chat.response,
                        "model": chat.model,
                        "response_time": chat.response_time,
                        "tokens_used": chat.tokens_used,
                        "context": chat.context,
                        "created_at": chat.created_at.timestamp()
                    }
            except Exception as e:
                logger.error(f"Failed to save chat message to PostgreSQL: {e}")
                return None
        
        elif self.connection_type == "supabase":
            try:
                if 'created_at' not in message_data:
                    message_data['created_at'] = time.time()
                
                result = self.supabase.table('chat_history').insert(message_data).execute()
                if result.data:
                    return result.data[0]
                return None
            except Exception as e:
                logger.error(f"Failed to save chat message to Supabase: {e}")
                return None
        
        else:
            # Memory storage
            message = message_data.copy()
            message['id'] = self.next_id
            message['created_at'] = message.get('created_at', time.time())
            
            self.memory_storage['chat_history'].append(message)
            self.next_id += 1
            
            return message

    async def get_chat_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history, optionally filtered by user"""
        if not self.initialized:
            # Use in-memory storage
            history = self.memory_storage['chat_history']
            if user_id:
                history = [msg for msg in history if msg.get('user_id') == user_id]
            # Sort by created_at descending and limit
            history.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            return history[:limit]
        
        try:
            query = self.supabase.table('chat_history').select('*').order('created_at', desc=True).limit(limit)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to fetch chat history: {e}")
            return []

    async def clear_chat_history(self, user_id: Optional[str] = None) -> int:
        """Clear chat history, optionally for a specific user"""
        if not self.initialized:
            # Use in-memory storage
            original_count = len(self.memory_storage['chat_history'])
            
            if user_id:
                self.memory_storage['chat_history'] = [
                    msg for msg in self.memory_storage['chat_history'] 
                    if msg.get('user_id') != user_id
                ]
            else:
                self.memory_storage['chat_history'] = []
            
            cleared_count = original_count - len(self.memory_storage['chat_history'])
            logger.info(f"Cleared {cleared_count} chat messages from memory")
            return cleared_count
        
        try:
            query = self.supabase.table('chat_history').delete()
            
            if user_id:
                query = query.eq('user_id', user_id)
            else:
                query = query.neq('id', 0)  # Clear all
            
            result = query.execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Cleared {count} chat messages")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            return 0

    # ==========================================
    # USER OPERATIONS
    # ==========================================
    
    async def create_or_get_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user or get existing user"""
        if not self.initialized:
            # Use in-memory storage
            # First try to get existing user
            if 'email' in user_data:
                for user in self.memory_storage['users']:
                    if user.get('email') == user_data['email']:
                        return user
            
            # Create new user
            user = user_data.copy()
            user['id'] = self.next_id
            user['created_at'] = user.get('created_at', time.time())
            
            self.memory_storage['users'].append(user)
            self.next_id += 1
            
            logger.info(f"Created user in memory: {user['id']}")
            return user
        
        try:
            # First try to get existing user
            if 'email' in user_data:
                existing = self.supabase.table('users').select('*').eq('email', user_data['email']).execute()
                if existing.data:
                    return existing.data[0]
            
            # Create new user
            if 'created_at' not in user_data:
                user_data['created_at'] = time.time()
            
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                logger.info(f"Created user: {result.data[0].get('id')}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to create/get user: {e}")
            return None

    # ==========================================
    # FILE OPERATIONS
    # ==========================================
    
    async def save_uploaded_file(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save file upload record"""
        if not self.initialized:
            # Use in-memory storage
            file_record = file_data.copy()
            file_record['id'] = self.next_id
            file_record['created_at'] = file_record.get('created_at', time.time())
            
            self.memory_storage['uploaded_files'].append(file_record)
            self.next_id += 1
            
            logger.info(f"Saved file record in memory: {file_record['id']} - {file_record.get('filename', 'Unknown')}")
            return file_record
        
        try:
            if 'created_at' not in file_data:
                file_data['created_at'] = time.time()
            
            result = self.supabase.table('uploaded_files').insert(file_data).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to save file record: {e}")
            return None

    async def get_uploaded_files(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get file upload records"""
        if not self.initialized:
            # Use in-memory storage
            files = self.memory_storage['uploaded_files']
            if user_id:
                files = [file for file in files if file.get('user_id') == user_id]
            # Sort by created_at descending
            files.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            return files
        
        try:
            query = self.supabase.table('uploaded_files').select('*').order('created_at', desc=True)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to fetch file records: {e}")
            return []

    # Compatibility aliases for existing code
    async def save_file_record(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Alias for save_uploaded_file for backward compatibility"""
        return await self.save_uploaded_file(file_data)
    
    async def get_file_records(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Alias for get_uploaded_files for backward compatibility"""
        return await self.get_uploaded_files(user_id)

# Global database service instance
database_service = DatabaseService() 