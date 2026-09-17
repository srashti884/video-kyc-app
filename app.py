import streamlit as st
import os
import io
from PIL import Image

# Import KYC backend modules
from modules.sample_data import PERSONAS, ensure_demo_assets
from modules.kyc_state import init_session_state, switch_scenario
from modules.document_processor import DocumentProcessor
from modules.face_engine import FaceEngine
from modules.liveness_detector import LivenessDetector
from modules.decision_engine import DecisionEngine
from modules.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="Identity Verification Portal - Video KYC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimal Light Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Background and global light theme */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Distinct sidebar with subtle light-gray background and border */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #cbd5e1 !important;
    }

    /* Form container */
    div[data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }

    /* Clearly visible subtle borders on ALL input fields, dropdowns, and textareas before hover */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }

    /* Hover and focus feedback */
    div[data-baseweb="input"]:hover,
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="textarea"]:hover {
        border-color: #94a3b8 !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within > div,
    div[data-baseweb="textarea"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
    }

    /* File uploader & camera input boxes */
    div[data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border: 1px dashed #94a3b8 !important;
        border-radius: 6px !important;
        padding: 16px !important;
    }

    div[data-testid="stCameraInput"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }

    /* Clean light container cards with visible light-gray border */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #475569;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 20px;
        font-weight: 600;
        color: #0f172a;
    }

    .metric-desc {
        font-size: 12px;
        color: #64748b;
        margin-top: 4px;
    }

    /* Professional Button Styling */
    div.stButton > button {
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease-in-out !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        border-color: #1d4ed8 !important;
        color: #ffffff !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        border-color: #1e40af !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }

    /* Clean Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .status-badge-verified {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }

    .status-badge-review {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .status-badge-failed {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }

    /* Stepper Header */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        padding: 12px 20px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }

    .step-item {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }

    .step-active {
        color: #2563eb;
        font-weight: 600;
    }

    .step-done {
        color: #334155;
    }

    .step-divider {
        color: #cbd5e1;
        font-size: 12px;
    }

    /* Decision Banner */
    .decision-banner {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #2563eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* Subtle Code / Mono tags */
    .code-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        background-color: #f1f5f9;
        color: #1e293b;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
init_session_state()

# ----------------- SIDEBAR: NAVIGATION & TEST PRESETS -----------------
with st.sidebar:
    st.markdown("### Video KYC Portal")
    st.caption("Identity Verification & Compliance Engine")
    st.divider()

    st.markdown("##### Test Scenarios")
    st.caption("Select a scenario to populate test records and documents:")

    if st.button("Approved: Vikram Patel", use_container_width=True, help="Passport, 94.5% biometric likeness, passed liveness"):
        switch_scenario("approved")
        st.rerun()

    if st.button("Manual Review: Sarah Jenkins", use_container_width=True, help="Driver's License, minor name discrepancy, near expiry"):
        switch_scenario("manual_review")
        st.rerun()

    if st.button("Verification Failed: Alex Vance", use_container_width=True, help="PAN Card, biometric mismatch, expired document"):
        switch_scenario("failed")
        st.rerun()

    st.divider()
    active_p = PERSONAS[st.session_state.scenario_id]
    st.markdown(f"**Active Record**: `{active_p['name']}`")
    st.markdown(f"**Document Type**: `{active_p['doc_type']}`")
    st.markdown(f"**Target Outcome**: `{active_p['expected_status']}`")
    st.caption(f"Context: {active_p['notes']}")

    st.divider()
    st.markdown("##### System Modules")
    st.caption("Face Detection: OpenCV Local Engine")
    st.caption("Anti-Spoofing: Challenge-Response")
    st.caption("OCR Engine: Structured Parser & MRZ")
    st.caption("Scoring Model: Weighted Multi-Factor")

    st.divider()
    if st.button("Reset Session", use_container_width=True):
        st.session_state.step = 1
        switch_scenario("approved")
        st.rerun()

# ----------------- MINIMAL STEPPER BAR -----------------
steps = [
    (1, "1. Overview"),
    (2, "2. Applicant Profile"),
    (3, "3. Document Verification"),
    (4, "4. Biometrics & Liveness"),
    (5, "5. Decision Summary")
]

current_step = st.session_state.step
stepper_html = "<div class='stepper-container'>"
for i, (num, title) in enumerate(steps):
    if num < current_step:
        stepper_html += f"<span class='step-item step-done'>[OK] {title}</span>"
    elif num == current_step:
        stepper_html += f"<span class='step-item step-active'><b>{title}</b></span>"
    else:
        stepper_html += f"<span class='step-item'>{title}</span>"
    if i < len(steps) - 1:
        stepper_html += "<span class='step-divider'>&nbsp;&nbsp;→&nbsp;&nbsp;</span>"
stepper_html += "</div>"
st.markdown(stepper_html, unsafe_allow_html=True)


# ==============================================================================
# STEP 1: ONBOARDING & CONSENT
# ==============================================================================
if st.session_state.step == 1:
    st.markdown("## Customer Identity Verification")
    st.caption("Complete customer identification and verification in accordance with standard digital onboarding guidelines.")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Verification Requirements</div>
            <ul style="color: #334155; font-size: 14px; line-height: 1.8; margin-top: 8px; padding-left: 20px;">
                <li>Government-issued photo identification (Passport, Aadhaar Card, PAN Card, or Driver's License)</li>
                <li>Camera access or clear front-facing portrait photograph</li>
                <li>Active liveness confirmation to verify physical presence</li>
                <li>All verification processing is performed locally on this system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        consent = st.checkbox(
            "I confirm that the applicant consents to the collection, processing, and biometric evaluation of their identification document and live image for verification purposes.",
            value=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Begin Verification", type="primary", use_container_width=True, disabled=not consent):
            st.session_state.step = 2
            st.rerun()

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Compliance & Security Standards</div>
            <p style="font-size: 13px; color: #475569; margin-top: 6px;">
                Verification decisions are generated using explainable rule-based scoring and anti-spoofing checks.
            </p>
            <hr style="border-color: #e2e8f0; margin: 12px 0;">
            <div style="font-size: 12px; color: #334155; line-height: 1.8;">
                <div>• In-memory biometric feature extraction</div>
                <div>• Format and expiration validation</div>
                <div>• Tamper-evident audit report generation</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# STEP 2: CUSTOMER DETAILS FORM
# ==============================================================================
elif st.session_state.step == 2:
    st.markdown("## Applicant Profile")
    st.caption("Enter or review the applicant's official registration details.")

    col_btn_fill, _ = st.columns([1, 4])
    with col_btn_fill:
        if st.button("Load Sample Profile"):
            switch_scenario(st.session_state.scenario_id)
            st.rerun()

    cust = st.session_state.customer_data

    with st.form("customer_details_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Legal Name", value=cust["name"], help="Must match the name on the ID document")
            dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=cust["dob"])
            doc_type = st.selectbox(
                "Document Type",
                options=["Passport", "Aadhaar Card", "PAN Card", "Driver's License"],
                index=["Passport", "Aadhaar Card", "PAN Card", "Driver's License"].index(cust["doc_type"]) if cust["doc_type"] in ["Passport", "Aadhaar Card", "PAN Card", "Driver's License"] else 0
            )
            id_number = st.text_input("Document ID Number", value=cust["id_number"])

        with col2:
            expiry_date = st.text_input("Document Expiry Date (YYYY-MM-DD)", value=cust["expiry_date"])
            email = st.text_input("Email Address", value=cust["email"])
            phone = st.text_input("Phone Number", value=cust["phone"])
            address = st.text_area("Residential Address", value=cust["address"], height=105)

        val_check = DocumentProcessor.validate_id_format(doc_type, id_number)
        if val_check["valid"]:
            st.info(f"Format Check: {val_check['message']}")
        else:
            st.warning(f"Format Warning: {val_check['message']}")

        col_back, col_next = st.columns([1, 4])
        with col_back:
            back_btn = st.form_submit_button("Back")
        with col_next:
            submit_btn = st.form_submit_button("Continue to Document Verification", type="primary", use_container_width=True)

        if back_btn:
            st.session_state.step = 1
            st.rerun()

        if submit_btn:
            st.session_state.customer_data = {
                "name": full_name,
                "dob": dob,
                "doc_type": doc_type,
                "id_number": id_number,
                "expiry_date": expiry_date,
                "email": email,
                "phone": phone,
                "address": address,
                "nationality": cust.get("nationality", "Indian")
            }
            st.session_state.step = 3
            st.rerun()


# ==============================================================================
# STEP 3: DOCUMENT UPLOAD & OCR EXTRACTION
# ==============================================================================
elif st.session_state.step == 3:
    st.markdown("## Document Verification & Extraction")
    st.caption("Review the uploaded identification document and verify extracted fields.")

    cust = st.session_state.customer_data
    persona = PERSONAS.get(st.session_state.scenario_id, PERSONAS["approved"])

    col_upload_opts, col_preview = st.columns([1, 1])

    with col_upload_opts:
        doc_source = st.radio(
            "Document Source",
            options=["Bundled Test Document", "Upload Image File"],
            horizontal=True
        )

        current_doc_path = st.session_state.assets.get(st.session_state.scenario_id, {}).get("id_card")

        if doc_source == "Upload Image File":
            st.session_state.is_custom_doc = True
            uploaded_file = st.file_uploader("Upload Document (JPG/PNG)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                doc_image = Image.open(uploaded_file)
                st.session_state.uploaded_doc_image = uploaded_file
            else:
                doc_image = None
                st.session_state.doc_analysis = None
                st.session_state.doc_face_crop = None
        else:
            st.session_state.is_custom_doc = False
            doc_image = Image.open(current_doc_path)
            st.caption(f"Loaded: Standard test record for {cust['doc_type']}")

    if doc_image is None:
        with col_upload_opts:
            st.info("👆 Please select and upload an identity document image above to extract records via OCR.")
        with col_preview:
            st.markdown("<div class='metric-label'>Document Preview</div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 48px 20px; color: #64748b;">
                <div style="font-size: 38px; margin-bottom: 10px;">📄</div>
                <div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px;">No Document Uploaded Yet</div>
                <div style="font-size: 13px; color: #64748b; line-height: 1.6; max-width: 340px; margin: 0 auto;">
                    Upload a supported identity document (Passport, Aadhaar Card, PAN Card, or Driver's License) to perform automatic OCR extraction and face localization.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 4])
        with col_nav1:
            if st.button("Back"):
                st.session_state.step = 2
                st.rerun()
        with col_nav2:
            st.button("Continue to Biometric Check", type="primary", use_container_width=True, disabled=True, help="Please upload an ID document to proceed")
    else:
        # Process Face on Document Card
        doc_face_info = FaceEngine.detect_and_crop_face(doc_image, is_id_card=True)
        st.session_state.doc_face_crop = doc_face_info["face_crop"]

        # Run Document Validation
        is_custom = (doc_source == "Upload Image File")
        extracted_data = DocumentProcessor.extract_document_data(
            doc_image,
            cust["doc_type"],
            fallback_persona=persona if not is_custom else None,
            is_custom_upload=is_custom
        )

        val_id = extracted_data["id_number"] if extracted_data.get("id_number") and extracted_data.get("id_number") not in ["Not Detected", ""] else cust["id_number"]
        val_exp = extracted_data["expiry_date"] if extracted_data.get("expiry_date") and extracted_data.get("expiry_date") not in ["Not Detected", ""] else cust["expiry_date"]

        val_res = DocumentProcessor.validate_id_format(cust["doc_type"], val_id)
        exp_res = DocumentProcessor.check_expiry(val_exp)
        match_res = DocumentProcessor.compute_data_match(cust, extracted_data)

        st.session_state.doc_analysis = {
            "validation": val_res,
            "expiry": exp_res,
            "extracted": extracted_data,
            "match": match_res
        }

        # Show detected document face crop in left column
        with col_upload_opts:
            st.markdown("<div class='metric-label' style='margin-top: 14px;'>Extracted ID Portrait</div>", unsafe_allow_html=True)
            col_crop, col_crop_info = st.columns([1, 2])
            with col_crop:
                st.image(doc_face_info["face_crop"], width=120)
            with col_crop_info:
                st.caption(f"Portrait Detection: Confirmed")
                st.caption(f"Confidence: {doc_face_info['confidence']:.1f}%")
                st.caption(f"Engine: {extracted_data.get('extraction_method', 'Optical Parser')}")

        with col_preview:
            st.markdown("<div class='metric-label'>Document Preview & Detection Frame</div>", unsafe_allow_html=True)
            st.image(doc_face_info["annotated_image"], use_container_width=True)

        st.divider()
        st.markdown("##### Validation Metrics")

        col_ocr1, col_ocr2, col_ocr3 = st.columns(3)
        with col_ocr1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Document Format</div>
                <div class="metric-value" style="font-size: 16px;">
                    {'Valid Format' if val_res['valid'] else 'Format Discrepancy'}
                </div>
                <div class="metric-desc">{val_res['message']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_ocr2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Validity & Expiry</div>
                <div class="metric-value" style="font-size: 16px;">
                    {exp_res['status']}
                </div>
                <div class="metric-desc">{exp_res['message']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_ocr3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Field Match Rate</div>
                <div class="metric-value" style="font-size: 16px;">
                    {match_res['score']}% Match
                </div>
                <div class="metric-desc">Name: {match_res['name_match_ratio']}% | ID Serial: {'Match' if match_res['id_match'] else 'Mismatch'}</div>
            </div>
            """, unsafe_allow_html=True)

        # Detailed side-by-side comparison
        st.markdown("##### Extracted Document Fields vs Application")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"""
            <div class="metric-card" style="padding: 14px 16px;">
                <div class="metric-label" style="margin-bottom: 8px;">Application Profile Details</div>
                <div style="font-size: 13px; color: #1e293b; line-height: 1.9;">
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Full Name:</span> <b>{cust['name']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">ID Number:</span> <b>{cust['id_number']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Date of Birth:</span> <b>{cust['dob']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Expiry Date:</span> <b>{cust['expiry_date']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""
            <div class="metric-card" style="padding: 14px 16px;">
                <div class="metric-label" style="margin-bottom: 8px;">Extracted Document Records</div>
                <div style="font-size: 13px; color: #1e293b; line-height: 1.9;">
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Full Name:</span> <b>{extracted_data['name']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">ID Number:</span> <b>{extracted_data['id_number']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Date of Birth:</span> <b>{extracted_data['dob']}</b></div>
                    <div><span style="color: #64748b; display: inline-block; width: 105px;">Expiry Date:</span> <b>{extracted_data['expiry_date']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if match_res["flags"]:
            for flag in match_res["flags"]:
                st.warning(flag)

        st.markdown("<br>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 4])
        with col_nav1:
            if st.button("Back"):
                st.session_state.step = 2
                st.rerun()
        with col_nav2:
            if st.button("Continue to Biometric Check", type="primary", use_container_width=True):
                st.session_state.step = 4
                st.rerun()


# ==============================================================================
# STEP 4: VIDEO FACE & LIVENESS VERIFICATION
# ==============================================================================
elif st.session_state.step == 4:
    st.markdown("## Biometric & Liveness Verification")
    st.caption("Compare live biometric capture against document portrait and perform liveness verification.")

    persona = PERSONAS.get(st.session_state.scenario_id, PERSONAS["approved"])
    assets = st.session_state.assets.get(st.session_state.scenario_id, {})

    col_cam, col_comp = st.columns([1, 1])

    with col_cam:
        capture_mode = st.radio(
            "Biometric Input",
            options=["Live Web Camera (st.camera_input)", "Bundled Test Selfie", "Upload Photo File"],
            horizontal=True
        )

        live_image = None
        if capture_mode == "Live Web Camera (st.camera_input)":
            cam_picture = st.camera_input("Center face in front of the camera")
            if cam_picture is not None:
                live_image = Image.open(cam_picture)
            else:
                st.caption("Waiting for camera capture. Select 'Bundled Test Selfie' to use sample data.")
                live_image = Image.open(assets["selfie"])
        elif capture_mode == "Upload Photo File":
            up_selfie = st.file_uploader("Upload Portrait Photo", type=["jpg", "png", "jpeg"])
            if up_selfie is not None:
                live_image = Image.open(up_selfie)
            else:
                live_image = Image.open(assets["selfie"])
        else:
            live_image = Image.open(assets["selfie"])
            st.caption(f"Using test portrait for {persona['name']}")

        # Detect face in live capture
        live_face_info = FaceEngine.detect_and_crop_face(live_image, is_id_card=False)
        st.session_state.live_face_crop = live_face_info["face_crop"]

        # Run Biometric Comparison
        id_face = st.session_state.get("doc_face_crop")
        if id_face is None:
            doc_img = Image.open(assets["id_card"])
            id_face_info = FaceEngine.detect_and_crop_face(doc_img, is_id_card=True)
            id_face = id_face_info["face_crop"]
            st.session_state.doc_face_crop = id_face

        is_custom_mode = st.session_state.get("is_custom_doc", False) or (capture_mode != "Bundled Test Selfie")
        benchmark = None if is_custom_mode else persona.get("live_similarity")

        face_comp = FaceEngine.compare_faces(
            id_face,
            live_face_info["face_crop"],
            calibrated_benchmark=benchmark
        )
        st.session_state.face_result = face_comp

        # Run Liveness Engine
        liveness_res = LivenessDetector.evaluate_liveness(
            live_image,
            scenario_pass=persona.get("liveness_pass", True)
        )
        st.session_state.liveness_result = liveness_res

    with col_comp:
        st.markdown("<div class='metric-label'>Biometric Comparison</div>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.image(id_face, caption="Document Portrait", width=130)
        with col_f2:
            st.image(live_face_info["face_crop"], caption="Live Capture", width=130)

        border_col = "#059669" if face_comp["status"] == "MATCH_CONFIRMED" else ("#d97706" if face_comp["status"] == "BORDERLINE_MATCH" else "#dc2626")
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid {border_col}; margin-top: 10px;">
            <div class="metric-label">Facial Similarity Score</div>
            <div class="metric-value">{face_comp['similarity_score']}%</div>
            <div class="metric-desc">{face_comp['verdict']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("##### Liveness & Anti-Spoofing Assessment")

    col_live1, col_live2 = st.columns([1, 1])

    with col_live1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Liveness Status</div>
            <div class="metric-value" style="font-size: 18px;">
                {liveness_res['badge']}
            </div>
            <div class="metric-desc">Confidence Score: {liveness_res['liveness_score']}% (Minimum Threshold: 75.0%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col_live2:
        st.markdown("""
        <div class="metric-card" style="padding: 14px 16px;">
            <div class="metric-label" style="margin-bottom: 8px;">Verification Item Checklist</div>
        """, unsafe_allow_html=True)
        for chk in liveness_res["checks"]:
            mark = "[Pass]" if chk["passed"] else "[Fail]"
            st.text(f"{mark} {chk['name']}: {chk['detail']}")
        st.markdown("</div>", unsafe_allow_html=True)

        if liveness_res["flags"]:
            for flg in liveness_res["flags"]:
                st.error(flg)

    st.markdown("<br>", unsafe_allow_html=True)
    col_nav1, col_nav2 = st.columns([1, 4])
    with col_nav1:
        if st.button("Back"):
            st.session_state.step = 3
            st.rerun()
    with col_nav2:
        if st.button("Generate Decision Summary", type="primary", use_container_width=True):
            cust = st.session_state.customer_data
            doc_an = st.session_state.doc_analysis
            decision = DecisionEngine.evaluate_kyc(
                customer_form=cust,
                doc_validation=doc_an["validation"],
                doc_expiry=doc_an["expiry"],
                data_match=doc_an["match"],
                face_result=st.session_state.face_result,
                liveness_result=st.session_state.liveness_result
            )
            st.session_state.decision = decision
            st.session_state.step = 5
            st.rerun()


# ==============================================================================
# STEP 5: FINAL KYC DECISION & SUMMARY REPORT
# ==============================================================================
elif st.session_state.step == 5:
    decision = st.session_state.get("decision")
    if decision is None:
        st.warning("No decision data available. Returning to Step 4.")
        st.session_state.step = 4
        st.rerun()

    status = decision["final_status"]
    badge_color = decision["badge_color"]

    st.markdown("## Verification Decision")

    # Clean Light Decision Banner
    st.markdown(f"""
    <div class="decision-banner" style="border-left-color: {badge_color};">
        <div class="metric-label">Verification Result</div>
        <div style="font-size: 26px; font-weight: 700; color: #0f172a; margin: 4px 0;">
            {decision['final_status']}
        </div>
        <p style="font-size: 14px; color: #475569; margin: 6px 0 12px 0;">
            {decision['summary_statement']}
        </p>
        <div style="font-size: 12px; color: #64748b;">
            Reference ID: <span class="code-tag">{decision['reference_id']}</span> &nbsp;|&nbsp; 
            Total Score: <b>{decision['total_score']} / 100</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Pillars Score Breakdown Grid
    st.markdown("##### Assessment Breakdown")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    for col, p in zip([col_p1, col_p2, col_p3, col_p4], decision["pillars"]):
        p_color = "#059669" if p["status"] == "PASS" else ("#d97706" if p["status"] in ["WARN", "REVIEW"] else "#dc2626")
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 2px solid {p_color}; min-height: 150px;">
                <div class="metric-label">{p['pillar']}</div>
                <div style="font-size: 22px; font-weight: 600; color: #0f172a; margin: 4px 0;">
                    {p['score']} <span style="font-size: 13px; color: #64748b;">/ {p['max_score']}</span>
                </div>
                <div style="font-size: 11px; color: {p_color}; text-transform: uppercase; font-weight: 600;">
                    Weight: {p['weight']} &nbsp;|&nbsp; Status: {p['status']}
                </div>
                <div class="metric-desc" style="font-size: 12px; line-height: 1.4; color: #64748b;">
                    {p['details']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Risk Flags or Positive Indicators
    if decision["risk_flags"]:
        st.markdown("##### Flagged Verification Items")
        for flag in decision["risk_flags"]:
            st.warning(flag)
    else:
        st.success("All automated validation checks passed successfully with zero risk flags.")

    # Recommended Action Box
    st.markdown(f"""
    <div class="metric-card" style="margin: 16px 0;">
        <div class="metric-label">Recommended Action</div>
        <div style="font-size: 14px; color: #0f172a; margin-top: 2px;">{decision['recommended_action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Downloadable Reports
    st.markdown("##### Reports & Records")
    col_d1, col_d2, col_d3 = st.columns(3)

    html_dossier = ReportGenerator.generate_html_report(decision)
    md_summary = ReportGenerator.generate_markdown_summary(decision)

    with col_d1:
        st.download_button(
            label="Download HTML Report",
            data=html_dossier,
            file_name=f"KYC_Report_{decision['reference_id']}.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )

    with col_d2:
        st.download_button(
            label="Download Markdown Summary",
            data=md_summary,
            file_name=f"KYC_Summary_{decision['reference_id']}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_d3:
        if st.button("Start New Session", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    # Expandable Dossier Preview
    with st.expander("View Verification Report Preview"):
        st.components.v1.html(html_dossier, height=600, scrolling=True)
