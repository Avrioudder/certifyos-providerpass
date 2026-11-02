"""
CertifyOS ProviderPass — Autonomous Provider Intake & PSV Anomaly Resolution Copilot
Streamlit Enterprise Dashboard
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Set page config FIRST before any other streamlit calls
st.set_page_config(
    page_title="CertifyOS ProviderPass | PSV Anomaly Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment
load_dotenv()

# Internal imports
from app.models import (
    VerificationStatus,
    DiscrepancySeverity,
    ReviewActionRequest,
)
from app.mock_data import MOCK_PROVIDERS
from app.engine import VerificationEngine

# Initialize session state
if "review_history" not in st.session_state:
    st.session_state.review_history = []
if "selected_provider_id" not in st.session_state:
    st.session_state.selected_provider_id = "PRV-101"
if "overrides" not in st.session_state:
    st.session_state.overrides = {}
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

# Custom CSS for CertifyOS Branding
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0284C7;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-badge-auto {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-badge-hitl {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-badge-escalate {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-badge-blocked {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .discrepancy-card {
        border-left: 4px solid #EF4444;
        background-color: #FFF5F5;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .compliance-pill-pass {
        color: #15803D;
        font-weight: 600;
    }
    .compliance-pill-fail {
        color: #B91C1C;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("CertifyOS Engine")
    st.caption("Provider Intelligence & Credentialing OS")
    
    st.markdown("---")
    st.subheader("⚙️ Runtime & AI Configuration")
    user_key = st.text_input(
        "Groq API Key (Optional)",
        value=st.session_state.groq_api_key,
        type="password",
        help="Optional: Enter a Groq key to enable live Llama-3-70b inference. When omitted, the deterministic NCQA rules engine runs instantly."
    )
    if user_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = user_key

    engine_instance = VerificationEngine(groq_api_key=st.session_state.groq_api_key)
    
    if st.session_state.groq_api_key:
        st.success("🟢 Groq Llama-3.3-70b Active")
    else:
        st.info("⚡ NCQA Deterministic Rules Active (Zero Latency Fallback)")

    st.markdown("---")
    st.subheader("🎯 Triage Queue Filter")
    status_filter = st.selectbox(
        "Filter by Resolution Status",
        options=["ALL", "AUTO_APPROVE", "HITL_REVIEW_REQUIRED", "ESCALATE_CREDENTIALING_COMMITTEE", "HARD_BLOCK_SANCTIONED"]
    )

    st.markdown("---")
    st.subheader("📋 Forward Deployed PM Context")
    with st.expander("💼 Business Case & Unit Economics", expanded=False):
        st.markdown("""
        **Target Market Friction:**
        - Credentialing backlogs cost health systems **$7,500/day** in unbilled provider revenue.
        - Manual CVO (Credentialing Verification Org) processing costs **$280 - $450** per provider file.
        
        **ProviderPass Commercial Value:**
        - **33%+ Auto-Pass Rate** for pristine providers (reduces turnaround from 45 days to < 3 minutes).
        - **$35 / verification** automated cost structure.
        - Built-in audit trail for NCQA CR3 & URAC accreditation checks.
        """)


# Main Header
st.markdown('<div class="main-header">CertifyOS ProviderPass</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Provider Intake & Primary Source Verification (PSV) Anomaly Resolution Copilot</div>', unsafe_allow_html=True)

# Run Evaluations on All Mock Providers
all_evaluations = []
for p in MOCK_PROVIDERS:
    intake = p["intake"]
    sources = p["primary_sources"]
    pid = intake["provider_id"]
    
    # Run evaluation
    res = engine_instance.run_ai_verification(intake, sources)
    
    # Apply user override if present
    if pid in st.session_state.overrides:
        res.status = st.session_state.overrides[pid]
        
    all_evaluations.append({
        "intake": intake,
        "sources": sources,
        "result": res
    })

# Compute Executive KPIs
total_count = len(all_evaluations)
auto_count = sum(1 for e in all_evaluations if e["result"].status == VerificationStatus.AUTO_APPROVE)
hitl_count = sum(1 for e in all_evaluations if e["result"].status == VerificationStatus.HITL_REVIEW_REQUIRED)
escalate_count = sum(1 for e in all_evaluations if e["result"].status == VerificationStatus.ESCALATE_CREDENTIALING_COMMITTEE)
blocked_count = sum(1 for e in all_evaluations if e["result"].status == VerificationStatus.HARD_BLOCK_SANCTIONED)
avg_score = int(sum(e["result"].cred_trust_score for e in all_evaluations) / total_count)

# Render KPI Banner
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_count}</div>
        <div class="metric-label">Queue Ingested</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #16A34A;">{int((auto_count/total_count)*100)}%</div>
        <div class="metric-label">Auto-Approval Rate</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #D97706;">{hitl_count}</div>
        <div class="metric-label">Pending HITL Triage</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #DC2626;">{blocked_count}</div>
        <div class="metric-label">Sanction / Blocks</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score} <span style="font-size: 1rem; color: #64748B;">/100</span></div>
        <div class="metric-label">Avg CredTrust Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_queue, tab_sandbox, tab_fdpm = st.tabs([
    "🗂️ Verification Queue & Provider 360",
    "🧪 Live Intake Sandbox & Custom Verification",
    "📊 Forward Deployed PM Discovery & Strategy"
])

# Helper for status badge HTML
def get_badge_html(status: VerificationStatus):
    if status == VerificationStatus.AUTO_APPROVE:
        return '<span class="status-badge-auto">🟢 AUTO APPROVE</span>'
    elif status == VerificationStatus.HITL_REVIEW_REQUIRED:
        return '<span class="status-badge-hitl">🟡 HITL REVIEW</span>'
    elif status == VerificationStatus.ESCALATE_CREDENTIALING_COMMITTEE:
        return '<span class="status-badge-escalate">🟠 ESCALATE COMMITTEE</span>'
    else:
        return '<span class="status-badge-blocked">🔴 HARD BLOCK</span>'

# TAB 1: QUEUE & PROVIDER 360
with tab_queue:
    # Filter queue
    filtered_evals = all_evaluations
    if status_filter != "ALL":
        filtered_evals = [e for e in all_evaluations if e["result"].status.value == status_filter]

    q_col, detail_col = st.columns([1, 2], gap="large")

    with q_col:
        st.subheader(f"Provider Triage ({len(filtered_evals)})")
        
        for item in filtered_evals:
            intake = item["intake"]
            res = item["result"]
            pid = intake["provider_id"]
            is_selected = (pid == st.session_state.selected_provider_id)
            
            border_style = "2px solid #0284C7" if is_selected else "1px solid #E2E8F0"
            bg_style = "#F0F9FF" if is_selected else "#FFFFFF"
            
            with st.container():
                st.markdown(f"""
                <div style="border: {border_style}; background-color: {bg_style}; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #1E293B;">{intake['full_name']}</span>
                        <span style="font-size: 0.8rem; font-weight: 600; color: #64748B;">Score: {res.cred_trust_score}/100</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 2px;">
                        NPI: <code>{intake['npi']}</code> • {intake['specialty']}
                    </div>
                    <div style="margin-top: 6px;">
                        {get_badge_html(res.status)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Inspect Provider 360", key=f"btn_select_{pid}", use_container_width=True):
                    st.session_state.selected_provider_id = pid
                    st.rerun()

    # Detail Column
    with detail_col:
        # Find selected item
        active_item = next((e for e in all_evaluations if e["intake"]["provider_id"] == st.session_state.selected_provider_id), all_evaluations[0])
        intake = active_item["intake"]
        sources = active_item["sources"]
        res = active_item["result"]
        pid = intake["provider_id"]

        st.markdown(f"### 🩺 Provider 360: {intake['full_name']}")
        st.caption(f"Provider ID: **{pid}** | NPI: **{intake['npi']}** | Submission Date: **{intake['submitted_date']}** | Model: `{res.model_used}`")

        # Top alert banner
        if res.status == VerificationStatus.AUTO_APPROVE:
            st.success(f"**Verification Passed (CredTrust Score: {res.cred_trust_score}/100)**: {res.executive_summary}")
        elif res.status == VerificationStatus.HITL_REVIEW_REQUIRED:
            st.warning(f"**HITL Triage Required (CredTrust Score: {res.cred_trust_score}/100)**: {res.executive_summary}")
        elif res.status == VerificationStatus.ESCALATE_CREDENTIALING_COMMITTEE:
            st.error(f"**Committee Escalation Required (CredTrust Score: {res.cred_trust_score}/100)**: {res.executive_summary}")
        else:
            st.error(f"**STATUTORY HARD BLOCK (CredTrust Score: {res.cred_trust_score}/100)**: {res.executive_summary}")

        # Primary Source vs Intake Cross-Verification Matrix
        st.markdown("#### 🔍 Primary Source Verification (PSV) Matrix")
        
        matrix_data = []
        # NPPES
        matrix_data.append({
            "Verification Vector": "Identity / NPPES",
            "Intake Declared": intake["full_name"],
            "Primary Source Returned": sources.get("nppes", {}).get("legal_name", "N/A"),
            "Status": "✅ Verified" if not any(d.vector.value == "IDENTITY_NPI" for d in res.discrepancies) else "⚠️ Mismatch"
        })
        # State Boards
        boards = sources.get("state_boards", [])
        for b in boards:
            board_status = b.get("status")
            board_disc = b.get("disciplinary_actions", "NONE")
            matrix_data.append({
                "Verification Vector": f"State License ({b.get('board')})",
                "Intake Declared": f"Lic #{b.get('license_number')} (Active)",
                "Primary Source Returned": f"{board_status} (Disc: {board_disc})",
                "Status": "✅ Verified" if "REVOKED" not in board_status and "SUSPENDED" not in board_status else "❌ Encumbered"
            })
        # DEA
        dea = sources.get("dea", {})
        matrix_data.append({
            "Verification Vector": "DEA Registration",
            "Intake Declared": f"DEA #{intake.get('dea_number', 'N/A')}",
            "Primary Source Returned": f"Status: {dea.get('status')} (Exp: {dea.get('expiration_date')})",
            "Status": "✅ Verified" if "ACTIVE" in dea.get("status", "") and "EXPIRING" not in dea.get("status", "") else ("⚠️ Action Needed" if "EXPIRING" in dea.get("status", "") else "❌ Sanction")
        })
        # NPDB
        npdb = sources.get("npdb", {})
        claims_cnt = len(npdb.get("malpractice_payments", []))
        matrix_data.append({
            "Verification Vector": "NPDB Malpractice & Sanctions",
            "Intake Declared": f"{intake.get('malpractice_claims_declared', 0)} claims declared",
            "Primary Source Returned": f"{claims_cnt} payment record(s) on file",
            "Status": "✅ Clean" if claims_cnt == 0 else ("⚠️ Disclosure Gap" if claims_cnt > intake.get('malpractice_claims_declared', 0) else "ℹ️ Disclosed")
        })
        # OIG / SAM
        oig = sources.get("oig_sam", {})
        matrix_data.append({
            "Verification Vector": "HHS OIG LEIE Exclusions",
            "Intake Declared": "No Federal Debarment",
            "Primary Source Returned": f"LEIE: {oig.get('leie_status')} | SAM: {oig.get('sam_exclusion')}",
            "Status": "✅ Clear" if oig.get("leie_status") == "CLEAR" else "❌ EXCLUDED"
        })
        # Directory / Address
        dir_check = sources.get("directory_verification", {})
        matrix_data.append({
            "Verification Vector": "CMS Directory Facility Integrity",
            "Intake Declared": intake.get("practice_address")[:35] + "...",
            "Primary Source Returned": f"{dir_check.get('address_type')} ({dir_check.get('cms_directory_flag')})",
            "Status": "✅ Valid Site" if dir_check.get("cms_directory_flag") == "PASS" else "⚠️ Ghost Location Flag"
        })

        st.table(matrix_data)

        # Discrepancy Breakdown (if any)
        if res.discrepancies:
            st.markdown(f"#### ⚠️ Detected Discrepancies ({len(res.discrepancies)})")
            for d in res.discrepancies:
                st.markdown(f"""
                <div class="discrepancy-card">
                    <strong style="color: #991B1B;">[{d.severity.value}] {d.field_name}</strong><br>
                    <span><strong>Intake:</strong> {d.intake_value} &nbsp;|&nbsp; <strong>Verified Source:</strong> {d.primary_source_value}</span><br>
                    <span style="color: #4B5563; font-size: 0.9rem;">{d.description}</span><br>
                    <span style="color: #1E40AF; font-size: 0.85rem; font-weight: 600;">Suggested Action: {d.suggested_action}</span>
                </div>
                """, unsafe_allow_html=True)

        # Regulatory Compliance Checklist
        st.markdown("#### 📜 Regulatory Audit Trail (NCQA, URAC, CMS)")
        for c in res.compliance_checks:
            pill = "✅ PASS" if c.passed else "❌ FLAG"
            pill_color = "#16A34A" if c.passed else "#DC2626"
            st.markdown(f"- **<span style='color:{pill_color}'>{pill}</span> {c.standard}**: {c.evidence}", unsafe_allow_html=True)

        # Human-in-the-Loop Action Center
        st.markdown("---")
        st.markdown("#### ⚡ Human-in-the-Loop (HITL) Action Center")
        st.info(f"**Analyst Protocol Recommendation:** {res.hitl_recommendation}")

        hitl_col1, hitl_col2, hitl_col3 = st.columns(3)
        with hitl_col1:
            if st.button("✅ Approve with Exception", use_container_width=True, key=f"hitl_app_{pid}"):
                st.session_state.overrides[pid] = VerificationStatus.AUTO_APPROVE
                st.session_state.review_history.append({
                    "provider_id": pid,
                    "action": "APPROVED_OVERRIDE",
                    "note": "Analyst manually verified alias and documentation.",
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Provider status updated to Approved!")
                st.rerun()

        with hitl_col2:
            if st.button("🟠 Escalate to Committee", use_container_width=True, key=f"hitl_esc_{pid}"):
                st.session_state.overrides[pid] = VerificationStatus.ESCALATE_CREDENTIALING_COMMITTEE
                st.session_state.review_history.append({
                    "provider_id": pid,
                    "action": "ESCALATED",
                    "note": "Referred to quarterly Credentialing Committee review.",
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.warning("Provider escalated to Committee agenda.")
                st.rerun()

        with hitl_col3:
            if st.button("🔴 Issue Statutory Block", use_container_width=True, key=f"hitl_blk_{pid}"):
                st.session_state.overrides[pid] = VerificationStatus.HARD_BLOCK_SANCTIONED
                st.session_state.review_history.append({
                    "provider_id": pid,
                    "action": "HARD_BLOCK",
                    "note": "Statutory debarment or active revocation confirmed.",
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.error("Hard block enforced.")
                st.rerun()

        # Pre-drafted Provider Outreach Form
        if res.outreach_draft:
            st.markdown("##### ✉️ Automated Provider Clarification Dispatcher")
            edited_draft = st.text_area("Review or edit pre-drafted outreach before sending:", value=res.outreach_draft, height=180)
            if st.button("📤 Send Clarification Request via CertifyOS Webhook", key=f"send_mail_{pid}"):
                st.session_state.review_history.append({
                    "provider_id": pid,
                    "action": "OUTREACH_DISPATCHED",
                    "note": f"Clarification email dispatched via CertifyOS notification webhook.",
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success(f"Clarification notice dispatched to {intake['full_name']}! Ticket created in CertifyOS Operations Queue.")

        # Reviewer Action History
        if st.session_state.review_history:
            st.markdown("##### 📝 Session Audit Log")
            for h in reversed(st.session_state.review_history):
                if h["provider_id"] == pid:
                    st.caption(f"⏱️ **{h['time']} UTC** — `{h['action']}`: {h['note']}")

        # Raw JSON Inspector Expander
        with st.expander("🛠️ Inspect Raw Verification JSON Payload"):
            st.json(res.model_dump())


# TAB 2: LIVE INTAKE SANDBOX
with tab_sandbox:
    st.subheader("🧪 Live Intake Simulator & Custom Verification Engine")
    st.markdown("Test ProviderPass with customized provider intake payloads and primary source responses.")

    sample_intake = {
        "provider_id": "PRV-CUSTOM-99",
        "npi": "1849201847",
        "full_name": "Dr. Sarah Jenkins",
        "specialty": "Dermatology",
        "taxonomy_code": "207N00000X",
        "state_licenses": [{"state": "MA", "license_number": "MA-98421", "status": "ACTIVE", "expiration_date": "2027-05-15"}],
        "dea_number": "SJ4891023",
        "practice_address": "75 Francis St, Boston, MA 02115",
        "hospital_affiliations": ["Brigham and Women's Hospital"],
        "malpractice_claims_declared": 0,
        "submitted_date": "2026-11-02"
    }

    sample_sources = {
        "nppes": {"npi": "1849201847", "legal_name": "SARAH JENKINS", "other_names": [], "status": "ACTIVE"},
        "state_boards": [{"board": "Massachusetts Board of Registration in Medicine", "license_number": "MA-98421", "name_on_record": "SARAH JENKINS", "status": "ACTIVE", "disciplinary_actions": "NONE", "expiration_date": "2027-05-15"}],
        "dea": {"registration_number": "SJ4891023", "name": "SARAH JENKINS", "schedules": ["2", "3", "4", "5"], "status": "ACTIVE", "expiration_date": "2027-08-31"},
        "npdb": {"adverse_actions": [], "malpractice_payments": [], "sanctions": []},
        "oig_sam": {"leie_status": "CLEAR", "sam_exclusion": "NONE"},
        "directory_verification": {"address_type": "ACADEMIC_MEDICAL_CENTER", "usps_deliverable": True, "cms_directory_flag": "PASS"}
    }

    sb_col1, sb_col2 = st.columns(2)
    with sb_col1:
        custom_intake_str = st.text_area("Provider Intake JSON", value=json.dumps(sample_intake, indent=2), height=280)
    with sb_col2:
        custom_sources_str = st.text_area("Primary Sources JSON", value=json.dumps(sample_sources, indent=2), height=280)

    if st.button("🚀 Run Live PSV Verification", type="primary", use_container_width=True):
        try:
            c_intake = json.loads(custom_intake_str)
            c_sources = json.loads(custom_sources_str)
            
            with st.spinner("Analyzing against NCQA primary source rules..."):
                c_result = engine_instance.run_ai_verification(c_intake, c_sources)
            
            st.markdown("### 📊 Verification Outcome")
            st.markdown(f"**Status:** {get_badge_html(c_result.status)} &nbsp;|&nbsp; **Score:** `{c_result.cred_trust_score}/100` &nbsp;|&nbsp; **Engine:** `{c_result.model_used}`", unsafe_allow_html=True)
            st.info(c_result.executive_summary)
            
            if c_result.discrepancies:
                st.markdown("#### Detected Discrepancies")
                for d in c_result.discrepancies:
                    st.error(f"**[{d.severity.value}] {d.field_name}**: {d.description}")
            else:
                st.success("No primary source discrepancies detected. All NCQA standards met.")
                
            with st.expander("View Full Structured JSON Output"):
                st.json(c_result.model_dump())
        except Exception as err:
            st.error(f"Error parsing JSON or running verification: {err}")


# TAB 3: FORWARD DEPLOYED PM DISCOVERY & STRATEGY
with tab_fdpm:
    st.subheader("Forward Deployed PM Blueprint: Scaling CertifyOS ProviderPass")
    st.markdown("""
    This prototype models how a Forward Deployed Product Manager at CertifyOS bridges sales engineering, customer discovery, regulatory compliance, and rapid prototyping.
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        #### 1. Unmet Customer Need & Discovery
        - **Target Segment:** Rapidly expanding digital health platforms and national health plans onboarding 500+ clinicians per month.
        - **Pain Point:** Traditional credentialing relies on manual operations (Credentialing Verification Organizations) requiring **60-90 days per provider**. Clinicians cannot see patients or bill insurance during this window, causing **tens of thousands in delayed revenue per provider**.
        - **Discovery Finding:** 70% of intake exceptions are routine administrative variances (e.g. maiden vs. married surname on state licenses, imminent DEA renewals, or address formatting) that do not warrant a full committee freeze.
        """)
        
        st.markdown("""
        #### 2. Commercial Model & Pricing Strategy
        - **SaaS Platform Fee:** Base fee of $3,500/month for payer/health system portal access.
        - **Usage-Based Verification:** $35 per automated Primary Source Verification (PSV) package vs. the $280-$450 per provider charged by legacy outsourced CVOs.
        - **ROI Equation:** A 1,000-provider health system saves **$245,000 annually in CVO spend** while accelerating clinical time-to-bill by **42 days**.
        """)

    with col_b:
        st.markdown("""
        #### 3. AI Safety, Guardrails & Human-in-the-Loop (HITL)
        - **Deterministic Fallback Engine:** Healthcare credentialing cannot tolerate LLM hallucinations. ProviderPass uses strict deterministic primary source verification as the baseline grounding layer.
        - **NCQA / URAC Audit Readiness:** Every flag is mapped to an explicit regulatory standard (NCQA CR1, CR3, CR4; HHS OIG 42 CFR § 1001; CMS No Surprises Act).
        - **Zero Autonomous Hard Decisions:** The AI proposes confidence-scored recommendations and drafts provider clarification inquiries; human credentialing analysts retain 1-click binding signoff.
        """)

        st.markdown("""
        #### 4. Enterprise Scale & Roadmap
        - **Phase 1 (Pilot - Weeks 1-4):** Shadow-mode verification parallel to existing CVO operations across 100 providers.
        - **Phase 2 (Hardening - Weeks 5-8):** Webhook integration into payer intake APIs; enable 1-click provider outreach dispatch.
        - **Phase 3 (Production Scale - Weeks 9+):** Expand to multi-state CAQH automated sync and continuous monitoring against daily state license sanctions.
        """)
