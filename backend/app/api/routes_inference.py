from __future__ import annotations

from fastapi import APIRouter

from app.schemas.inference import SupplierRiskRequest, SupplierRiskResponse
from app.services.inference_service import get_inference_service
from app.storage.seed_data import SUPPLIERS

router = APIRouter(prefix="/api/v1/inference", tags=["inference"])


@router.post("/supplier-risk", response_model=SupplierRiskResponse)
async def predict_supplier_risk(request: SupplierRiskRequest) -> SupplierRiskResponse:
    service = get_inference_service()
    return await service.predict(request)


@router.get("/suppliers")
async def list_suppliers() -> list[dict]:
    return SUPPLIERS
