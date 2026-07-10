from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.storage.vector_store import get_vector_store

SUPPLIERS: list[dict] = [
    {"supplier_id": "SUP-VN-001", "name": "Saigon Steel Corp", "country": "VN", "lead_time_days": 14, "defect_rate": 0.03, "late_delivery_count": 2, "order_value": 120000},
    {"supplier_id": "SUP-CN-001", "name": "Shanghai Electronics Co.", "country": "CN", "lead_time_days": 21, "defect_rate": 0.05, "late_delivery_count": 5, "order_value": 350000},
    {"supplier_id": "SUP-TH-001", "name": "Bangkok Rubber Industries", "country": "TH", "lead_time_days": 18, "defect_rate": 0.04, "late_delivery_count": 3, "order_value": 85000},
    {"supplier_id": "SUP-IN-001", "name": "Mumbai Textile Exports", "country": "IN", "lead_time_days": 25, "defect_rate": 0.08, "late_delivery_count": 8, "order_value": 65000},
    {"supplier_id": "SUP-US-001", "name": "Detroit Precision Parts", "country": "US", "lead_time_days": 10, "defect_rate": 0.02, "late_delivery_count": 1, "order_value": 450000},
    {"supplier_id": "SUP-DE-001", "name": "Stuttgart Machining GmbH", "country": "DE", "lead_time_days": 12, "defect_rate": 0.01, "late_delivery_count": 0, "order_value": 500000},
    {"supplier_id": "SUP-JP-001", "name": "Osaka Semiconductor Ltd", "country": "JP", "lead_time_days": 15, "defect_rate": 0.02, "late_delivery_count": 1, "order_value": 280000},
    {"supplier_id": "SUP-KR-001", "name": "Busan Chemical Works", "country": "KR", "lead_time_days": 20, "defect_rate": 0.06, "late_delivery_count": 4, "order_value": 175000},
    {"supplier_id": "SUP-BD-001", "name": "Dhaka Garment Solutions", "country": "BD", "lead_time_days": 30, "defect_rate": 0.12, "late_delivery_count": 12, "order_value": 42000},
    {"supplier_id": "SUP-VN-002", "name": "Hanoi Plastics Manufacturing", "country": "VN", "lead_time_days": 16, "defect_rate": 0.05, "late_delivery_count": 3, "order_value": 95000},
    {"supplier_id": "SUP-CN-002", "name": "Shenzhen Circuit Board Tech", "country": "CN", "lead_time_days": 28, "defect_rate": 0.09, "late_delivery_count": 7, "order_value": 220000},
    {"supplier_id": "SUP-TH-002", "name": "Chiang Mai Auto Parts", "country": "TH", "lead_time_days": 22, "defect_rate": 0.07, "late_delivery_count": 6, "order_value": 130000},
    {"supplier_id": "SUP-IN-002", "name": "Chennai Forge & Foundry", "country": "IN", "lead_time_days": 35, "defect_rate": 0.10, "late_delivery_count": 10, "order_value": 78000},
    {"supplier_id": "SUP-JP-002", "name": "Tokyo Precision Optics", "country": "JP", "lead_time_days": 8, "defect_rate": 0.01, "late_delivery_count": 0, "order_value": 380000},
    {"supplier_id": "SUP-DE-002", "name": "Berlin Advanced Polymers AG", "country": "DE", "lead_time_days": 45, "defect_rate": 0.03, "late_delivery_count": 2, "order_value": 290000},
]

