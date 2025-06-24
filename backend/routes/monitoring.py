from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime
from services.monitoring import api_monitor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

@router.get("/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        dashboard = api_monitor.get_dashboard_data()
        return {
            "status": "success",
            "health": dashboard["overall_health"],
            "timestamp": dashboard["timestamp"],
            "services": dashboard["services"],
            "summary": {
                "total_requests": dashboard["total_requests"],
                "total_errors": dashboard["total_errors"],
                "error_rate": dashboard["total_errors"] / max(dashboard["total_requests"], 1)
            }
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")

@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Get comprehensive monitoring dashboard data"""
    try:
        return {
            "status": "success",
            "data": api_monitor.get_dashboard_data()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/metrics")
async def get_recent_metrics(minutes: int = Query(60, ge=1, le=1440)):
    """Get recent API metrics"""
    try:
        metrics = api_monitor.get_recent_metrics(minutes)
        return {
            "status": "success",
            "timeframe_minutes": minutes,
            "metrics_count": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.get("/service/{service_name}")
async def get_service_health(service_name: str):
    """Get health status for a specific service"""
    try:
        if service_name not in ['groq', 'huggingface', 'supabase']:
            raise HTTPException(status_code=404, detail="Service not found")
        
        health = api_monitor.get_service_health(service_name)
        return {
            "status": "success",
            "service": health
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service health for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service health")

@router.post("/export")
async def export_metrics():
    """Export metrics to file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"monitoring/metrics_export_{timestamp}.json"
        
        await api_monitor.export_metrics(filepath)
        
        return {
            "status": "success",
            "message": "Metrics exported successfully",
            "filepath": filepath,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to export metrics")

@router.get("/rate-limits")
async def get_rate_limits():
    """Get current rate limit status for all services"""
    try:
        dashboard = api_monitor.get_dashboard_data()
        return {
            "status": "success",
            "rate_limits": dashboard["rate_limits"],
            "timestamp": dashboard["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting rate limits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rate limits") 