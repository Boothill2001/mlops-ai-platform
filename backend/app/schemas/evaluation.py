from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    top_k: int = Field(default=5, ge=1, le=20)
    role: str = "analyst"


class FailedCase(BaseModel):
    question: str
    recall: float
    expected_docs: list[str]
    retrieved_docs: list[str]


class EvaluationResponse(BaseModel):
    recall_at_k: float
    precision_at_k: float
    faithfulness: float
    citation_accuracy: float
    total_questions: int
    passed_questions: int
    failed_cases: list[FailedCase]
    regression_detected: bool
