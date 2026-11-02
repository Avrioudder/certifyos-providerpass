"""
Data models and strongly-typed Pydantic schemas for CertifyOS ProviderPass.
Supports both runtime validation and structured LLM output generation.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    HITL_REVIEW_REQUIRED = "HITL_REVIEW_REQUIRED"
    ESCALATE_CREDENTIALING_COMMITTEE = "ESCALATE_CREDENTIALING_COMMITTEE"
    HARD_BLOCK_SANCTIONED = "HARD_BLOCK_SANCTIONED"


class VerificationVector(str, Enum):
    IDENTITY_NPI = "IDENTITY_NPI"
    STATE_LICENSE = "STATE_LICENSE"
    DEA_REGISTRATION = "DEA_REGISTRATION"
    OIG_SAM_EXCLUSIONS = "OIG_SAM_EXCLUSIONS"
    NPDB_MALPRACTICE = "NPDB_MALPRACTICE"
    DIRECTORY_INTEGRITY = "DIRECTORY_INTEGRITY"


class DiscrepancySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SourceDiscrepancy(BaseModel):
    vector: VerificationVector = Field(..., description="Verification dimension where the discrepancy occurred")
    field_name: str = Field(..., description="Field name in dispute")
    intake_value: str = Field(..., description="Value provided on the provider intake packet")
    primary_source_value: str = Field(..., description="Verified value returned by the primary source authority")
    severity: DiscrepancySeverity = Field(..., description="Risk severity of this discrepancy")
    description: str = Field(..., description="Clear explanation of the mismatch and regulatory impact")
    suggested_action: str = Field(..., description="Prescribed remediation workflow")


class ComplianceCheck(BaseModel):
    standard: str = Field(..., description="Regulatory standard ID (NCQA, URAC, CMS)")
    passed: bool = Field(..., description="Whether the requirement passed without block")
    evidence: str = Field(..., description="Audit evidence citation")


class PrimarySourceRecord(BaseModel):
    source_name: str
    status: str
    verified_at: str
    record_details: Dict[str, Any] = Field(default_factory=dict)


class ProviderLicense(BaseModel):
    state: str
    license_number: str
    status: str
    expiration_date: str


class ProviderIntake(BaseModel):
    provider_id: str
    npi: str
    full_name: str
    specialty: str
    taxonomy_code: str
    state_licenses: List[ProviderLicense]
    dea_number: Optional[str] = None
    practice_address: str
    hospital_affiliations: List[str] = Field(default_factory=list)
    malpractice_claims_declared: int = 0
    submitted_date: str


class VerificationResult(BaseModel):
    provider_id: str
    npi: str
    cred_trust_score: int = Field(..., ge=0, le=100, description="Normalized credential trust score (0-100)")
    status: VerificationStatus
    executive_summary: str
    discrepancies: List[SourceDiscrepancy] = Field(default_factory=list)
    compliance_checks: List[ComplianceCheck] = Field(default_factory=list)
    outreach_draft: Optional[str] = Field(None, description="Pre-composed clarification message ready for provider outreach")
    hitl_recommendation: str = Field(..., description="Actionable recommendation for the human credentialing analyst")
    audited_at: str
    model_used: str = "certifyos-hybrid-engine-v1"


class ReviewActionRequest(BaseModel):
    provider_id: str
    action: str = Field(..., description="Action taken: APPROVE, REQUEST_CLARIFICATION, ESCALATE, RESOLVE")
    reviewer_notes: str
    reviewer_name: str = "Credentialing Analyst"
    override_status: Optional[VerificationStatus] = None
