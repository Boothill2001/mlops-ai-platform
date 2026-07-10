from __future__ import annotations


COUNTRY_RISK_MAP: dict[str, float] = {
    "VN": 0.3,
    "CN": 0.4,
    "TH": 0.25,
    "IN": 0.35,
    "US": 0.15,
    "DE": 0.1,
    "JP": 0.12,
    "KR": 0.2,
    "BD": 0.5,
    "PK": 0.45,
}

_MAX_LEAD_TIME = 120.0
_MAX_DEFECT_RATE = 0.25
_MAX_LATE_DELIVERY = 50
_MAX_ORDER_VALUE = 500_000.0


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def normalize_lead_time(days: float) -> float:
    return _clamp(days / _MAX_LEAD_TIME)


def normalize_defect_rate(rate: float) -> float:
    return _clamp(rate / _MAX_DEFECT_RATE)


def normalize_late_delivery(count: int) -> float:
    return _clamp(count / _MAX_LATE_DELIVERY)


def normalize_order_value(value: float) -> float:
    return _clamp(value / _MAX_ORDER_VALUE)


def get_country_risk(country: str) -> float:
    return COUNTRY_RISK_MAP.get(country.upper(), 0.5)


def build_features(supplier_data: dict) -> dict:
    """Transform raw supplier record into normalised feature vector."""
    lead_time_norm = normalize_lead_time(supplier_data["lead_time_days"])
    defect_rate_norm = normalize_defect_rate(supplier_data["defect_rate"])
    late_delivery_norm = normalize_late_delivery(supplier_data["late_delivery_count"])
    order_value_norm = normalize_order_value(supplier_data["order_value"])
    country_risk = get_country_risk(supplier_data["country"])

    # Interaction: high defect rate on large orders amplifies risk
    defect_cost_interaction = (
        supplier_data["defect_rate"] * supplier_data["order_value"] / _MAX_ORDER_VALUE
    )

    delivery_reliability = 1.0 - (
        supplier_data["late_delivery_count"] / _MAX_LATE_DELIVERY
    )
    delivery_reliability = _clamp(delivery_reliability)

    return {
        "supplier_id": supplier_data["supplier_id"],
        "lead_time_norm": round(lead_time_norm, 6),
        "defect_rate_norm": round(defect_rate_norm, 6),
        "late_delivery_norm": round(late_delivery_norm, 6),
        "order_value_norm": round(order_value_norm, 6),
        "country_risk": round(country_risk, 6),
        "defect_cost_interaction": round(_clamp(defect_cost_interaction), 6),
        "delivery_reliability": round(delivery_reliability, 6),
    }
