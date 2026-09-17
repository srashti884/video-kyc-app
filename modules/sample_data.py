import os
import io
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_synthetic_portrait(name: str, seed_color: tuple, filename: str) -> str:
    """Generates a clean synthetic human-like avatar portrait for demo face matching."""
    filepath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(filepath):
        return filepath
    
    img = Image.new("RGB", (300, 350), color=seed_color)
    draw = ImageDraw.Draw(img)
    
    # Background
    draw.rectangle([(0, 0), (300, 350)], fill=seed_color)
    
    # Shoulders / Body
    draw.ellipse([(-20, 220), (320, 480)], fill=(40, 50, 75))
    
    # Neck
    draw.rectangle([(120, 180), (180, 240)], fill=(230, 190, 160))
    
    # Head / Face oval
    draw.ellipse([(85, 70), (215, 215)], fill=(240, 205, 175))
    
    # Hair
    draw.chord([(80, 50), (220, 160)], start=180, end=360, fill=(45, 30, 20))
    draw.ellipse([(85, 45), (215, 110)], fill=(45, 30, 20))
    
    # Eyes
    draw.ellipse([(110, 125), (135, 140)], fill=(255, 255, 255))
    draw.ellipse([(120, 128), (130, 138)], fill=(40, 25, 20)) # Pupil
    draw.ellipse([(165, 125), (190, 140)], fill=(255, 255, 255))
    draw.ellipse([(170, 128), (180, 138)], fill=(40, 25, 20)) # Pupil
    
    # Eyebrows
    draw.arc([(105, 115), (140, 130)], start=190, end=350, fill=(35, 25, 15), width=3)
    draw.arc([(160, 115), (195, 130)], start=190, end=350, fill=(35, 25, 15), width=3)
    
    # Nose
    draw.line([(150, 135), (146, 165), (155, 165)], fill=(200, 160, 130), width=2)
    
    # Mouth / Smile
    draw.arc([(125, 165), (175, 195)], start=10, end=170, fill=(180, 70, 70), width=3)
    
    # Label watermark
    draw.rectangle([(0, 310), (300, 350)], fill=(15, 23, 42))
    draw.text((20, 320), f"PHOTO ID: {name.upper()}", fill=(200, 220, 240))
    
    img.save(filepath, "JPEG", quality=95)
    return filepath


def create_synthetic_id_card(doc_type: str, persona: dict, portrait_path: str, filename: str) -> str:
    """Generates a realistic government/official ID card mockup with photo, barcodes, and text."""
    filepath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(filepath):
        return filepath
        
    width, height = 700, 440
    bg_color = (248, 250, 252)
    header_color = (15, 76, 129) if doc_type == "Passport" else (22, 101, 52) if doc_type == "Aadhaar Card" else (124, 45, 18)
    
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Border & card frame
    draw.rounded_rectangle([(10, 10), (width - 10, height - 10)], radius=18, fill=bg_color, outline=(203, 213, 225), width=3)
    
    # Header Banner
    draw.rounded_rectangle([(12, 12), (width - 12, 85)], radius=16, fill=header_color)
    draw.rectangle([(12, 50), (width - 12, 85)], fill=header_color)
    
    # Header Text
    header_titles = {
        "Passport": "REPUBLIC OFFICIAL TRAVEL DOCUMENT - PASSPORT",
        "Aadhaar Card": "GOVERNMENT OF INDIA - UNIQUE IDENTIFICATION AUTHORITY",
        "PAN Card": "INCOME TAX DEPARTMENT - PERMANENT ACCOUNT CARD",
        "Driver's License": "DEPARTMENT OF MOTOR VEHICLES - DRIVING LICENCE"
    }
    draw.text((30, 22), header_titles.get(doc_type, "OFFICIAL IDENTITY CARD"), fill=(255, 255, 255))
    draw.text((30, 48), "VERIFIED BIOMETRIC ENROLLMENT RECORD", fill=(186, 230, 253))
    
    # Embed Portrait
    if os.path.exists(portrait_path):
        portrait = Image.open(portrait_path).resize((160, 190))
        img.paste(portrait, (35, 110))
        draw.rectangle([(33, 108), (197, 302)], outline=header_color, width=2)
    
    # Hologram / Security Seal Mockup
    draw.ellipse([(120, 250), (185, 315)], fill=None, outline=(234, 179, 8), width=3)
    draw.text((130, 275), "SECURE", fill=(161, 98, 7))
    
    # Detail Fields
    x_offset = 220
    draw.text((x_offset, 110), f"FULL NAME:", fill=(100, 116, 139))
    draw.text((x_offset, 130), persona["name"].upper(), fill=(15, 23, 42))
    
    draw.text((x_offset, 165), f"DATE OF BIRTH:", fill=(100, 116, 139))
    draw.text((x_offset, 185), persona["dob"], fill=(15, 23, 42))
    
    draw.text((x_offset, 220), f"DOCUMENT ID NUMBER:", fill=(100, 116, 139))
    draw.text((x_offset, 240), persona["id_number"], fill=(2, 132, 199))
    
    draw.text((x_offset, 275), f"EXPIRATION DATE:", fill=(100, 116, 139))
    draw.text((x_offset, 295), persona.get("expiry_date", "2032-11-20"), fill=(15, 23, 42))

    # Machine Readable Zone (MRZ) / Barcode representation
    draw.rectangle([(25, 345), (width - 25, 415)], fill=(241, 245, 249), outline=(226, 232, 240), width=1)
    
    clean_id = persona["id_number"].replace(" ", "").replace("-", "")
    mrz_line_1 = f"P<IND{persona['name'].replace(' ', '<<').upper()}<<<<<<<<<<<<<<<<<<<<"[:44]
    mrz_line_2 = f"{clean_id}4IND8507128M3211204<<<<<<<<<<<<<<02"[:44]
    draw.text((40, 355), mrz_line_1, fill=(51, 65, 85))
    draw.text((40, 382), mrz_line_2, fill=(51, 65, 85))
    
    img.save(filepath, "JPEG", quality=95)
    return filepath