SAMPLE_CSV_DATA = """supplier_id,name,country,lead_time_days,defect_rate,late_delivery_count,order_value
SUP-VN-001,Saigon Steel Corp,VN,14,0.03,2,120000
SUP-CN-001,Shanghai Electronics Co.,CN,21,0.05,5,350000
SUP-TH-001,Bangkok Rubber Industries,TH,18,0.04,3,85000
SUP-IN-001,Mumbai Textile Exports,IN,25,0.08,8,65000
SUP-US-001,Detroit Precision Parts,US,10,0.02,1,450000
SUP-DE-001,Stuttgart Machining GmbH,DE,12,0.01,0,500000
SUP-JP-001,Osaka Semiconductor Ltd,JP,15,0.02,1,280000
SUP-KR-001,Busan Chemical Works,KR,20,0.06,4,175000
SUP-BD-001,Dhaka Garment Solutions,BD,30,0.12,12,42000
SUP-VN-002,Hanoi Plastics Manufacturing,VN,16,0.05,3,95000
SUP-CN-002,Shenzhen Circuit Board Tech,CN,28,0.09,7,220000
SUP-TH-002,Chiang Mai Auto Parts,TH,22,0.07,6,130000
SUP-IN-002,Chennai Forge & Foundry,IN,35,0.10,10,78000
SUP-JP-002,Tokyo Precision Optics,JP,8,0.01,0,380000
SUP-DE-002,Berlin Advanced Polymers AG,DE,45,0.03,2,290000
SUP-KR-002,Seoul Microchip Inc,KR,19,0.04,3,195000
SUP-VN-003,Da Nang Ceramic Works,VN,17,0.06,4,55000
SUP-US-002,Austin Battery Systems,US,11,0.02,1,410000
SUP-CN-003,Guangzhou Packaging Group,CN,24,0.07,6,145000
SUP-BD-002,Chittagong Jute Exports,BD,40,0.15,20,28000
"""

