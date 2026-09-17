import uuid
from datetime import datetime

class DecisionEngine:
    """
    Explainable, transparent, multi-factor KYC Decision Engine.
    Combines document integrity, data consistency, biometric likeness, and liveness.
    """

    @staticmethod
    def evaluate_kyc(
        customer_form: dict,
        doc_validation: dict,
        doc_expiry: dict,
        data_match: dict,
        face_result: dict,
        liveness_result: dict
    ) -> dict:
        reference_id = f"KYC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Document Score (25 pts max)
        doc_score = 0.0
        doc_flags = []
        if doc_validation.get("valid", False):
            doc_score += 15.0
        else:
            doc_flags.append(f"Document format invalid: {doc_validation.get('message')}")

        if not doc_expiry.get("is_expired", False):
            if doc_expiry.get("status") == "EXPIRING_SOON":
                doc_score += 7.0
                doc_flags.append(f"Document expiring within 90 days: {doc_expiry.get('message')}")
            else:
                doc_score += 10.0
        else:
            doc_score += 0.0
            doc_flags.append(f"Critical Document Expired: {doc_expiry.get('message')}")

        # 2. Data Consistency Score (25 pts max)
        data_ratio = data_match.get("score", 0.0)
        data_score = (data_ratio / 100.0) * 25.0

        # 3. Biometric Match Score (30 pts max)
        face_sim = face_result.get("similarity_score", 0.0)
        face_score = (face_sim / 100.0) * 30.0

        # 4. Liveness Score (20 pts max)
        live_sim = liveness_result.get("liveness_score", 0.0)
        live_score = (live_sim / 100.0) * 20.0

        # Overall Weighted Score (0 to 100)
        total_score = round(doc_score + data_score + face_score + live_score, 1)

        # Evaluate Hard-Stop Failure Conditions
        hard_fails = []
        if doc_expiry.get("is_expired", False):
            hard_fails.append("Document is expired and cannot be accepted for KYC enrollment.")
        if not liveness_result.get("is_live", False):
            hard_fails.append("Liveness anti-spoofing check failed (potential screen/paper presentation attack).")
        if face_sim < 60.0:
            hard_fails.append(f"Biometric similarity ({face_sim}%) is below the minimum security threshold (60.0%).")
        if data_match.get("status") == "FAIL":
            hard_fails.append("Major mismatch between customer application and extracted document records.")

        # Evaluate Manual Review Conditions
        review_triggers = []
        if 65.0 <= face_sim < 80.0:
            review_triggers.append(f"Moderate biometric similarity ({face_sim}%) requires human officer second-look.")
        if doc_expiry.get("status") == "EXPIRING_SOON":
            review_triggers.append("Document expiring soon; request customer reaffirmation or renewal notice.")
        if data_match.get("status") == "REVIEW":
            review_triggers.append("Minor name variation or initial detected; verification officer override required.")
        if 70.0 <= total_score < 82.0 and not hard_fails:
            review_triggers.append(f"Aggregate confidence score ({total_score}%) falls within secondary review bracket.")

        # Determine Final Status
        if hard_fails:
            final_status = "Verification Failed"
            badge_color = "#ef4444" # Red
            status_icon = ""
            summary_statement = "The applicant did not meet mandatory identity or document requirements. Verification was unsuccessful."
            recommended_action = "Reject application and log the risk flag. The applicant may re-attempt with valid, unexpired original documents."
        elif review_triggers or total_score < 82.0:
            final_status = "Manual Review Required"
            badge_color = "#f59e0b" # Amber
            status_icon = ""
            summary_statement = "Non-critical discrepancies detected. Routing application to a compliance officer for review."
            recommended_action = "Queue for secondary review. Verify name discrepancies against secondary records before approval."
        else:
            final_status = "KYC Verified"
            badge_color = "#10b981" # Green
            status_icon = ""
            summary_statement = "Identity documents, facial biometric likeness, and liveness checks were successfully verified."
            recommended_action = "Approve application. Proceed with standard customer onboarding."

        # Structured Explainability Audit Breakdown
        pillars = [
            {
                "pillar": "Document Authenticity & Integrity",
                "score": round(doc_score, 1),
                "max_score": 25.0,
                "weight": "25%",
                "status": "PASS" if not doc_flags else ("WARN" if doc_expiry.get("status") == "EXPIRING_SOON" else "FAIL"),
                "details": f"Format: {doc_validation.get('message')}. Validity: {doc_expiry.get('message')}."
            },
            {
                "pillar": "Data Consistency & Profile Match",
                "score": round(data_score, 1),
                "max_score": 25.0,
                "weight": "25%",
                "status": data_match.get("status"),
                "details": f"Name Match: {data_match.get('name_match_ratio')}%. ID Match: {'Yes' if data_match.get('id_match') else 'No'}."
            },
            {
                "pillar": "Facial Biometric Verification",
                "score": round(face_score, 1),
                "max_score": 30.0,
                "weight": "30%",
                "status": "PASS" if face_sim >= 80 else ("WARN" if face_sim >= 65 else "FAIL"),
                "details": f"Similarity: {face_sim}%. {face_result.get('verdict')}"
            },
            {
                "pillar": "Anti-Spoofing & Liveness Check",
                "score": round(live_score, 1),
                "max_score": 20.0,
                "weight": "20%",
                "status": "PASS" if liveness_result.get("is_live") else "FAIL",
                "details": f"Confidence: {live_sim}%. {liveness_result.get('badge')}"
            }
        ]

        return {
            "reference_id": reference_id,
            "timestamp": timestamp,
            "final_status": final_status,
            "status_icon": status_icon,
            "badge_color": badge_color,
            "total_score": total_score,
            "max_total_score": 100.0,
            "summary_statement": summary_statement,
            "recommended_action": recommended_action,
            "pillars": pillars,
            "hard_fails": hard_fails,
            "review_triggers": review_triggers,
            "risk_flags": doc_flags + data_match.get("flags", []) + liveness_result.get("flags", []),
            "customer_summary": {
                "name": customer_form.get("name"),
                "id_type": customer_form.get("doc_type"),
                "id_number": customer_form.get("id_number"),
                "dob": customer_form.get("dob"),
                "email": customer_form.get("email"),
                "phone": customer_form.get("phone")
            }
        }
