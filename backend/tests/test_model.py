import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ml.feature_builder import build_features
from app.ml.supplier_risk_model import RuleBasedModel
from app.ml.model_registry import ModelRegistry


_SAMPLE_SUPPLIER = {
    "supplier_id": "SUP-001",
    "lead_time_days": 30,
    "defect_rate": 0.05,
    "late_delivery_count": 5,
    "order_value": 100_000,
    "country": "VN",
}


def test_feature_builder_valid_output():
    features = build_features(_SAMPLE_SUPPLIER)

    expected_keys = {
        "supplier_id",
        "lead_time_norm",
        "defect_rate_norm",
        "late_delivery_norm",
        "order_value_norm",
        "country_risk",
        "defect_cost_interaction",
        "delivery_reliability",
    }
    assert set(features.keys()) == expected_keys

    for key in expected_keys - {"supplier_id"}:
        assert 0.0 <= features[key] <= 1.0, f"{key} out of [0,1] range"

    assert features["supplier_id"] == "SUP-001"


def test_rule_based_model_returns_valid_schema():
    features = build_features(_SAMPLE_SUPPLIER)
    model = RuleBasedModel()
    result = model.predict(features)

    assert "risk_score" in result
    assert "risk_level" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in {"low", "medium", "high", "critical"}


def test_risk_level_thresholds():
    model = RuleBasedModel()

    low_features = {k: 0.1 for k in [
        "defect_rate_norm", "late_delivery_norm", "country_risk",
        "lead_time_norm", "order_value_norm",
    ]}
    assert model.predict(low_features)["risk_level"] == "low"

    medium_features = {k: 0.5 for k in low_features}
    assert model.predict(medium_features)["risk_level"] == "medium"

    high_features = {k: 0.8 for k in low_features}
    assert model.predict(high_features)["risk_level"] == "high"

    critical_features = {k: 1.0 for k in low_features}
    assert model.predict(critical_features)["risk_level"] == "critical"


def test_explain_returns_factors():
    features = build_features(_SAMPLE_SUPPLIER)
    model = RuleBasedModel()
    explanations = model.explain(features)

    assert len(explanations) == 5
    for entry in explanations:
        assert "factor" in entry
        assert "value" in entry
        assert "impact" in entry
        assert "direction" in entry
        assert entry["direction"] in {"increases_risk", "decreases_risk"}

    impacts = [e["impact"] for e in explanations]
    assert impacts == sorted(impacts, reverse=True), "Should be sorted by impact desc"


def test_model_registry_get_production():
    registry = ModelRegistry()
    prod = registry.get_production()

    assert prod is not None
    assert prod.stage == "production"
    assert prod.version == "1.0.0"
    assert isinstance(prod.model_instance, RuleBasedModel)

    assert registry.get_by_version("1.0.0") is prod
    assert len(registry.list_versions()) >= 1