RAG_DOCUMENTS: list[dict] = [
    {
        "doc_id": "DOC-001",
        "title": "Q1 2025 Supplier Quality Report",
        "content": (
            "Overall supplier defect rate decreased from 5.2% to 4.1% compared to Q4 2024. "
            "Top performers include Stuttgart Machining GmbH with a 1% defect rate and "
            "Tokyo Precision Optics at 1.2%. Key areas of concern remain with Dhaka Garment Solutions "
            "at 12% defect rate, requiring corrective action plan submission by March 2025. "
            "Six sigma improvement initiatives launched across 4 supplier facilities in Vietnam and Thailand."
        ),
        "metadata": {"department": "quality", "allowed_roles": ["viewer", "analyst", "manager", "admin"], "doc_type": "report", "created_date": "2025-04-01"},
    },
    {
        "doc_id": "DOC-002",
        "title": "Supplier Compliance Audit - ISO 9001 Status",
        "content": (
            "Annual compliance audit completed for all tier-1 suppliers. 12 of 15 suppliers hold current "
            "ISO 9001:2015 certification. Non-certified suppliers: Dhaka Garment Solutions (audit scheduled Q2), "
            "Chittagong Jute Exports (remediation in progress), and Da Nang Ceramic Works (application submitted). "
            "All German and Japanese suppliers maintain additional IATF 16949 automotive certification. "
            "Recommendation: suspend new orders to non-certified suppliers until compliance achieved."
        ),
        "metadata": {"department": "compliance", "allowed_roles": ["analyst", "manager", "admin"], "doc_type": "audit", "created_date": "2025-03-15"},
    },
    {
        "doc_id": "DOC-003",
        "title": "2025 Raw Material Pricing Forecast",
        "content": (
            "Steel prices projected to increase 8-12% due to global demand recovery. Semiconductor component "
            "costs stabilizing after 18-month decline. Rubber prices volatile due to Southeast Asian weather patterns. "
            "Recommended hedging strategy: lock in Q3-Q4 steel contracts with Saigon Steel Corp and Stuttgart Machining. "
            "Chemical raw materials stable with slight downward trend. Textile costs rising 5% due to cotton supply constraints."
        ),
        "metadata": {"department": "procurement", "allowed_roles": ["manager", "admin"], "doc_type": "forecast", "created_date": "2025-02-20"},
    },
    {
        "doc_id": "DOC-004",
        "title": "Supply Chain Risk Assessment Framework",
        "content": (
            "Risk scoring methodology: composite score based on financial stability (25%), delivery reliability (25%), "
            "quality metrics (25%), and geopolitical risk (25%). Suppliers with composite scores above 0.7 classified "
            "as high-risk requiring monthly reviews. Medium-risk (0.4-0.7) reviewed quarterly. Current high-risk "
            "suppliers: Dhaka Garment Solutions (0.82), Chittagong Jute Exports (0.78), Chennai Forge & Foundry (0.71). "
            "Mitigation strategies include dual-sourcing for critical components and safety stock buffers."
        ),
        "metadata": {"department": "risk", "allowed_roles": ["viewer", "analyst", "manager", "admin"], "doc_type": "framework", "created_date": "2025-01-10"},
    },
    {
        "doc_id": "DOC-005",
        "title": "Confidential: Supplier Contract Negotiations Q2 2025",
        "content": (
            "Negotiation targets for upcoming contract renewals. Shanghai Electronics: target 8% cost reduction "
            "with volume commitment increase. Bangkok Rubber Industries: renegotiate penalty clauses for late delivery. "
            "Detroit Precision Parts: extend contract 3 years with price lock at current rates. Osaka Semiconductor: "
            "request JIT delivery capability to reduce warehousing costs. Budget authority up to $2.5M for advance "
            "payments to secure favorable terms with Stuttgart Machining and Berlin Advanced Polymers."
        ),
        "metadata": {"department": "procurement", "allowed_roles": ["admin"], "doc_type": "confidential", "created_date": "2025-04-05"},
    },
    {
        "doc_id": "DOC-006",
        "title": "Logistics Performance Dashboard - March 2025",
        "content": (
            "On-time delivery rate: 87.3% (target 95%). Average lead time: 21.4 days across all suppliers. "
            "Top performing routes: DE-VN via Hamburg port (98% on-time), JP-VN via Yokohama (96% on-time). "
            "Underperforming routes: BD-VN via Chittagong (62% on-time), IN-VN via Mumbai port (71% on-time). "
            "Freight cost per unit increased 4.2% month-over-month. Container availability improved in Asia-Pacific "
            "region. Recommended action: shift BD shipments to air freight for critical orders."
        ),
        "metadata": {"department": "logistics", "allowed_roles": ["viewer", "analyst", "manager", "admin"], "doc_type": "dashboard", "created_date": "2025-04-10"},
    },
    {
        "doc_id": "DOC-007",
        "title": "Supplier Onboarding Guidelines v3.1",
        "content": (
            "Standard onboarding process for new suppliers: Phase 1 - Document collection (business license, "
            "financial statements, quality certifications). Phase 2 - Factory audit (minimum score 75/100). "
            "Phase 3 - Sample order evaluation (3 pilot batches). Phase 4 - Contract negotiation and payment "
            "terms setup (Net-30 standard, Net-60 for orders above $200K). Approval required from procurement "
            "manager for orders up to $100K, VP approval for $100K-$500K, C-level for above $500K."
        ),
        "metadata": {"department": "procurement", "allowed_roles": ["analyst", "manager", "admin"], "doc_type": "guideline", "created_date": "2024-11-01"},
    },
    {
        "doc_id": "DOC-008",
        "title": "Environmental Compliance Report - Supplier Carbon Footprint",
        "content": (
            "Scope 3 emissions tracking initiated for all tier-1 suppliers. Total supply chain carbon footprint: "
            "12,450 tonnes CO2e for FY2024. Highest emitters: Shanghai Electronics (2,100t), Shenzhen Circuit Board "
            "Tech (1,850t), Stuttgart Machining (1,200t). Carbon reduction targets set: 15% reduction by 2027. "
            "Green supplier incentive program launched offering 2% price premium for suppliers achieving ISO 14001 "
            "certification. Currently 6 of 15 suppliers ISO 14001 certified."
        ),
        "metadata": {"department": "sustainability", "allowed_roles": ["viewer", "analyst", "manager", "admin"], "doc_type": "report", "created_date": "2025-03-01"},
    },
    {
        "doc_id": "DOC-009",
        "title": "Internal: Supplier Financial Health Assessment",
        "content": (
            "Quarterly financial health review of critical suppliers. Dhaka Garment Solutions showing liquidity "
            "concerns with current ratio at 0.8 (below 1.0 threshold). Chennai Forge & Foundry reported declining "
            "revenue of 15% YoY. Recommendation: increase payment frequency to weekly for at-risk suppliers to "
            "maintain production continuity. All Japanese and German suppliers maintain strong financial positions. "
            "Busan Chemical Works completed successful debt refinancing, improving credit outlook."
        ),
        "metadata": {"department": "finance", "allowed_roles": ["manager", "admin"], "doc_type": "assessment", "created_date": "2025-03-20"},
    },
]