# Predefined personas
PERSONAS = {
    "approved": {
        "scenario_id": "approved",
        "label": "Vikram Patel — Standard Verification",
        "name": "Vikram Patel",
        "dob": "1990-08-14",
        "doc_type": "Passport",
        "id_number": "P8372619",
        "expiry_date": "2032-05-18",
        "address": "42 Marine Drive, Nariman Point, Mumbai 400021",
        "email": "vikram.patel@fintechmail.com",
        "phone": "+91 98201 54321",
        "nationality": "Indian",
        "expected_status": "KYC Verified",
        "portrait_color": (210, 225, 240),
        "live_similarity": 94.5,
        "liveness_pass": True,
        "notes": "Valid passport, matching details, verified biometric likeness, passed liveness challenge."
    },
    "manual_review": {
        "scenario_id": "manual_review",
        "label": "Sarah Jenkins — Name Discrepancy",
        "name": "Sarah Jenkins",
        "doc_name": "Sarah Ann Jenkins",  # slight variation
        "dob": "1994-03-22",
        "doc_type": "Driver's License",
        "id_number": "DL1420110012345",
        "expiry_date": "2026-11-30", # near expiry
        "address": "120 Silicon Alley, Tech District, Bengaluru 560100",
        "email": "sarah.j@startuphub.io",
        "phone": "+91 91234 56780",
        "nationality": "Indian",
        "expected_status": "Manual Review",
        "portrait_color": (235, 220, 245),
        "live_similarity": 76.2,
        "liveness_pass": True,
        "notes": "Middle name mismatch on license vs application form; license expires in 2 months. Requires officer signoff."
    },
    "failed": {
        "scenario_id": "failed",
        "label": "Alex Vance — Biometric Mismatch",
        "name": "Alex Vance",
        "doc_name": "Marcus Vance",
        "dob": "1988-12-05",
        "doc_type": "PAN Card",
        "id_number": "ABCDE1234F",
        "expiry_date": "2024-01-10", # expired
        "address": "99 Unknown Street, North Zone",
        "email": "alex.vance.test@tempmail.com",
        "phone": "+91 99999 00000",
        "nationality": "Indian",
        "expected_status": "Verification Failed",
        "portrait_color": (245, 225, 215),
        "live_similarity": 38.0,
        "liveness_pass": False,
        "notes": "High biometric mismatch against ID portrait, anti-spoofing liveness failed (static image detected), expired ID."
    }
}


def ensure_demo_assets():
    """Generates all synthetic portraits and ID card files for immediate zero-friction demo."""
    assets = {}
    
    # 1. Approved Persona
    p_app = PERSONAS["approved"]
    p_app_portrait = create_synthetic_portrait(p_app["name"], p_app["portrait_color"], "approved_portrait.jpg")
    p_app_id = create_synthetic_id_card(p_app["doc_type"], p_app, p_app_portrait, "approved_id_card.jpg")
    p_app_selfie = create_synthetic_portrait(p_app["name"], (215, 230, 245), "approved_live_selfie.jpg")
    
    # 2. Manual Review Persona
    p_man = PERSONAS["manual_review"]
    p_man_portrait = create_synthetic_portrait(p_man["name"], p_man["portrait_color"], "manual_portrait.jpg")
    p_man_id = create_synthetic_id_card(p_man["doc_type"], {**p_man, "name": p_man["doc_name"]}, p_man_portrait, "manual_id_card.jpg")
    p_man_selfie = create_synthetic_portrait(p_man["name"], (240, 225, 250), "manual_live_selfie.jpg")
    
    # 3. Failed Persona
    p_fail = PERSONAS["failed"]
    p_fail_portrait = create_synthetic_portrait("Marcus Vance", p_fail["portrait_color"], "failed_id_portrait.jpg")
    p_fail_id = create_synthetic_id_card(p_fail["doc_type"], {**p_fail, "name": p_fail["doc_name"]}, p_fail_portrait, "failed_id_card.jpg")
    p_fail_selfie = create_synthetic_portrait("Imposter", (220, 245, 230), "failed_live_selfie.jpg")
    
    assets["approved"] = {"portrait": p_app_portrait, "id_card": p_app_id, "selfie": p_app_selfie}
    assets["manual_review"] = {"portrait": p_man_portrait, "id_card": p_man_id, "selfie": p_man_selfie}
    assets["failed"] = {"portrait": p_fail_portrait, "id_card": p_fail_id, "selfie": p_fail_selfie}
    
    return assets
