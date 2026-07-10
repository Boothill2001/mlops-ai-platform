from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.ml.supplier_risk_model import BaseRiskModel, RuleBasedModel


Stage = Literal["production", "canary", "archived"]


@dataclass
class ModelVersion:
    name: str
    version: str
    stage: Stage
    model_instance: BaseRiskModel
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRegistry:
    def __init__(self) -> None:
        self._versions: dict[str, ModelVersion] = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        self.register(
            name="supplier-risk-rule-based",
            version="1.0.0",
            stage="production",
            model_instance=RuleBasedModel(),
        )

    def register(
        self,
        name: str,
        version: str,
        stage: Stage,
        model_instance: BaseRiskModel,
    ) -> ModelVersion:
        entry = ModelVersion(
            name=name,
            version=version,
            stage=stage,
            model_instance=model_instance,
        )
        self._versions[version] = entry
        return entry

    def get_production(self) -> ModelVersion | None:
        for mv in self._versions.values():
            if mv.stage == "production":
                return mv
        return None

    def get_by_version(self, version: str) -> ModelVersion | None:
        return self._versions.get(version)

    def list_versions(self) -> list[ModelVersion]:
        return list(self._versions.values())
