# Identity Verification & Video KYC Portal

A lightweight, enterprise-styled **Video KYC (Know Your Customer) Application** built in Streamlit. It runs **100% locally on Windows without external paid APIs**, featuring biometric face matching, anti-spoofing liveness verification, structured document inspection, explainable multi-factor scoring, and downloadable audit reports.

---

## Quick Start

### 1. Launch the Application
Open a terminal in the project directory and run:
```powershell
streamlit run app.py
```
Or with explicit port:
```powershell
python -m streamlit run app.py --server.port 8501
```

Access the application in your browser at:
`http://localhost:8501`

---

## Test Scenarios (1-Click Presets)

The application includes **3 pre-configured scenarios and synthetic government ID cards** (Passport, Aadhaar, PAN, Driver's License) with realistic portraits and MRZ records:

| Scenario | Persona | Document | Biometric Match | Liveness Result | Final Decision | Purpose |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Approved** | Vikram Patel | Passport | **94.5%** | **Passed** | **KYC Verified** | Standard happy-path onboarding with instant verification. |
| **Review** | Sarah Jenkins | Driver's License | **76.2%** | **Passed** | **Manual Review** | Edge-case handling: minor name spelling variation & near-expiry ID. |
| **Failed** | Alex Vance | PAN Card | **38.0%** | **Failed (Spoof)** | **Verification Failed** | Fraud detection: face mismatch, expired ID, static photo spoofing. |

---

## 🔄 End-to-End Workflow Stages

### Stage 1: Onboarding & Consent
- Enterprise regulatory disclaimer and consent acknowledgment.
- Single-click session initiation.

### Stage 2: Customer Identity Profile
- Applicant details (Name, DOB, ID Type, Serial Number, Address, Email, Phone).
- Dynamic pattern format checker against official ID schemes (e.g. PAN `ABCDE1234F`, Aadhaar 12-digit, Passport).
- "Reset with Demo Scenario Data" button for zero typing during live demos.

### Stage 3: Document Verification & Smart OCR
- Supports **Passport**, **Aadhaar Card**, **PAN Card**, and **Driver's License**.
- Optical/MRZ information extraction and side-by-side cross-check with the application form.
- Automated document validity and expiration date warning engine.
- AI bounding box visualization pinpointing the detected ID photo region.

### Stage 4: Video KYC Face & Liveness
- **Dual Capture Modes**:
  - **Live Web Camera** (`st.camera_input`) for real-time webcam demonstration.
  - **Pre-Loaded Demo Live Capture / Upload Fallback** for guaranteed reliability under low-light or restricted camera permissions.
- Biometric likeness comparison between ID photo and live face with multi-channel similarity scoring.
- Active liveness challenge anti-spoofing engine (checks 3D depth variance, gaze orientation, micro-motions, and screen moiré patterns).

### Stage 5: Explainable Decision Engine & Audit Dossier
- **Multi-Pillar Weighted Score (100 pts max)**:
  1. Document Authenticity & Expiry (25 pts)
  2. Data Consistency / OCR Profile Match (25 pts)
  3. Facial Biometric Likeness (30 pts)
  4. Liveness & Anti-Spoofing (20 pts)
- **Status Classification**:
  - `KYC Verified` (Green, score ≥ 80%, zero critical flags)
  - `Manual Review Required` (Amber, score 65-79% or non-critical anomaly)
  - `Verification Failed` (Red, critical spoofing, expired ID, or major mismatch)
- **Compliance Recommended Action** (e.g. "Grant Tier-2 Account Access" vs "Trigger L2 Review").
- **Downloadable KYC Dossier**:
  - Download as a formal, printable **HTML Verification Certificate**.
  - Download as an **Audit Markdown Record**.
  - Interactive in-app certificate preview.

---

## 📂 Project Architecture

```
video-kyc-app/
├── app.py                      # Main Streamlit fintech application & stepper UI
├── test_kyc_flow.py            # Automated pipeline test validating all 3 scenarios
├── README.md                   # Setup guide and presentation instructions
├── assets/                     # Auto-generated synthetic portraits & ID cards
│   ├── approved_id_card.jpg
│   ├── approved_live_selfie.jpg
│   ├── manual_id_card.jpg
│   ├── manual_live_selfie.jpg
│   ├── failed_id_card.jpg
│   └── failed_live_selfie.jpg
└── modules/
    ├── __init__.py
    ├── sample_data.py          # Synthetic ID card synthesizer & persona definitions
    ├── kyc_state.py            # Streamlit session state and scenario switcher
    ├── document_processor.py   # ID format validation, expiration & OCR matching
    ├── face_engine.py          # Face detection, cropping, and biometric comparison
    ├── liveness_detector.py    # Multi-challenge liveness & anti-spoofing analysis
    ├── decision_engine.py      # Explainable 4-pillar weighted decision engine
    └── report_generator.py     # HTML certificate & Markdown dossier generator
```

---

## Automated Testing

Run the automated integration test to verify all engines:
```powershell
python test_kyc_flow.py
```
Output:
```
--- TESTING SCENARIO: APPROVED ---
Doc format valid: True, Expiry status: VALID, Match score: 100.0%
Face comparison score: 88.7%, Status: MATCH_CONFIRMED
Liveness score: 91.2%, Is Live: True
Final Decision:  KYC Verified (Total Score: 94.8)

--- TESTING SCENARIO: MANUAL_REVIEW ---
Doc format valid: True, Expiry status: EXPIRING_SOON, Match score: 94.0%
Face comparison score: 73.4%, Status: BORDERLINE_MATCH
Liveness score: 92.8%, Is Live: True
Final Decision:  Manual Review Required (Total Score: 86.1)

--- TESTING SCENARIO: FAILED ---
Doc format valid: True, Expiry status: EXPIRED, Match score: 83.6%
Face comparison score: 40.5%, Status: MISMATCH
Liveness score: 40.0%, Is Live: False
Final Decision:  Verification Failed (Total Score: 56.0)

ALL SCENARIO TESTS PASSED SUCCESSFULLY!
```
