import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class APIMetric:
    """Individual API call metric"""
    timestamp: datetime
    service: str  # 'groq', 'huggingface', 'supabase'
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    error_message: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class ServiceHealth:
    """Service health status"""
    service: str
    status: str  # 'healthy', 'degraded', 'down'
    last_success: datetime
    last_failure: Optional[datetime]
    success_rate: float
    avg_response_time: float
    total_requests: int
    error_count: int

class APIMonitor:
    """Comprehensive API monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.service_stats = defaultdict(lambda: {
            'total_requests': 0,
            'total_errors': 0,
            'total_response_time': 0,
            'last_success': None,
            'last_failure': None,
            'recent_response_times': deque(maxlen=100)
        })
        self.rate_limits = {
            'groq': {'requests_per_minute': 30, 'current_count': 0, 'reset_time': datetime.now()},
            'huggingface': {'requests_per_minute': 1000, 'current_count': 0, 'reset_time': datetime.now()},
            'supabase': {'requests_per_minute': 1000, 'current_count': 0, 'reset_time': datetime.now()}
        }
        
    async def track_api_call(self, service: str, endpoint: str, method: str = 'POST', 
                           user_id: Optional[str] = None):
        """Context manager for tracking API calls"""
        return APICallTracker(self, service, endpoint, method, user_id)
    
    def record_metric(self, metric: APIMetric):
        """Record an API metric"""
        self.metrics.append(metric)
        
        # Update service statistics
        stats = self.service_stats[metric.service]
        stats['total_requests'] += 1
        stats['total_response_time'] += metric.response_time
        stats['recent_response_times'].append(metric.response_time)
        
        if metric.status_code >= 400:
            stats['total_errors'] += 1
            stats['last_failure'] = metric.timestamp
        else:
            stats['last_success'] = metric.timestamp
            
        # Check rate limits
        self._check_rate_limits(metric.service)
        
        # Log significant events
        if metric.response_time > 10:  # Slow response
            logger.warning(f"Slow API response: {metric.service} took {metric.response_time:.2f}s")
        if metric.status_code >= 400:
            logger.error(f"API error: {metric.service} returned {metric.status_code}: {metric.error_message}")
    
    def _check_rate_limits(self, service: str):
        """Check and update rate limits"""
        if service not in self.rate_limits:
            return
            
        rate_limit = self.rate_limits[service]
        now = datetime.now()
        
        # Reset counter if a minute has passed
        if now >= rate_limit['reset_time']:
            rate_limit['current_count'] = 0
            rate_limit['reset_time'] = now + timedelta(minutes=1)
        
        rate_limit['current_count'] += 1
        
        # Warn if approaching limit
        if rate_limit['current_count'] >= rate_limit['requests_per_minute'] * 0.8:
            logger.warning(f"Approaching rate limit for {service}: {rate_limit['current_count']}/{rate_limit['requests_per_minute']}")
    
    def get_service_health(self, service: str) -> ServiceHealth:
        """Get health status for a service"""
        stats = self.service_stats[service]
        
        if stats['total_requests'] == 0:
            return ServiceHealth(
                service=service,
                status='unknown',
                last_success=datetime.now(),
                last_failure=None,
                success_rate=0.0,
                avg_response_time=0.0,
                total_requests=0,
                error_count=0
            )
        
        success_rate = (stats['total_requests'] - stats['total_errors']) / stats['total_requests']
        avg_response_time = stats['total_response_time'] / stats['total_requests']
        
        # Determine status
        status = 'healthy'
        if success_rate < 0.95:
            status = 'degraded'
        if success_rate < 0.5 or avg_response_time > 30:
            status = 'down'
        
        return ServiceHealth(
            service=service,
            status=status,
            last_success=stats['last_success'] or datetime.now(),
            last_failure=stats['last_failure'],
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            total_requests=stats['total_requests'],
            error_count=stats['total_errors']
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        services = ['groq', 'huggingface', 'supabase']
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'overall_health': 'healthy',
            'total_requests': sum(self.service_stats[s]['total_requests'] for s in services),
            'total_errors': sum(self.service_stats[s]['total_errors'] for s in services),
            'rate_limits': self.rate_limits.copy()
        }
        
        unhealthy_services = 0
        for service in services:
            health = self.get_service_health(service)
            dashboard['services'][service] = asdict(health)
            
            if health.status != 'healthy':
                unhealthy_services += 1
        
        # Overall health assessment
        if unhealthy_services >= 2:
            dashboard['overall_health'] = 'down'
        elif unhealthy_services == 1:
            dashboard['overall_health'] = 'degraded'
        
        return dashboard
    
    def get_recent_metrics(self, minutes: int = 60) -> List[Dict]:
        """Get metrics from the last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            asdict(metric) for metric in self.metrics 
            if metric.timestamp >= cutoff
        ]
    
    async def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'dashboard': self.get_dashboard_data(),
            'recent_metrics': self.get_recent_metrics(1440)  # Last 24 hours
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {filepath}")

class APICallTracker:
    """Context manager for tracking individual API calls"""
    
    def __init__(self, monitor: APIMonitor, service: str, endpoint: str, 
                 method: str, user_id: Optional[str] = None):
        self.monitor = monitor
        self.service = service
        self.endpoint = endpoint
        self.method = method
        self.user_id = user_id
        self.start_time = None
        self.request_size = 0
        self.response_size = 0
        self.status_code = 200
        self.error_message = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        response_time = time.time() - self.start_time
        
        # Determine status and error if exception occurred
        if exc_type is not None:
            self.status_code = 500
            self.error_message = str(exc_val)
        
        # Create and record metric
        metric = APIMetric(
            timestamp=datetime.now(),
            service=self.service,
            endpoint=self.endpoint,
            method=self.method,
            status_code=self.status_code,
            response_time=response_time,
            request_size=self.request_size,
            response_size=self.response_size,
            error_message=self.error_message,
            user_id=self.user_id
        )
        
        self.monitor.record_metric(metric)
    
    def set_request_size(self, size: int):
        """Set the request payload size"""
        self.request_size = size
    
    def set_response_size(self, size: int):
        """Set the response payload size"""
        self.response_size = size
    
    def set_status(self, status_code: int, error_message: Optional[str] = None):
        """Manually set status for successful calls with custom status"""
        self.status_code = status_code
        self.error_message = error_message

# Global monitor instance
api_monitor = APIMonitor()

# Convenience functions
async def track_groq_call(endpoint: str, user_id: Optional[str] = None):
    return await api_monitor.track_api_call('groq', endpoint, 'POST', user_id)

async def track_huggingface_call(endpoint: str, user_id: Optional[str] = None):
    return await api_monitor.track_api_call('huggingface', endpoint, 'POST', user_id)

async def track_supabase_call(endpoint: str, user_id: Optional[str] = None):
    return await api_monitor.track_api_call('supabase', endpoint, 'POST', user_id) 