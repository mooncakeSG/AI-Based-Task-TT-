import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# PostgreSQL/SQLAlchemy imports
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import declarative_base, Mapped, mapped_column
    from sqlalchemy import Integer, String, Text, Float, DateTime, select, delete
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

class PostgreSQLDatabaseService:
    def __init__(self):
        self.engine = None
        self.async_session = None
        self.supabase: Optional[Client] = None
        self.connection_type = "none"
        self.initialized = False
        
        # In-memory storage fallback
        self.memory_storage = {
            'tasks': [],
            'chat_history': [],
            'uploaded_files': [],
            'users': []
        }
        self.next_id = 1
    
    async def initialize_connections(self):
        """Initialize database connections in order of preference"""
        
        # 1. Try PostgreSQL direct connection first
        if await self._try_postgresql():
            self.initialized = True
            return
        
        # 2. Try Supabase as fallback
        if await self._try_supabase():
            self.initialized = True
            return
        
        # 3. Use in-memory storage
        logger.warning("No database connection available - using in-memory storage")
        self.connection_type = "memory"
        self.initialized = True
    
    async def _try_postgresql(self) -> bool:
        """Try to connect to PostgreSQL directly"""
        # Temporarily disabled due to permission issues (42501)
        # The user has PostgreSQL configured but lacks table creation privileges
        logger.info("PostgreSQL temporarily disabled - using Supabase for better compatibility")
        return False
        
        # Original code commented out until permissions are resolved:
        # if not SQLALCHEMY_AVAILABLE:
        #     logger.warning("SQLAlchemy not available - install asyncpg and sqlalchemy")
        #     return False
        # 
        # if not settings.database_url or settings.database_url.strip() == "":
        #     logger.info("No PostgreSQL DATABASE_URL configured")
        #     return False
        # 
        # try:
        #     # Convert postgresql:// to postgresql+asyncpg://
        #     db_url = settings.database_url
        #     if db_url.startswith("postgresql://"):
        #         db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        #     
        #     # Create async engine
        #     self.engine = create_async_engine(db_url, echo=settings.debug)
        #     self.async_session = async_sessionmaker(self.engine, class_=AsyncSession)
        #     
        #     # Test connection and create tables
        #     async with self.engine.begin() as conn:
        #         await conn.run_sync(Base.metadata.create_all)
        #     
        #     self.connection_type = "postgresql"
        #     logger.info("PostgreSQL connection established successfully")
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"Failed to connect to PostgreSQL: {e}")
        #     return False
    
    async def _try_supabase(self) -> bool:
        """Try to connect to Supabase"""
        if not SUPABASE_AVAILABLE:
            return False
        
        if (not settings.supabase_url or not settings.supabase_anon_key or
            settings.supabase_url == "https://your-project-id.supabase.co"):
            return False
        
        try:
            self.supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
            test_result = self.supabase.table('tasks').select('count').limit(1).execute()
            self.connection_type = "supabase"
            logger.info("Supabase connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        if not self.initialized:
            await self.initialize_connections()
        
        return {
            "status": "connected" if self.connection_type != "memory" else "development_mode",
            "type": self.connection_type,
            "message": f"Using {self.connection_type} database",
            "timestamp": time.time(),
            "tasks_count": len(self.memory_storage['tasks']) if self.connection_type == "memory" else None
        }

    async def get_tasks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks"""
        if not self.initialized:
            await self.initialize_connections()
        
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
        if not self.initialized:
            await self.initialize_connections()
        
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
                    
                    logger.info(f"Created task in PostgreSQL: {task.id}")
                    
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
            
            logger.info(f"Created task in memory: {task['id']}")
            return task

    async def clear_all_tasks(self, user_id: Optional[str] = None) -> int:
        """Clear all tasks"""
        if not self.initialized:
            await self.initialize_connections()
        
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

    # Placeholder methods for compatibility
    async def save_chat_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
    
    async def save_uploaded_file(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None
    
    async def get_uploaded_files(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return []
    
    async def save_file_record(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.save_uploaded_file(file_data)
    
    async def get_file_records(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.get_uploaded_files(user_id)

# Global database service instance
database_service = PostgreSQLDatabaseService() 