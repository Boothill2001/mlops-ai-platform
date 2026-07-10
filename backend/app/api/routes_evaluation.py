from __future__ import annotations

from fastapi import APIRouter

from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import get_evaluation_service
from app.storage.seed_data import GOLDEN_QUESTIONS

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])


@router.post("/run", response_model=EvaluationResponse)
async def run_evaluation(request: EvaluationRequest):
    service = get_evaluation_service()
    result = await service.run_evaluation(top_k=request.top_k, role=request.role)
    return result


@router.get("/golden-questions")
async def get_golden_questions():
    return GOLDEN_QUESTIONS
