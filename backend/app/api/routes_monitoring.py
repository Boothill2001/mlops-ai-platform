from fastapi import APIRouter

from app.schemas.monitoring import MetricsResponse, DriftInfo
from app.services.monitoring_service import get_monitoring_service
from app.services.drift_service import get_drift_service
from app.services.history_service import get_history_service

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    svc = get_monitoring_service()
    return svc.get_metrics()


@router.get("/drift", response_model=DriftInfo)
async def get_drift():
    svc = get_drift_service()
    return svc.get_drift_score()


@router.get("/history")
async def get_history():
    svc = get_history_service()
    return svc.get_history(limit=50)
