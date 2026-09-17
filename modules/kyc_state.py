import streamlit as st
from modules.sample_data import PERSONAS, ensure_demo_assets

def init_session_state():
    """Initializes Streamlit session state keys with robust defaults."""
    if "step" not in st.session_state:
        st.session_state.step = 1

    if "scenario_id" not in st.session_state:
        st.session_state.scenario_id = "approved"

    # Preload sample assets
    if "assets" not in st.session_state:
        st.session_state.assets = ensure_demo_assets()

    # Customer Form Data
    if "customer_data" not in st.session_state:
        p = PERSONAS["approved"]
        st.session_state.customer_data = {
            "name": p["name"],
            "dob": p["dob"],
            "doc_type": p["doc_type"],
            "id_number": p["id_number"],
            "expiry_date": p["expiry_date"],
            "address": p["address"],
            "email": p["email"],
            "phone": p["phone"],
            "nationality": p["nationality"]
        }

    # Document state
    if "uploaded_doc_image" not in st.session_state:
        st.session_state.uploaded_doc_image = st.session_state.assets["approved"]["id_card"]

    if "doc_analysis" not in st.session_state:
        st.session_state.doc_analysis = None

    # Biometrics state
    if "uploaded_live_image" not in st.session_state:
        st.session_state.uploaded_live_image = st.session_state.assets["approved"]["selfie"]

    if "face_result" not in st.session_state:
        st.session_state.face_result = None

    if "liveness_result" not in st.session_state:
        st.session_state.liveness_result = None

    # Final Decision
    if "decision" not in st.session_state:
        st.session_state.decision = None


def switch_scenario(scenario_key: str):
    """Loads all data, synthetic documents, and photos for a given demo scenario."""
    if scenario_key not in PERSONAS:
        return
        
    p = PERSONAS[scenario_key]
    st.session_state.scenario_id = scenario_key
    st.session_state.customer_data = {
        "name": p["name"],
        "dob": p["dob"],
        "doc_type": p["doc_type"],
        "id_number": p["id_number"],
        "expiry_date": p["expiry_date"],
        "address": p["address"],
        "email": p["email"],
        "phone": p["phone"],
        "nationality": p["nationality"]
    }
    
    # Update linked assets
    assets = st.session_state.assets.get(scenario_key, {})
    st.session_state.uploaded_doc_image = assets.get("id_card")
    st.session_state.uploaded_live_image = assets.get("selfie")
    
    # Clear downstream results so presenter sees fresh calculation
    st.session_state.doc_analysis = None
    st.session_state.face_result = None
    st.session_state.liveness_result = None
    st.session_state.decision = None
