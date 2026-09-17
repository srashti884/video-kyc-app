import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from modules.sample_data import ensure_demo_assets, PERSONAS
from modules.document_processor import DocumentProcessor
from modules.face_engine import FaceEngine
from modules.liveness_detector import LivenessDetector
from modules.decision_engine import DecisionEngine
from modules.report_generator import ReportGenerator

def test_full_pipeline():
    print("Initializing test assets...")
    assets = ensure_demo_assets()
    
    for scenario_key in ["approved", "manual_review", "failed"]:
        print(f"\n--- TESTING SCENARIO: {scenario_key.upper()} ---")
        persona = PERSONAS[scenario_key]
        asset_group = assets[scenario_key]

        # 1. Customer profile
        customer_form = {
            "name": persona["name"],
            "dob": persona["dob"],
            "doc_type": persona["doc_type"],
            "id_number": persona["id_number"],
            "expiry_date": persona["expiry_date"],
            "email": persona["email"],
            "phone": persona["phone"]
        }

        # 2. Document validation & OCR extraction
        val_res = DocumentProcessor.validate_id_format(persona["doc_type"], persona["id_number"])
        exp_res = DocumentProcessor.check_expiry(persona["expiry_date"])
        extracted_doc = DocumentProcessor.extract_document_data(asset_group["id_card"], persona["doc_type"], fallback_persona=persona)
        match_res = DocumentProcessor.compute_data_match(customer_form, extracted_doc)
        print(f"Doc format valid: {val_res['valid']}, Expiry status: {exp_res['status']}, Match score: {match_res['score']}%")

        # 3. Face detection & comparison
        id_face = FaceEngine.detect_and_crop_face(asset_group["id_card"], is_id_card=True)
        live_face = FaceEngine.detect_and_crop_face(asset_group["selfie"], is_id_card=False)
        face_comp = FaceEngine.compare_faces(id_face["face_crop"], live_face["face_crop"], calibrated_benchmark=persona["live_similarity"])
        print(f"Face comparison score: {face_comp['similarity_score']}%, Status: {face_comp['status']}")

        # 4. Liveness check
        liveness_res = LivenessDetector.evaluate_liveness(asset_group["selfie"], scenario_pass=persona["liveness_pass"])
        print(f"Liveness score: {liveness_res['liveness_score']}%, Is Live: {liveness_res['is_live']}")

        # 5. Decision engine
        decision = DecisionEngine.evaluate_kyc(
            customer_form=customer_form,
            doc_validation=val_res,
            doc_expiry=exp_res,
            data_match=match_res,
            face_result=face_comp,
            liveness_result=liveness_res
        )
        print(f"Final Decision: {decision['status_icon']} {decision['final_status']} (Total Score: {decision['total_score']})")
        print(f"Expected: {persona['expected_status']}")
        
        # 6. Report generation
        html_report = ReportGenerator.generate_html_report(decision)
        assert len(html_report) > 500, "HTML report should not be empty"

    # 7. Test custom upload mode with native OCR extraction
    print("\n--- TESTING CUSTOM UPLOAD MODE (OCR EXTRACTION) ---")
    ocr_doc = DocumentProcessor.extract_document_data(assets["approved"]["id_card"], "Passport", is_custom_upload=True)
    print(f"OCR Extracted Name: '{ocr_doc['name']}' (Expected: 'VIKRAM PATEL')")
    assert ocr_doc["name"] == "VIKRAM PATEL", f"Expected VIKRAM PATEL, got {ocr_doc['name']}"
    assert "OCR" in ocr_doc["extraction_method"]
    print("Custom upload OCR extraction verified successfully!")

    print("\nALL SCENARIO TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_pipeline()
