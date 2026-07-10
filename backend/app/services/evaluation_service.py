from __future__ import annotations

import threading

from app.services.rag_service import get_rag_service
from app.storage.seed_data import GOLDEN_QUESTIONS


class EvaluationService:
    async def run_evaluation(self, top_k: int = 5, role: str = "analyst") -> dict:
        rag_service = get_rag_service()
        questions = GOLDEN_QUESTIONS

        per_question_metrics: list[dict] = []
        failed_cases: list[dict] = []

        for q in questions:
            result = await rag_service.query(
                user_id="eval_user",
                role=role,
                query_text=q["question"],
                top_k=top_k,
            )

            retrieved_doc_ids = [c["doc_id"] for c in result.get("citations", [])]
            expected_doc_ids = q["expected_doc_ids"]

            expected_set = set(expected_doc_ids)
            retrieved_set = set(retrieved_doc_ids)
            overlap = expected_set & retrieved_set

            recall_at_k = len(overlap) / len(expected_set) if expected_set else 0.0
            precision_at_k = len(overlap) / len(retrieved_set) if retrieved_set else 0.0

            answer_lower = result.get("answer", "").lower()
            keywords = q["expected_answer_keywords"]
            keyword_hits = sum(1 for kw in keywords if kw.lower() in answer_lower)
            faithfulness = keyword_hits / len(keywords) if keywords else 0.0

            cited_ids = set(retrieved_doc_ids)
            citation_accuracy = (
                len(cited_ids & expected_set) / len(cited_ids) if cited_ids else 0.0
            )

            per_question_metrics.append(
                {
                    "recall_at_k": recall_at_k,
                    "precision_at_k": precision_at_k,
                    "faithfulness": faithfulness,
                    "citation_accuracy": citation_accuracy,
                }
            )

            if recall_at_k < 0.5:
                failed_cases.append(
                    {
                        "question": q["question"],
                        "recall": recall_at_k,
                        "expected_docs": expected_doc_ids,
                        "retrieved_docs": retrieved_doc_ids,
                    }
                )

        n = len(per_question_metrics)
        avg_recall = sum(m["recall_at_k"] for m in per_question_metrics) / n if n else 0.0
        avg_precision = sum(m["precision_at_k"] for m in per_question_metrics) / n if n else 0.0
        avg_faithfulness = sum(m["faithfulness"] for m in per_question_metrics) / n if n else 0.0
        avg_citation = sum(m["citation_accuracy"] for m in per_question_metrics) / n if n else 0.0

        regression_detected = avg_recall < 0.6 or avg_faithfulness < 0.5

        return {
            "recall_at_k": round(avg_recall, 4),
            "precision_at_k": round(avg_precision, 4),
            "faithfulness": round(avg_faithfulness, 4),
            "citation_accuracy": round(avg_citation, 4),
            "total_questions": n,
            "passed_questions": n - len(failed_cases),
            "failed_cases": failed_cases,
            "regression_detected": regression_detected,
        }


_instance: EvaluationService | None = None
_instance_lock = threading.Lock()


def get_evaluation_service() -> EvaluationService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = EvaluationService()
    return _instance