GOLDEN_QUESTIONS: list[dict] = [
    {
        "question": "What is the overall supplier defect rate trend?",
        "expected_answer_keywords": ["decreased", "5.2%", "4.1%", "Q4 2024"],
        "expected_doc_ids": ["DOC-001"],
        "required_role": "viewer",
    },
    {
        "question": "Which suppliers are not ISO 9001 certified?",
        "expected_answer_keywords": ["Dhaka Garment", "Chittagong Jute", "Da Nang Ceramic"],
        "expected_doc_ids": ["DOC-002"],
        "required_role": "analyst",
    },
    {
        "question": "What is the steel price forecast for 2025?",
        "expected_answer_keywords": ["increase", "8-12%", "global demand"],
        "expected_doc_ids": ["DOC-003"],
        "required_role": "manager",
    },
    {
        "question": "How is supplier risk score calculated?",
        "expected_answer_keywords": ["financial stability", "delivery reliability", "quality metrics", "geopolitical"],
        "expected_doc_ids": ["DOC-004"],
        "required_role": "viewer",
    },
    {
        "question": "What are the contract negotiation targets for Shanghai Electronics?",
        "expected_answer_keywords": ["8% cost reduction", "volume commitment"],
        "expected_doc_ids": ["DOC-005"],
        "required_role": "admin",
    },
    {
        "question": "What is the on-time delivery rate?",
        "expected_answer_keywords": ["87.3%", "target 95%"],
        "expected_doc_ids": ["DOC-006"],
        "required_role": "viewer",
    },
    {
        "question": "What are the supplier onboarding phases?",
        "expected_answer_keywords": ["document collection", "factory audit", "sample order", "contract negotiation"],
        "expected_doc_ids": ["DOC-007"],
        "required_role": "analyst",
    },
    {
        "question": "What is the total supply chain carbon footprint?",
        "expected_answer_keywords": ["12,450 tonnes", "CO2e", "FY2024"],
        "expected_doc_ids": ["DOC-008"],
        "required_role": "viewer",
    },
    {
        "question": "Which suppliers have financial health concerns?",
        "expected_answer_keywords": ["Dhaka Garment", "liquidity", "Chennai Forge", "declining revenue"],
        "expected_doc_ids": ["DOC-009"],
        "required_role": "manager",
    },
    {
        "question": "Which are the highest-risk suppliers?",
        "expected_answer_keywords": ["Dhaka Garment", "Chittagong Jute", "Chennai Forge", "0.82", "0.78", "0.71"],
        "expected_doc_ids": ["DOC-004"],
        "required_role": "viewer",
    },
    {
        "question": "What are the best performing shipping routes?",
        "expected_answer_keywords": ["DE-VN", "Hamburg", "98%", "JP-VN", "Yokohama", "96%"],
        "expected_doc_ids": ["DOC-006"],
        "required_role": "viewer",
    },
    {
        "question": "What approval levels are required for large supplier orders?",
        "expected_answer_keywords": ["procurement manager", "$100K", "VP", "$500K", "C-level"],
        "expected_doc_ids": ["DOC-007"],
        "required_role": "analyst",
    },
]


_CHUNK_SIZE = 200


def _chunk_documents(docs: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    for doc in docs:
        content = doc["content"]
        words = content.split()
        current_chunk: list[str] = []
        current_len = 0

        for word in words:
            word_len = len(word) + (1 if current_chunk else 0)
            if current_len + word_len > _CHUNK_SIZE and current_chunk:
                chunks.append(
                    {
                        "doc_id": doc["doc_id"],
                        "title": doc["title"],
                        "content": doc["content"],
                        "chunk_text": " ".join(current_chunk),
                        "metadata": doc["metadata"],
                    }
                )
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += word_len

        if current_chunk:
            chunks.append(
                {
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "chunk_text": " ".join(current_chunk),
                    "metadata": doc["metadata"],
                }
            )

    return chunks


def seed_all() -> None:
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # The vector store is in-memory, so it must be re-seeded on every startup.
    store = get_vector_store()
    if not store.documents:
        chunks = _chunk_documents(RAG_DOCUMENTS)
        store.add_documents(chunks)

    golden_path = data_dir / "golden_questions.json"
    if not golden_path.exists():
        golden_path.write_text(json.dumps(GOLDEN_QUESTIONS, indent=2), encoding="utf-8")
