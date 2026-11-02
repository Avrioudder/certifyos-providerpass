"""
Core Verification & AI Engine for CertifyOS ProviderPass.
Executes Hybrid RAG Primary Source Verification with Groq Llama-3 integration
and a robust deterministic heuristic engine fallback for offline and air-gapped resilience.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from app.models import (
    VerificationResult,
    VerificationStatus,
    VerificationVector,
    DiscrepancySeverity,
    SourceDiscrepancy,
    ComplianceCheck,
    ProviderIntake,
    ReviewActionRequest,
)
from app.mock_data import MOCK_PROVIDERS

load_dotenv()

logger = logging.getLogger("certifyos.engine")
logging.basicConfig(level=logging.INFO)


class VerificationEngine:
    def __init__(self, groq_api_key: Optional[str] = None):
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = None
        if self.api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}. Falling back to deterministic engine.")

    def run_deterministic_verification(self, intake: Dict[str, Any], sources: Dict[str, Any]) -> VerificationResult:
        """
        Deterministic, rule-based Primary Source Verification (PSV) engine.
        Implements strict NCQA CR3, URAC, and CMS No Surprises Act validation logic.
        """
        discrepancies: List[SourceDiscrepancy] = []
        compliance_checks: List[ComplianceCheck] = []
        cred_score = 100

        # Vector 1: Identity & NPI Registry Check
        nppes = sources.get("nppes", {})
        intake_name = intake.get("full_name", "").strip().upper().replace("DR. ", "")
        nppes_legal = nppes.get("legal_name", "").strip().upper()
        nppes_others = [n.strip().upper() for n in nppes.get("other_names", [])]

        if nppes.get("status") != "ACTIVE":
            cred_score -= 50
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.IDENTITY_NPI,
                    field_name="nppes_status",
                    intake_value="Active Clinical Provider",
                    primary_source_value=f"NPPES Status: {nppes.get('status')}",
                    severity=DiscrepancySeverity.CRITICAL,
                    description="Provider NPI record is inactive or deactivated in federal NPPES registry.",
                    suggested_action="Immediately halt enrollment and issue hard block notice."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="CMS Provider Identification (45 CFR § 162.410)",
                passed=False,
                evidence="NPI deactivated in National Plan and Provider Enumeration System."
            ))
        else:
            name_matched = (intake_name in nppes_legal) or (nppes_legal in intake_name) or any(intake_name in alt for alt in nppes_others)
            if not name_matched:
                cred_score -= 15
                discrepancies.append(
                    SourceDiscrepancy(
                        vector=VerificationVector.IDENTITY_NPI,
                        field_name="legal_name_match",
                        intake_value=intake.get("full_name"),
                        primary_source_value=nppes_legal,
                        severity=DiscrepancySeverity.MEDIUM,
                        description=f"Intake name '{intake.get('full_name')}' does not exact-match NPPES legal name '{nppes_legal}'. Alias check required.",
                        suggested_action="Review government photo ID and alias declaration form."
                    )
                )
                compliance_checks.append(ComplianceCheck(
                    standard="NCQA CR1 - Provider Identity Verification",
                    passed=False,
                    evidence="Name divergence flagged between application and federal registry."
                ))
            else:
                compliance_checks.append(ComplianceCheck(
                    standard="NCQA CR1 - Provider Identity Verification",
                    passed=True,
                    evidence=f"Active NPI verified with matching identity on NPPES ({nppes_legal})."
                ))

        # Vector 2: State Medical Boards
        boards = sources.get("state_boards", [])
        state_license_passed = True
        for b in boards:
            b_status = b.get("status", "").upper()
            b_disc = b.get("disciplinary_actions", "").upper()
            b_name = b.get("name_on_record", "").upper()

            if "REVOKED" in b_status or "SUSPENDED" in b_status or b_disc != "NONE":
                cred_score -= 60
                state_license_passed = False
                discrepancies.append(
                    SourceDiscrepancy(
                        vector=VerificationVector.STATE_LICENSE,
                        field_name=f"state_license_{b.get('board')}",
                        intake_value="Active Unencumbered License Declared",
                        primary_source_value=f"{b_status} - Disciplinary: {b.get('disciplinary_actions')}",
                        severity=DiscrepancySeverity.CRITICAL,
                        description=f"Sanction or license suspension active on {b.get('board')}.",
                        suggested_action="Automatic referral to Chief Medical Officer and Credentialing Committee."
                    )
                )
            elif (intake_name not in b_name) and not any(b_name in alt for alt in nppes_others):
                cred_score -= 10
                discrepancies.append(
                    SourceDiscrepancy(
                        vector=VerificationVector.STATE_LICENSE,
                        field_name="license_holder_name",
                        intake_value=intake.get("full_name"),
                        primary_source_value=b.get("name_on_record"),
                        severity=DiscrepancySeverity.LOW,
                        description=f"State medical board reflects prior or hyphenated surname '{b.get('name_on_record')}'.",
                        suggested_action="Request marriage/alias documentation to satisfy NCQA audit trail."
                    )
                )

        compliance_checks.append(ComplianceCheck(
            standard="NCQA CR3 - State Medical Licensing Verification",
            passed=state_license_passed,
            evidence="All primary state medical boards queried directly via API." if state_license_passed else "Adverse action or status revocation detected."
        ))

        # Vector 3: DEA Registration
        dea = sources.get("dea", {})
        dea_status = dea.get("status", "").upper()
        if "SURRENDERED" in dea_status or "REVOKED" in dea_status:
            cred_score -= 50
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.DEA_REGISTRATION,
                    field_name="dea_status",
                    intake_value=f"DEA: {intake.get('dea_number')}",
                    primary_source_value=f"DEA Status: {dea_status}",
                    severity=DiscrepancySeverity.CRITICAL,
                    description="DEA registration has been surrendered for cause or revoked.",
                    suggested_action="Immediate hard block from prescribing panels."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="DEA Controlled Substance Act Compliance",
                passed=False,
                evidence=f"DEA certificate revoked or surrendered ({dea_status})."
            ))
        elif "EXPIRING" in dea_status:
            cred_score -= 8
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.DEA_REGISTRATION,
                    field_name="dea_expiration",
                    intake_value="Active DEA",
                    primary_source_value=f"Expires {dea.get('expiration_date')}",
                    severity=DiscrepancySeverity.MEDIUM,
                    description=f"DEA certificate expires imminently on {dea.get('expiration_date')}.",
                    suggested_action="Issue automated reminder for renewed DEA certificate prior to final committee signoff."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="DEA Controlled Substance Act Compliance",
                passed=True,
                evidence=f"Active registration verified; renewal renewal window flagged ({dea.get('expiration_date')})."
            ))
        elif dea.get("ny_cross_state_certificate") == "EXPIRED":
            cred_score -= 10
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.DEA_REGISTRATION,
                    field_name="multi_state_dea",
                    intake_value="Multi-state Practice Approval",
                    primary_source_value="NY cross-state certificate expired",
                    severity=DiscrepancySeverity.MEDIUM,
                    description="DEA certificate is active in California but cross-state dispensing credential in NY has lapsed.",
                    suggested_action="Restrict NY prescriptive authority or obtain updated cross-state certificate."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="DEA Controlled Substance Act Compliance",
                passed=True,
                evidence="Primary state active; secondary state endorsement requires renewal."
            ))
        else:
            compliance_checks.append(ComplianceCheck(
                standard="DEA Controlled Substance Act Compliance",
                passed=True,
                evidence=f"Active DEA certificate ({dea.get('registration_number')}) verified with Schedules {dea.get('schedules')}."
            ))

        # Vector 4: OIG / SAM Sanctions & Exclusions
        oig = sources.get("oig_sam", {})
        if oig.get("leie_status") != "CLEAR" or oig.get("sam_exclusion") != "NONE":
            cred_score = min(cred_score, 15)
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.OIG_SAM_EXCLUSIONS,
                    field_name="federal_exclusion",
                    intake_value="No Exclusions Declared",
                    primary_source_value=f"LEIE: {oig.get('leie_status')} | Type: {oig.get('exclusion_type')}",
                    severity=DiscrepancySeverity.CRITICAL,
                    description="Provider is listed on federal OIG List of Excluded Individuals/Entities (LEIE). Federal payment prohibited.",
                    suggested_action="Execute immediate statutory hard block. Notify compliance officer within 24 hours."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="HHS OIG LEIE & SAM Exclusions Screening (42 CFR § 1001)",
                passed=False,
                evidence=f"Excluded under statutory authority: {oig.get('exclusion_type')}."
            ))
        else:
            compliance_checks.append(ComplianceCheck(
                standard="HHS OIG LEIE & SAM Exclusions Screening (42 CFR § 1001)",
                passed=True,
                evidence="Negative exclusion match confirmed on OIG LEIE and GSA SAM lists."
            ))

        # Vector 5: NPDB Malpractice Disclosure vs Primary Records
        npdb = sources.get("npdb", {})
        actual_payments = len(npdb.get("malpractice_payments", []))
        declared_payments = intake.get("malpractice_claims_declared", 0)

        if actual_payments > declared_payments:
            cred_score -= 25
            payment_details = npdb.get("malpractice_payments", [])[0]
            amount = payment_details.get("amount", 0)
            allegation = payment_details.get("allegation", "Undisclosed settlement")
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.NPDB_MALPRACTICE,
                    field_name="malpractice_disclosure_divergence",
                    intake_value=f"Declared: {declared_payments} claims",
                    primary_source_value=f"NPDB Found: {actual_payments} claim(s) (${amount:,})",
                    severity=DiscrepancySeverity.HIGH,
                    description=f"NPDB report reflects a ${amount:,} settlement for '{allegation}' not disclosed on intake application.",
                    suggested_action="Escalate to Credentialing Committee with mandatory explanatory statement from provider."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="NCQA CR4 - National Practitioner Data Bank Query",
                passed=False,
                evidence=f"Malpractice payment record detected with disclosure gap."
            ))
        else:
            compliance_checks.append(ComplianceCheck(
                standard="NCQA CR4 - National Practitioner Data Bank Query",
                passed=True,
                evidence=f"NPDB queried successfully with zero adverse actions or unaligned settlements."
            ))

        # Vector 6: Directory Integrity & No Surprises Act
        dir_check = sources.get("directory_verification", {})
        if dir_check.get("cms_directory_flag") != "PASS":
            cred_score -= 15
            discrepancies.append(
                SourceDiscrepancy(
                    vector=VerificationVector.DIRECTORY_INTEGRITY,
                    field_name="practice_location_deliverability",
                    intake_value=intake.get("practice_address"),
                    primary_source_value=f"Facility Type: {dir_check.get('address_type')} ({dir_check.get('cms_directory_flag')})",
                    severity=DiscrepancySeverity.MEDIUM,
                    description="Practice location flags as non-clinical or commercial mail drop (potential ghost network listing).",
                    suggested_action="Request physical facility lease or clinical site verification attestation."
                )
            )
            compliance_checks.append(ComplianceCheck(
                standard="CMS No Surprises Act Provider Directory Accuracy (45 CFR § 149)",
                passed=False,
                evidence=f"Address verification failed clinical facility criteria: {dir_check.get('address_type')}."
            ))
        else:
            compliance_checks.append(ComplianceCheck(
                standard="CMS No Surprises Act Provider Directory Accuracy (45 CFR § 149)",
                passed=True,
                evidence="USPS deliverable clinical medical facility confirmed."
            ))

        cred_score = max(5, min(100, cred_score))

        # Determine Status
        has_critical = any(d.severity == DiscrepancySeverity.CRITICAL for d in discrepancies)
        has_high = any(d.severity == DiscrepancySeverity.HIGH for d in discrepancies)
        has_medium = any(d.severity == DiscrepancySeverity.MEDIUM for d in discrepancies)

        if has_critical:
            status = VerificationStatus.HARD_BLOCK_SANCTIONED
            hitl_rec = "Statutory violation or sanction identified. Do not credential. Forward file to Compliance & Legal."
        elif has_high:
            status = VerificationStatus.ESCALATE_CREDENTIALING_COMMITTEE
            hitl_rec = "NPDB claim or unaligned disclosure requires formal peer review at the next Credentialing Committee session."
        elif has_medium or len(discrepancies) > 0:
            status = VerificationStatus.HITL_REVIEW_REQUIRED
            hitl_rec = "Administrative reconciliation needed. Review alias or cross-state documentation and proceed upon approval."
        else:
            status = VerificationStatus.AUTO_APPROVE
            hitl_rec = "All primary sources verified active and unencumbered. Safe for automated committee consent-agenda approval."

        # Draft Outreach if HITL or Escalated
        outreach_draft = None
        if discrepancies and not has_critical:
            reasons = "\n".join([f"  - {d.field_name}: {d.description} (Remediation: {d.suggested_action})" for d in discrepancies])
            outreach_draft = (
                f"Subject: Action Required: Primary Source Credentialing Verification for {intake.get('full_name')} (NPI: {intake.get('npi')})\n\n"
                f"Dear {intake.get('full_name')},\n\n"
                f"Thank you for submitting your credentialing package through our CertifyOS network intake portal.\n\n"
                f"During automated Primary Source Verification (PSV) against state licensing registries and federal databases, "
                f"our system flagged the following item(s) requiring clarification or updated documentation before your file can be submitted for committee approval:\n\n"
                f"{reasons}\n\n"
                f"Please upload the requested documentation directly into your provider portal or reply to this secure notice within 5 business days to prevent onboarding delays.\n\n"
                f"Best regards,\n"
                f"CertifyOS Credentialing Operations Team"
            )

        summary = (
            f"Provider {intake.get('full_name')} evaluated with CredTrust score {cred_score}/100. "
            f"Status: {status.value}. Found {len(discrepancies)} discrepancy(ies) across "
            f"{len(compliance_checks)} regulatory audit vectors."
        )

        return VerificationResult(
            provider_id=intake.get("provider_id"),
            npi=intake.get("npi"),
            cred_trust_score=cred_score,
            status=status,
            executive_summary=summary,
            discrepancies=discrepancies,
            compliance_checks=compliance_checks,
            outreach_draft=outreach_draft,
            hitl_recommendation=hitl_rec,
            audited_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            model_used="certifyos-deterministic-rules-engine-v1"
        )

    def run_ai_verification(self, intake: Dict[str, Any], sources: Dict[str, Any]) -> VerificationResult:
        """
        Executes Groq/Llama-3-70b verification with strict schema enforcement.
        Falls back to the deterministic engine if API key is absent, rate-limited, or call fails.
        """
        if not self.groq_client:
            return self.run_deterministic_verification(intake, sources)

        # Baseline deterministic result as grounding reference
        baseline = self.run_deterministic_verification(intake, sources)

        prompt = f"""You are the senior Primary Source Verification (PSV) intelligence engine for CertifyOS, an enterprise healthcare provider data platform.
