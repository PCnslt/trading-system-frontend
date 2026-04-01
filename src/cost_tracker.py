import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

from src.database import Database
from src.models import APIUsage, ServiceType, RequestType
from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class CostTracker:
    """Track API usage and costs."""
    
    def __init__(self):
        self.enabled = config.cost_tracking_enabled
        
        # Pricing per 1K tokens (in USD)
        self.pricing = {
            ServiceType.LOCAL: {
                "embedding": 0.0,
                "completion": 0.0,
                "chat": 0.0
            },
            ServiceType.OPENAI: {
                "embedding": 0.0001,  # text-embedding-3-small
                "completion": 0.0015,  # gpt-3.5-turbo-instruct
                "chat": 0.002  # gpt-3.5-turbo-1106
            },
            ServiceType.ANTHROPIC: {
                "chat": 0.003  # claude-instant-1.2
            }
        }
        
        # Budget tracking
        self.daily_budget = config.daily_limit
        self.weekly_budget = config.weekly_limit
        self.enforce_limits = config.enforce_limits
        
    async def log_usage(
        self,
        service: ServiceType,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_type: RequestType,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """Log API usage and return cost."""
        if not self.enabled:
            return 0.0
        
        # Calculate cost
        cost = self._calculate_cost(
            service, model, request_type, input_tokens, output_tokens
        )
        
        # Check budget limits
        if self.enforce_limits:
            await self._check_budget_limits(cost, service)
        
        # Log to database asynchronously (don't wait)
        asyncio.create_task(
            self._log_to_database(
                service, model, input_tokens, output_tokens,
                cost, request_type, endpoint, metadata
            )
        )
        
        logger.debug(
            f"API usage logged: {service}.{model}, "
            f"tokens: {input_tokens}+{output_tokens}, "
            f"cost: ${cost:.6f}"
        )
        
        return cost
    
    def _calculate_cost(
        self,
        service: ServiceType,
        model: str,
        request_type: RequestType,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost based on pricing table."""
        if service not in self.pricing:
            logger.warning(f"Unknown service: {service}, defaulting to local pricing")
            return 0.0
        
        service_pricing = self.pricing[service]
        
        # Get price per 1K tokens for this request type
        # Default to 'chat' if specific type not found
        price_per_1k = service_pricing.get(
            request_type.value,
            service_pricing.get("chat", 0.0)
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * price_per_1k
        output_cost = (output_tokens / 1000) * price_per_1k
        
        return input_cost + output_cost
    
    async def _check_budget_limits(self, cost: float, service: ServiceType):
        """Check if usage exceeds budget limits."""
        if service == ServiceType.LOCAL:
            return  # Local calls don't count against budget
        
        # Get today's usage
        today = datetime.now().date()
        daily_usage = await self.get_usage_summary(
            start_date=today,
            end_date=today + timedelta(days=1)
        )
        
        daily_total = sum(
            usage["total_cost"] for usage in daily_usage.values()
            if usage["service"] != ServiceType.LOCAL
        )
        
        if daily_total + cost > self.daily_budget:
            raise Exception(f"Daily budget exceeded: ${daily_total + cost:.2f} > ${self.daily_budget:.2f}")
        
        # Get weekly usage
        week_start = today - timedelta(days=today.weekday())
        weekly_usage = await self.get_usage_summary(
            start_date=week_start,
            end_date=week_start + timedelta(weeks=1)
        )
        
        weekly_total = sum(
            usage["total_cost"] for usage in weekly_usage.values()
            if usage["service"] != ServiceType.LOCAL
        )
        
        if weekly_total + cost > self.weekly_budget:
            raise Exception(f"Weekly budget exceeded: ${weekly_total + cost:.2f} > ${self.weekly_budget:.2f}")
    
    async def _log_to_database(
        self,
        service: ServiceType,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        request_type: RequestType,
        endpoint: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ):
        """Log usage to database."""
        try:
            pool = await Database.get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO api_usage 
                    (service, model, input_tokens, output_tokens, cost, 
                     request_type, endpoint, metadata, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP)
                """,
                service.value, model, input_tokens, output_tokens, cost,
                request_type.value, endpoint, json.dumps(metadata or {}))
                
        except Exception as e:
            logger.error(f"Failed to log API usage to database: {e}")
    
    async def get_usage_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """Get usage summary for a date range."""
        try:
            pool = await Database.get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        service,
                        model,
                        request_type,
                        SUM(input_tokens) as total_input_tokens,
                        SUM(output_tokens) as total_output_tokens,
                        SUM(cost) as total_cost,
                        COUNT(*) as request_count
                    FROM api_usage
                    WHERE timestamp >= $1 AND timestamp < $2
                    GROUP BY service, model, request_type
                    ORDER BY total_cost DESC
                """, start_date, end_date)
                
                summary = {}
                for row in rows:
                    key = f"{row['service']}.{row['model']}.{row['request_type']}"
                    summary[key] = {
                        "service": row["service"],
                        "model": row["model"],
                        "request_type": row["request_type"],
                        "total_input_tokens": row["total_input_tokens"],
                        "total_output_tokens": row["total_output_tokens"],
                        "total_cost": float(row["total_cost"]),
                        "request_count": row["request_count"]
                    }
                
                return summary
                
        except Exception as e:
            logger.error(f"Failed to get usage summary: {e}")
            return {}


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get cost tracker singleton."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker