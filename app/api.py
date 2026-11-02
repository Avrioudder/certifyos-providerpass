"""
FastAPI REST API router and application for CertifyOS ProviderPass.
Exposes endpoints for provider intake verification, batch auditing, and human-in-the-loop decisions.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any, List

from app.models import VerificationResult, ReviewActionRequest
from app.mock_data import MOCK_PROVIDERS
from app.engine import engine, get_all_mock_evaluations

api_app = FastAPI(
    title="CertifyOS ProviderPass API",
    description="Autonomous Provider Intake & Primary Source Verification (PSV) Anomaly Resolution Engine",
    version="1.0.0"
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for reviewer actions during session
REVIEW_AUDIT_TRAIL: List[Dict[str, Any]] = []


@api_app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CertifyOS ProviderPass",
        "timestamp": datetime.utcnow().isoformat(),
        "engine_mode": "Groq-Llama3/Deterministic Hybrid"
    }


@api_app.get("/api/providers")
def list_providers():
    return get_all_mock_evaluations()


@api_app.get("/api/providers/{provider_id}")
def get_provider(provider_id: str):
    for item in MOCK_PROVIDERS:
        if item["intake"]["provider_id"] == provider_id:
            eval_res = engine.run_ai_verification(item["intake"], item["primary_sources"])
            return {
                "intake": item["intake"],
                "primary_sources": item["primary_sources"],
                "evaluation": eval_res
            }
    raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")


@api_app.post("/api/verify", response_model=VerificationResult)
def verify_provider(payload: Dict[str, Any]):
    intake = payload.get("intake")
    sources = payload.get("primary_sources")
    if not intake or not sources:
        raise HTTPException(status_code=400, detail="Missing 'intake' or 'primary_sources' object")
    return engine.run_ai_verification(intake, sources)


@api_app.post("/api/review")
def record_review_action(action: ReviewActionRequest):
    record = {
        "provider_id": action.provider_id,
        "action": action.action,
        "reviewer_notes": action.reviewer_notes,
        "reviewer_name": action.reviewer_name,
        "override_status": action.override_status.value if action.override_status else None,
        "recorded_at": datetime.utcnow().isoformat()
    }
    REVIEW_AUDIT_TRAIL.append(record)
    return {"status": "success", "audit_record": record}


@api_app.get("/api/audit-trail")
def get_audit_trail():
    return {"audit_trail": REVIEW_AUDIT_TRAIL}