Analyze the provider intake submission against verified primary sources (NPPES, State Medical Boards, DEA, NPDB, OIG/SAM, and USPS Directory Integrity).

Input Data:
Provider Intake:
{json.dumps(intake, indent=2)}

Primary Source Records:
{json.dumps(sources, indent=2)}

Baseline Rules Audit:
{baseline.model_dump_json(indent=2)}

Respond with a valid JSON object matching this schema:
{{
  "cred_trust_score": <int 0-100>,
  "status": "<AUTO_APPROVE | HITL_REVIEW_REQUIRED | ESCALATE_CREDENTIALING_COMMITTEE | HARD_BLOCK_SANCTIONED>",
  "executive_summary": "<crisp, professional 2-sentence executive summary>",
  "discrepancies": [
     {{
       "vector": "<IDENTITY_NPI | STATE_LICENSE | DEA_REGISTRATION | OIG_SAM_EXCLUSIONS | NPDB_MALPRACTICE | DIRECTORY_INTEGRITY>",
       "field_name": "<name>",
       "intake_value": "<val>",
       "primary_source_value": "<val>",
       "severity": "<INFO | LOW | MEDIUM | HIGH | CRITICAL>",
       "description": "<string>",
       "suggested_action": "<string>"
     }}
  ],
  "hitl_recommendation": "<Clear instruction for the human credentialing analyst>",
  "outreach_draft": "<Ready-to-send email to provider if clarification needed, else null>"
}}

Return ONLY valid JSON.
"""

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a specialized healthcare regulatory compliance AI. Output strict JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_content = chat_completion.choices[0].message.content
            parsed = json.loads(raw_content)

            status_str = parsed.get("status", baseline.status.value)
            try:
                valid_status = VerificationStatus(status_str)
            except Exception:
                valid_status = baseline.status

            discs = []
            for d in parsed.get("discrepancies", []):
                try:
                    discs.append(SourceDiscrepancy(**d))
                except Exception:
                    pass

            if not discs:
                discs = baseline.discrepancies

            return VerificationResult(
                provider_id=intake.get("provider_id"),
                npi=intake.get("npi"),
                cred_trust_score=int(parsed.get("cred_trust_score", baseline.cred_trust_score)),
                status=valid_status,
                executive_summary=parsed.get("executive_summary", baseline.executive_summary),
                discrepancies=discs,
                compliance_checks=baseline.compliance_checks,
                outreach_draft=parsed.get("outreach_draft", baseline.outreach_draft),
                hitl_recommendation=parsed.get("hitl_recommendation", baseline.hitl_recommendation),
                audited_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                model_used="groq/llama-3.3-70b-versatile"
            )
        except Exception as e:
            logger.warning(f"Groq API call encountered exception: {e}. Defaulting to deterministic engine.")
            res = baseline
            res.model_used = "certifyos-deterministic-fallback-v1"
            return res


# Global singleton instance
engine = VerificationEngine()


def get_all_mock_evaluations() -> List[Dict[str, Any]]:
    """Evaluates all mock providers and returns list of combined dicts."""
    results = []
    for item in MOCK_PROVIDERS:
        intake = item["intake"]
        sources = item["primary_sources"]
        eval_res = engine.run_ai_verification(intake, sources)
        results.append({
            "intake": intake,
            "primary_sources": sources,
            "evaluation": eval_res
        })
    return results
