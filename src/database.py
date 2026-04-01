import asyncpg
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import logging

from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class Database:
    """Database connection pool manager."""
    
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Get or create database connection pool."""
        if cls._pool is None:
            logger.info(f"Creating database connection pool to {config.database_url}")
            cls._pool = await asyncpg.create_pool(
                config.database_url,
                min_size=1,
                max_size=config.database_pool_size,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
            )
        return cls._pool
    
    @classmethod
    async def close(cls):
        """Close database connection pool."""
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database connection pool closed")
    
    @classmethod
    @asynccontextmanager
    async def get_connection(cls) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool."""
        pool = await cls.get_pool()
        connection = await pool.acquire()
        try:
            yield connection
        finally:
            await pool.release(connection)


async def init_database():
    """Initialize database connection and verify schema."""
    try:
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            # Verify tables exist
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_names = {row['table_name'] for row in tables}
            
            required_tables = {'memories', 'api_usage', 'embedding_cache'}
            missing_tables = required_tables - table_names
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                # In production, you would run migrations here
                # For now, we'll rely on init.sql
                
            logger.info(f"Database initialized with tables: {table_names}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def health_check() -> bool:
    """Check database health."""
    try:
        pool = await Database.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False