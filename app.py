import os, json, re, base64, uuid, tempfile, glob
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image
import requests

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import cloudinary
    import cloudinary.uploader
except Exception:
    cloudinary = None

APP_TITLE = "High Style AI – Inventory Intake Task 3.1.1"

# -----------------------------
# State / Reset
# -----------------------------

def init_state():
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0
    if "form_version" not in st.session_state:
        st.session_state["form_version"] = 0
    if "retry_history" not in st.session_state:
        st.session_state["retry_history"] = []

def clear_entry_state():
    exact_keys = [
        "draft", "item_id", "photo_names", "dims_inputs", "dims_formatted",
        "input_notes", "photos_for_save", "last_saved", "original_ai_draft",
        "retry_history", "brain_profile", "brain_matches", "submitted_by", "submitted_date"
    ]
    prefixes = [
        "height_input_", "width_input_", "depth_input_", "diameter_input_",
        "body_height_input_", "seat_height_input_", "known_info_input_",
        "notes_input_", "target_price_input_", "item_id_review_",
        "title_review_", "description_review_", "suggested_price_review_",
        "approved_price_review_", "confidence_review_", "category_review_",
        "subcategory_review_", "style_review_", "period_review_", "country_review_",
        "maker_review_", "materials_review_", "dims_final_review_",
        "condition_notes_review_", "price_tag_review_", "seo_review_",
        "internal_review_notes_", "title_feedback_", "description_feedback_",
        "price_feedback_", "reference_feedback_", "changed_notes_"
    ]
    for k in list(st.session_state.keys()):
        if k in exact_keys or any(k.startswith(p) for p in prefixes):
            del st.session_state[k]
    st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1
    st.session_state["form_version"] = st.session_state.get("form_version", 0) + 1
    st.session_state["retry_history"] = []

# -----------------------------
# Services
# -----------------------------

def get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None

def get_allowed_users():
    """
    Optional Streamlit secret:
    EMPLOYEE_USERS = "Paul:admin_password:Admin,Employee Name:employee_password:Employee"
    If not supplied, the app falls back to simple shared passwords.
    """
    raw = get_secret("EMPLOYEE_USERS")
    users = {}
    if raw:
        for part in str(raw).split(","):
            bits = [b.strip() for b in part.split(":")]
            if len(bits) >= 2:
                name = bits[0]
                password = bits[1]
                role = bits[2] if len(bits) >= 3 else "Employee"
                users[name] = {"password": password, "role": role}
    return users

def login_gate():
    st.title("High Style AI")
    st.caption("Inventory Assistant")

    users = get_allowed_users()
    admin_password = get_secret("ADMIN_PASSWORD")
    employee_password = get_secret("EMPLOYEE_PASSWORD")

    with st.form("login_form"):
        if users:
            user_name = st.selectbox("User", list(users.keys()))
        else:
            user_name = st.text_input("Name", placeholder="Enter your name")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if users:
            expected = users.get(user_name, {}).get("password")
            if password == expected:
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = user_name
                st.session_state["current_role"] = users.get(user_name, {}).get("role", "Employee")
                st.rerun()
            else:
                st.error("Incorrect password.")
        else:
            if admin_password and password == admin_password:
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = user_name or "Paul"
                st.session_state["current_role"] = "Admin"
                st.rerun()
            elif employee_password and password == employee_password:
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = user_name or "Employee"
                st.session_state["current_role"] = "Employee"
                st.rerun()
            else:
                st.error("Incorrect password.")

    st.info("Ask Paul for access if you do not have a password.")
    st.stop()

def get_openai_client():
    key = get_secret("OPENAI_API_KEY")
    if not key or OpenAI is None:
        return None
    return OpenAI(api_key=key)

def configure_cloudinary():
    if cloudinary is None:
        return False, "Cloudinary package is not installed."
    cloud_name = get_secret("CLOUDINARY_CLOUD_NAME")
    api_key = get_secret("CLOUDINARY_API_KEY")
    api_secret = get_secret("CLOUDINARY_API_SECRET")
    if not cloud_name or not api_key or not api_secret:
        return False, "Missing Cloudinary environment variables."
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    return True, ""

def safe_open_image(raw):
    return Image.open(BytesIO(raw)).convert("RGB")

def image_to_data_url(uploaded_file):
    raw = uploaded_file.getvalue()
    try:
        img = safe_open_image(raw)
        img.thumbnail((1400, 1400))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        raw = buf.getvalue()
    except Exception:
        pass
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("utf-8")

def upload_to_cloudinary(uploaded_file, item_id):
    ok, msg = configure_cloudinary()
    if not ok:
        return "", msg
    raw = uploaded_file.getvalue()
    try:
        img = safe_open_image(raw)
        img.thumbnail((1600, 1600))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=88)
        raw = buf.getvalue()
    except Exception as e:
        return "", f"Could not read/convert image: {e}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    try:
        result = cloudinary.uploader.upload(
            tmp_path,
            folder="high_style_ai/intake",
            public_id=item_id,
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url", ""), ""
    except Exception as e:
        return "", str(e)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

# -----------------------------
# High Style Brain
# -----------------------------

def clean_cell(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

@st.cache_data(show_spinner=False)
def load_high_style_brain():
    paths = []
    for folder in ["data", "."]:
        if os.path.exists(folder):
            paths.extend(glob.glob(os.path.join(folder, "*.xlsx")))
    preferred = [
        p for p in paths
        if "v5" in os.path.basename(p).lower()
        and ("ai_ready" in os.path.basename(p).lower() or "verified" in os.path.basename(p).lower() or "verification" in os.path.basename(p).lower())
    ]
    files = preferred or paths
    if not files:
        return pd.DataFrame(), ""

    path = files[0]
    try:
        xls = pd.ExcelFile(path)
        sheet_priority = ["Master_Data_V5", "Master_Data", "Low_Confidence_Review"]
        sheet = next((s for s in sheet_priority if s in xls.sheet_names), xls.sheet_names[0])
        df = pd.read_excel(path, sheet_name=sheet, dtype=object).dropna(how="all")
    except Exception as e:
        st.warning(f"Could not load High Style Brain file: {e}")
        return pd.DataFrame(), ""

    needed = [
        "Item_Title", "Item_Description", "AI_Clean_Title", "AI_Clean_Description",
        "Designer_or_Maker", "Category", "Subcategory", "Inferred_Item_Type",
        "AI_Item_Type", "Style", "AI_Period_Opening", "Approx_Year_or_Period",
        "Decade", "Country_of_Origin", "Materials_Normalized", "AI_Materials_Clean",
        "Materials_Raw", "AI_Search_Keywords", "AI_Search_Text", "Comparable_Key",
        "Original_List_Price_USD", "Actual_Net_Sale_Price_USD",
        "AI_Reference_Quality", "AI_Reference_Score", "Verified_By_Paul"
    ]
    for c in needed:
        if c not in df.columns:
            df[c] = ""

    df["_brain_search"] = (
        df["Item_Title"].apply(clean_cell) + " | " +
        df["Item_Description"].apply(clean_cell) + " | " +
        df["AI_Clean_Title"].apply(clean_cell) + " | " +
        df["AI_Clean_Description"].apply(clean_cell) + " | " +
        df["Designer_or_Maker"].apply(clean_cell) + " | " +
        df["Category"].apply(clean_cell) + " | " +
        df["Subcategory"].apply(clean_cell) + " | " +
        df["Inferred_Item_Type"].apply(clean_cell) + " | " +
        df["AI_Item_Type"].apply(clean_cell) + " | " +
        df["Style"].apply(clean_cell) + " | " +
        df["AI_Period_Opening"].apply(clean_cell) + " | " +
        df["Approx_Year_or_Period"].apply(clean_cell) + " | " +
        df["Decade"].apply(clean_cell) + " | " +
        df["Materials_Normalized"].apply(clean_cell) + " | " +
        df["AI_Materials_Clean"].apply(clean_cell) + " | " +
        df["Materials_Raw"].apply(clean_cell) + " | " +
        df["AI_Search_Keywords"].apply(clean_cell) + " | " +
        df["AI_Search_Text"].apply(clean_cell) + " | " +
        df["Comparable_Key"].apply(clean_cell)
    ).str.lower()

    return df, os.path.basename(path)

STOPWORDS = set("""
the and with for from this that pair set one two three large small rare vintage antique circa style modern beautiful fine decorative possibly likely
piece pieces table chair chairs lighting lamp lamps chandelier sconces mirror mirrors cabinet high style deco
""".split())

def tokenize(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    return [w for w in text.split() if len(w) > 2 and w not in STOPWORDS]

def quick_image_profile(photos, dims, known_info, notes):
    client = get_openai_client()
    if client is None:
        return {}
    schema = {
        "item_type": "specific object type",
        "category": "Lighting/Tables/Seating/Case Pieces/Accessories/Art/Mirrors",
        "style_period": "Art Deco/Mid-Century Modern/Modernist/Postmodern/etc.",
        "materials": ["material 1", "material 2"],
        "possible_maker_or_designer": "Unknown if unclear",
        "visual_features": ["feature 1", "feature 2"],
        "reference_search_terms": ["term 1", "term 2", "term 3"],
        "summary": "short internal summary"
    }
    prompt = f"""
Analyze these item photos for High Style Deco.
Return ONLY valid JSON with this schema:
{json.dumps(schema, indent=2)}

Do not invent a confirmed maker. Use Unknown if unclear.

Dimensions:
{dims}

Known info:
{known_info or "None"}

Notes:
{notes or "None"}
"""
    content = [{"type": "text", "text": prompt}]
    for photo in photos[:4]:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(photo)}})
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": content}],
            temperature=0.1
        )
        return parse_json(resp.choices[0].message.content)
    except Exception:
        return {}

def find_brain_matches(df, profile, dims, known_info, notes, top_n=8):
    if df.empty:
        return []
    seed_parts = [dims or "", known_info or "", notes or ""]
    for k in ["item_type", "category", "style_period", "possible_maker_or_designer", "summary"]:
        v = profile.get(k, "")
        if isinstance(v, str):
            seed_parts.append(v)
    for k in ["materials", "visual_features", "reference_search_terms"]:
        v = profile.get(k, [])
        if isinstance(v, list):
            seed_parts.extend([str(x) for x in v])
    terms = tokenize(" ".join(seed_parts))
    if not terms:
        return []

    profile_item = str(profile.get("item_type", "")).lower()
    profile_cat = str(profile.get("category", "")).lower()
    profile_style = str(profile.get("style_period", "")).lower()
    profile_mats = [str(x).lower() for x in profile.get("materials", [])] if isinstance(profile.get("materials"), list) else []

    def row_score(row):
        txt = str(row.get("_brain_search", "")).lower()
        title = (clean_cell(row.get("AI_Clean_Title", "")) or clean_cell(row.get("Item_Title", ""))).lower()
        desc = (clean_cell(row.get("AI_Clean_Description", "")) or clean_cell(row.get("Item_Description", ""))).lower()
        item_type = (clean_cell(row.get("AI_Item_Type", "")) or clean_cell(row.get("Inferred_Item_Type", ""))).lower()
        cat = clean_cell(row.get("Category", "")).lower()
        subcat = clean_cell(row.get("Subcategory", "")).lower()
        style = (clean_cell(row.get("AI_Period_Opening", "")) or clean_cell(row.get("Style", ""))).lower()
        mats = (clean_cell(row.get("AI_Materials_Clean", "")) + " " + clean_cell(row.get("Materials_Normalized", "")) + " " + clean_cell(row.get("Materials_Raw", ""))).lower()
        verified = clean_cell(row.get("Verified_By_Paul", "")).lower()
        ref_quality = clean_cell(row.get("AI_Reference_Quality", "")).lower()

        s = 0
        for t in terms:
            if t in txt: s += 1
            if t in title: s += 5
            if t in desc: s += 1
            if t in item_type: s += 6
            if t in cat or t in subcat: s += 4
            if t in style: s += 5
            if t in mats: s += 5

        if profile_item and profile_item in item_type: s += 18
        if profile_cat and profile_cat in cat: s += 10
        if profile_style and profile_style in style: s += 12
        for m in profile_mats:
            if m and m in mats: s += 8
        if verified == "yes": s += 10
        if "strong" in ref_quality or "high" in ref_quality: s += 4
        if desc: s += 3
        return s

    working = df.copy()
    working["_match_score"] = working.apply(row_score, axis=1)
    working = working[working["_match_score"] > 0].sort_values("_match_score", ascending=False).head(top_n)

    matches = []
    for _, r in working.iterrows():
        title = clean_cell(r.get("AI_Clean_Title", "")) or clean_cell(r.get("Item_Title", ""))
        desc = clean_cell(r.get("AI_Clean_Description", "")) or clean_cell(r.get("Item_Description", ""))
        matches.append({
            "match_score": int(r.get("_match_score", 0)),
            "title": title[:250],
            "description": desc[:1200],
            "category": clean_cell(r.get("Category", "")),
            "subcategory": clean_cell(r.get("Subcategory", "")),
            "item_type": clean_cell(r.get("AI_Item_Type", "")) or clean_cell(r.get("Inferred_Item_Type", "")),
            "style": clean_cell(r.get("AI_Period_Opening", "")) or clean_cell(r.get("Style", "")),
            "materials": clean_cell(r.get("AI_Materials_Clean", "")) or clean_cell(r.get("Materials_Normalized", "")) or clean_cell(r.get("Materials_Raw", "")),
            "maker": clean_cell(r.get("Designer_or_Maker", "")),
            "list_price": clean_cell(r.get("Original_List_Price_USD", "")),
            "net_price": clean_cell(r.get("Actual_Net_Sale_Price_USD", "")),
            "verified_by_paul": clean_cell(r.get("Verified_By_Paul", "")),
        })
    return matches

# -----------------------------
# Generation helpers
# -----------------------------

def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text or "", re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return {}
    return {}

def generate_item_id():
    return "HSAI-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()

def normalize_price(value):
    s = "" if value is None else str(value).strip()
    if not s:
        return ""
    try:
        return f"${float(s.replace('$','').replace(',','')):,.0f}"
    except Exception:
        return s

def format_dimensions(h, w, d, dia, body_h, seat_h):
    parts = []
    if h: parts.append(f"Height: {h} in")
    if w: parts.append(f"Width: {w} in")
    if d: parts.append(f"Depth: {d} in")
    if dia: parts.append(f"Diameter: {dia} in")
    if body_h: parts.append(f"Body Height: {body_h} in")
    if seat_h: parts.append(f"Seat Height: {seat_h} in")
    return " × ".join(parts)

def enforce_title(title):
    title = str(title or "").strip()
    title = re.sub(r"\b[Cc]irca\b\.?,?\s*", "", title)
    title = re.sub(r"\b[cC]\.\s*", "", title)
    title = re.sub(r"\bca\.\s*", "", title, flags=re.I)
    title = re.sub(r",?\s*\b(17|18|19|20)\d{2}s?\b", "", title)
    origins = ["Italian","French","American","Swedish","Danish","Belgian","English","Spanish","Austrian","German","Dutch","Brazilian","British"]
    for origin in origins:
        title = re.sub(rf"\b{origin}\b\s*", "", title)
    title = re.sub(r"\s{2,}", " ", title).strip(" ,.-")
    if len(title) > 80:
        title = title[:80].rsplit(" ", 1)[0].strip(" ,.-")
    return title

def base_prompt(dims, notes, known_info, target_price, brain_matches=None, brain_profile=None):
    schema = {
        "title": "max 80 chars, no origin/date/circa",
        "description": "approx 200 words, starts with design period/style",
        "suggested_price_usd": "number only",
        "category": "broad category",
        "subcategory": "specific subcategory",
        "style": "period/style",
        "period": "period or movement",
        "country": "metadata only",
        "designer_or_maker": "confirmed/attributed/Unknown",
        "materials": ["material 1", "material 2"],
        "condition_notes": "positive condition language",
        "seo_keywords": ["keyword 1", "keyword 2"],
        "ai_confidence_0_to_100": 0,
        "price_tag_text": "physical tag copy",
        "internal_notes_for_review": "what to verify",
        "dimensions_formatted": dims
    }

    return f"""
You are High Style Deco's inventory cataloging assistant.

HIGH STYLE BRAIN REQUIREMENT:
You MUST study the similar historical High Style Deco records before writing.
Use their tone, structure, material language, and cataloging style.
Do not copy them word-for-word. Write a fresh listing that belongs in the same catalog.

SIMILAR HIGH STYLE DECO RECORDS FROM V5:
{json.dumps({"item_profile": brain_profile or {}, "similar_records": brain_matches or []}, indent=2)}

TITLE RULES:
- Max 80 characters.
- No place of origin in title.
- No years, dates, decades, circa, c., or ca.
- Include item type and strongest descriptive features.

DESCRIPTION RULES:
- Approximately 200 words.
- First words must be the design period/style, e.g. Art Deco, Mid-Century Modern, Modernist, Postmodern.
- Do not start with place of origin.
- Sales-focused High Style Deco / 1stDibs tone.
- Describe the piece in the best light.
- Never say: wear consistent with age and use, aged, age-related wear, minor imperfections, surface scratches.
- Furniture: include exactly "Presented in excellent mint restored condition."
- Lighting: include exactly "Excellent condition. This piece has been professionally rewired to US standards and is ready for installation."

Return ONLY valid JSON:
{json.dumps(schema, indent=2)}

Dimensions:
{dims}

Known info:
{known_info or "None"}

Notes:
{notes or "None"}

Target price:
{target_price or "None"}
"""

def generate_draft(photos, dims, notes, known_info, target_price, brain_matches=None, brain_profile=None):
    client = get_openai_client()
    if client is None:
        return {"error": "No OPENAI_API_KEY found.", "draft": {}}

    content = [{"type": "text", "text": base_prompt(dims, notes, known_info, target_price, brain_matches, brain_profile)}]
    for photo in photos:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(photo)}})

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": content}],
            temperature=0.2
        )
        draft = parse_json(resp.choices[0].message.content)
        draft["title"] = enforce_title(draft.get("title", ""))
        if "dimensions_formatted" not in draft:
            draft["dimensions_formatted"] = dims
        return {"error": "", "draft": draft}
    except Exception as e:
        return {"error": str(e), "draft": {}}

def retry_with_feedback(current_draft, feedback_context, dims, notes, known_info, target_price):
    client = get_openai_client()
    if client is None:
        return {"error": "No OPENAI_API_KEY found.", "draft": {}}

    schema = {
        "title": "revised max 80 chars, no origin/date/circa",
        "description": "revised approx 200 words",
        "suggested_price_usd": "revised number only",
        "category": "broad category",
        "subcategory": "specific subcategory",
        "style": "period/style",
        "period": "period or movement",
        "country": "metadata only",
        "designer_or_maker": "confirmed/attributed/Unknown",
        "materials": ["material 1", "material 2"],
        "condition_notes": "positive condition language",
        "seo_keywords": ["keyword 1", "keyword 2"],
        "ai_confidence_0_to_100": 0,
        "price_tag_text": "physical tag copy",
        "internal_notes_for_review": "what changed and what to verify",
        "revision_summary": "brief summary of how feedback was applied",
        "dimensions_formatted": dims
    }

    prompt = f"""
You are revising a High Style Deco inventory draft.

Use the user's feedback AND the High Style Brain examples to improve the draft BEFORE it is saved.

IMPORTANT:
- Do not simply return the same draft.
- The revised title, description, price, or metadata must change meaningfully when feedback requests a change.
- Treat user feedback as highest priority unless it conflicts with house rules.
- Use high_style_brain_matches as the primary writing style reference.
- Preserve dimensions exactly unless the user asks to change them.

CURRENT DRAFT:
{json.dumps(current_draft, indent=2)}

USER FEEDBACK / EDITING INSTRUCTIONS:
{json.dumps(feedback_context, indent=2)}

ORIGINAL ITEM CONTEXT:
Dimensions: {dims}
Known info: {known_info or "None"}
Notes: {notes or "None"}
Target price: {target_price or "None"}

Return ONLY valid JSON using this schema:
{json.dumps(schema, indent=2)}
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            temperature=0.2
        )
        draft = parse_json(resp.choices[0].message.content)
        draft["title"] = enforce_title(draft.get("title", ""))
        if "dimensions_formatted" not in draft:
            draft["dimensions_formatted"] = dims
        return {"error": "", "draft": draft}
    except Exception as e:
        return {"error": str(e), "draft": {}}

# -----------------------------
# Google Sheet
# -----------------------------

def normalize_google_script_url(url):
    url = str(url or "").strip()
    if not url:
        return ""
    if url.startswith("AKfy"):
        return "https://script.google.com/macros/s/" + url.strip("/") + "/exec"
    return url

def send_to_google_sheet(url, payload):
    url = normalize_google_script_url(url)
    try:
        r = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=30, allow_redirects=True)
        if r.status_code >= 400:
            return False, f"HTTP {r.status_code}: {r.text[:500]}"
        try:
            data = r.json()
            if data.get("result") == "success":
                return True, "Saved to Google Sheet."
            return True, f"Completed. Response: {data}"
        except Exception:
            if "success" in (r.text or "").lower():
                return True, "Saved to Google Sheet."
            return True, f"Completed. Response: {(r.text or '')[:500]}"
    except Exception as e:
        return False, str(e)

def send_learning_log(url, payload):
    url = normalize_google_script_url(url)
    learning_payload = dict(payload)
    learning_payload["Action"] = "Learning_Log"
    try:
        r = requests.post(url, data=json.dumps(learning_payload), headers={"Content-Type": "application/json"}, timeout=30, allow_redirects=True)
        if r.status_code >= 400:
            return False, f"Learning log HTTP {r.status_code}: {r.text[:500]}"
        return True, "Learning feedback sent."
    except Exception as e:
        return False, str(e)

# -----------------------------
# App UI
# -----------------------------

init_state()
st.set_page_config(page_title=APP_TITLE, layout="wide")

if not st.session_state.get("authenticated"):
    login_gate()

st.title(APP_TITLE)
st.caption("Employee Access + High Style Brain + hidden Google Sheet connection.")

current_user = st.session_state.get("current_user", "Unknown")
current_role = st.session_state.get("current_role", "Employee")
form_key = st.session_state.get("form_version", 0)

with st.sidebar:
    st.success(f"Logged in as: {current_user} ({current_role})")
    if st.button("Log out"):
        clear_entry_state()
        st.session_state.pop("authenticated", None)
        st.session_state.pop("current_user", None)
        st.session_state.pop("current_role", None)
        st.rerun()

    st.header("Google Sheet")
    web_app_url = get_secret("GOOGLE_APPS_SCRIPT_URL")
    if web_app_url:
        st.success("Google Sheet connected")
    else:
        st.error("Google Sheet URL missing from Streamlit secrets")

    st.header("Cloudinary")
    c_ok, c_msg = configure_cloudinary()
    if c_ok:
        st.success("Cloudinary configured")
    else:
        st.warning(c_msg)

    st.header("High Style Brain")
    brain_df, brain_source = load_high_style_brain()
    if brain_source:
        st.success(f"Brain loaded: {brain_source} ({len(brain_df):,} rows)")
    else:
        st.warning("High Style Brain V5 dataset not found.")

    if st.button("Start New Entry / Clear Current Form"):
        clear_entry_state()
        st.rerun()

st.header("1. Upload item photos")
photos = st.file_uploader(
    "Upload main photo plus detail photos",
    type=["jpg", "jpeg", "png", "webp", "heic", "heif"],
    accept_multiple_files=True,
    key=f"photo_uploader_{st.session_state['uploader_version']}"
)

if photos:
    cols = st.columns(min(len(photos), 4))
    for i, photo in enumerate(photos[:4]):
        with cols[i % len(cols)]:
            try:
                st.image(photo, caption=f"Photo {i+1}", use_container_width=True)
            except Exception:
                st.caption(f"Photo {i+1}: {photo.name}")

st.header("2. Enter dimensions")
c1, c2, c3 = st.columns(3)
with c1: height = st.text_input("Height in", key=f"height_input_{form_key}")
with c2: width = st.text_input("Width in", key=f"width_input_{form_key}")
with c3: depth = st.text_input("Depth in", key=f"depth_input_{form_key}")
c4, c5, c6 = st.columns(3)
with c4: diameter = st.text_input("Diameter in", key=f"diameter_input_{form_key}")
with c5: body_height = st.text_input("Body Height in", key=f"body_height_input_{form_key}")
with c6: seat_height = st.text_input("Seat Height in", key=f"seat_height_input_{form_key}")

dims = format_dimensions(height, width, depth, diameter, body_height, seat_height)
if dims:
    st.caption(f"Formatted dimensions: {dims}")

st.header("3. Add known info")
st.caption(f"Submitted by: {current_user}")
known_info = st.text_area("Known maker/style/materials/period", height=90, key=f"known_info_input_{form_key}")
notes = st.text_area("Internal notes", height=90, key=f"notes_input_{form_key}")
target_price = st.text_input("Optional target/list price", key=f"target_price_input_{form_key}")

if st.button("Generate Draft Item Record", type="primary"):
    if not photos:
        st.warning("Upload at least one item photo.")
        st.stop()

    with st.spinner("Reading photos and building High Style Brain search profile..."):
        brain_profile = quick_image_profile(photos, dims, known_info, notes)

    with st.spinner("Searching High Style Brain V5 for similar historical records..."):
        brain_matches = find_brain_matches(brain_df, brain_profile, dims, known_info, notes, top_n=8)

    st.session_state["brain_profile"] = brain_profile
    st.session_state["brain_matches"] = brain_matches

    with st.spinner("Generating draft using High Style Brain examples..."):
        result = generate_draft(photos, dims, notes, known_info, target_price, brain_matches=brain_matches, brain_profile=brain_profile)

    if result["error"]:
        st.error(result["error"])
        st.stop()

    st.session_state["draft"] = result["draft"]
    st.session_state["original_ai_draft"] = dict(result["draft"])
    st.session_state["item_id"] = generate_item_id()
    st.session_state["photo_names"] = [p.name for p in photos]
    st.session_state["dims_inputs"] = {
        "height": height, "width": width, "depth": depth,
        "diameter": diameter, "body_height": body_height, "seat_height": seat_height
    }
    st.session_state["dims_formatted"] = dims
    st.session_state["input_notes"] = notes
    st.session_state["photos_for_save"] = photos
    st.session_state["submitted_by"] = current_user
    st.session_state["submitted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state["retry_history"] = []

if st.session_state.get("brain_matches"):
    with st.expander(f"High Style Brain matches used ({len(st.session_state.get('brain_matches', []))})"):
        if st.session_state.get("brain_profile"):
            st.caption("AI search profile")
            st.json(st.session_state.get("brain_profile"))
        for i, m in enumerate(st.session_state.get("brain_matches", []), 1):
            st.markdown(f"**{i}. {m.get('title','')}**")
            st.caption(f"Score {m.get('match_score','')} | {m.get('style','')} | {m.get('materials','')} | {m.get('maker','')} | Verified: {m.get('verified_by_paul','')}")
            if m.get("list_price") or m.get("net_price"):
                st.caption(f"List: {m.get('list_price','')} | Net: {m.get('net_price','')}")
            st.write(str(m.get("description",""))[:700])

if "draft" in st.session_state:
    draft = st.session_state["draft"]
    original = st.session_state.get("original_ai_draft", draft)
    inputs = st.session_state["dims_inputs"]

    st.divider()
    st.header("4. Review / Edit Draft")

    item_id = st.text_input("Item ID", value=st.session_state["item_id"], key=f"item_id_review_{form_key}")
    title = st.text_input("Title", value=str(draft.get("title", "")), max_chars=80, key=f"title_review_{form_key}")
    st.caption(f"Title length: {len(title)} / 80")
    description = st.text_area("Description", value=str(draft.get("description", "")), height=260, key=f"description_review_{form_key}")
    st.caption(f"Approx word count: {len(description.split())}")

    c1, c2, c3 = st.columns(3)
    with c1: suggested_price = st.text_input("Suggested Price USD", value=str(draft.get("suggested_price_usd", "")), key=f"suggested_price_review_{form_key}")
    with c2: approved_price = st.text_input("Approved Price USD", value=str(draft.get("suggested_price_usd", "")), key=f"approved_price_review_{form_key}")
    with c3: confidence = st.text_input("AI Confidence", value=str(draft.get("ai_confidence_0_to_100", "")), key=f"confidence_review_{form_key}")

    c4, c5, c6 = st.columns(3)
    with c4: category = st.text_input("Category", value=str(draft.get("category", "")), key=f"category_review_{form_key}")
    with c5: subcategory = st.text_input("Subcategory", value=str(draft.get("subcategory", "")), key=f"subcategory_review_{form_key}")
    with c6: style = st.text_input("Style", value=str(draft.get("style", "")), key=f"style_review_{form_key}")

    c7, c8, c9 = st.columns(3)
    with c7: period = st.text_input("Period", value=str(draft.get("period", "")), key=f"period_review_{form_key}")
    with c8: country = st.text_input("Country / Region", value=str(draft.get("country", "")), key=f"country_review_{form_key}")
    with c9: maker = st.text_input("Designer / Maker", value=str(draft.get("designer_or_maker", "")), key=f"maker_review_{form_key}")

    mats = draft.get("materials", [])
    materials_text_default = ", ".join(mats) if isinstance(mats, list) else str(mats)
    seo = draft.get("seo_keywords", [])
    seo_text_default = ", ".join(seo) if isinstance(seo, list) else str(seo)

    materials_text = st.text_input("Materials", value=materials_text_default, key=f"materials_review_{form_key}")
    saved_dims = st.session_state.get("dims_formatted", "")
    dims_default = str(draft.get("dimensions_formatted", "") or "").strip() or saved_dims or dims
    dims_final = st.text_input("Dimensions", value=dims_default, key=f"dims_final_review_{form_key}")
    condition_notes = st.text_area("Condition Notes", value=str(draft.get("condition_notes", "")), height=90, key=f"condition_notes_review_{form_key}")
    st.text_area("Price Tag Text", value=str(draft.get("price_tag_text", "")), height=140, key=f"price_tag_review_{form_key}")
    seo_text = st.text_input("SEO Keywords", value=seo_text_default, key=f"seo_review_{form_key}")
    review_notes = st.text_area("Internal Notes for Review", value=str(draft.get("internal_notes_for_review", "")), height=100, key=f"internal_review_notes_{form_key}")
    if draft.get("revision_summary"):
        st.info("Revision summary: " + str(draft.get("revision_summary", "")))

    st.subheader("5. Feedback / Retry")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        title_feedback = st.selectbox("Title quality", ["Excellent", "Good", "Needs edits", "Poor"], key=f"title_feedback_{form_key}")
    with f2:
        description_feedback = st.selectbox("Description quality", ["Excellent", "Good", "Needs edits", "Poor"], key=f"description_feedback_{form_key}")
    with f3:
        price_feedback = st.selectbox("Price suggestion", ["About right", "Too high", "Too low", "Not enough data"], key=f"price_feedback_{form_key}")
    with f4:
        reference_feedback = st.selectbox("Reference quality", ["Good references", "Some useful", "Not useful", "Not used"], key=f"reference_feedback_{form_key}")

    changed_notes = st.text_area(
        "Feedback for AI before saving",
        placeholder="Tell the AI what to fix. Example: make title shorter, use more High Style Deco style, improve description based on the Brain examples.",
        height=110,
        key=f"changed_notes_{form_key}"
    )

    if st.button("Try Again With Feedback", type="secondary"):
        feedback_context = {
            "title_feedback": title_feedback,
            "description_feedback": description_feedback,
            "price_feedback": price_feedback,
            "reference_feedback": reference_feedback,
            "feedback_notes": changed_notes,
            "current_user_edited_title": title,
            "current_user_edited_description": description,
            "current_user_approved_price": approved_price,
            "current_category": category,
            "current_subcategory": subcategory,
            "current_style": style,
            "current_period": period,
            "current_maker": maker,
            "current_materials": materials_text,
            "high_style_brain_matches": st.session_state.get("brain_matches", []),
            "high_style_brain_profile": st.session_state.get("brain_profile", {})
        }
        current_draft_for_retry = dict(draft)
        current_draft_for_retry.update({
            "title": title,
            "description": description,
            "suggested_price_usd": suggested_price,
            "category": category,
            "subcategory": subcategory,
            "style": style,
            "period": period,
            "country": country,
            "designer_or_maker": maker,
            "materials": materials_text,
            "condition_notes": condition_notes,
            "seo_keywords": seo_text,
            "dimensions_formatted": dims_final
        })
        with st.spinner("Rewriting draft using your feedback and High Style Brain matches..."):
            result = retry_with_feedback(current_draft_for_retry, feedback_context, dims_final, notes, known_info, target_price)
        if result["error"]:
            st.error(result["error"])
        else:
            st.session_state["retry_history"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "before": current_draft_for_retry,
                "feedback": feedback_context,
                "after": result["draft"]
            })
            st.session_state["draft"] = result["draft"]
            st.session_state["dims_formatted"] = result["draft"].get("dimensions_formatted") or dims_final or st.session_state.get("dims_formatted", "")
            st.session_state["form_version"] = st.session_state.get("form_version", 0) + 1
            st.rerun()

    if st.session_state.get("retry_history"):
        with st.expander(f"Retry history ({len(st.session_state['retry_history'])})"):
            for i, entry in enumerate(st.session_state["retry_history"], 1):
                st.markdown(f"**Retry {i} — {entry.get('timestamp','')}**")
                st.write("Feedback:", entry.get("feedback", {}).get("feedback_notes", ""))
                st.write("Before title:", entry.get("before", {}).get("title", ""))
                st.write("After title:", entry.get("after", {}).get("title", ""))

    st.subheader("Shoot List Row Preview")
    preview = pd.DataFrame([{
        "Image": "Cloudinary thumbnail will appear in Google Sheet",
        "Title": title,
        "Dimensions": dims_final,
        "Price": normalize_price(approved_price),
        "Description": description,
        "Status": "Approved"
    }])
    st.dataframe(preview, use_container_width=True, hide_index=True)

    st.header("6. Approve & Save Final Version to Google Sheet")
    st.caption(f"Approver: {current_user}")

    if st.session_state.get("last_saved"):
        st.success("Saved successfully.")
        if st.button("Submit Another Entry", type="primary"):
            clear_entry_state()
            st.rerun()

    elif not web_app_url:
        st.warning("Google Sheet URL is missing from Streamlit secrets. Add GOOGLE_APPS_SCRIPT_URL in Streamlit app secrets.")
    elif not c_ok:
        st.warning("Cloudinary is not configured.")
    elif st.button("Approve & Save to Google Sheet", type="primary"):
        with st.spinner("Uploading primary image to Cloudinary..."):
            primary_url, upload_error = upload_to_cloudinary(st.session_state["photos_for_save"][0], item_id)
        if upload_error:
            st.error(f"Cloudinary upload failed: {upload_error}")
            st.stop()

        image_formula = f'=IMAGE("{primary_url}", 4, 120, 120)'
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        price = normalize_price(approved_price or suggested_price)

        payload = {
            "Item_ID": item_id, "Status": "Approved", "Primary_Image": image_formula,
            "Primary_Image_URL": primary_url, "Additional_Images": ", ".join(st.session_state.get("photo_names", [])[1:]),
            "AI_Confidence": confidence, "Title": title, "Description": description, "Dimensions": dims_final,
            "Height_in": inputs.get("height", ""), "Width_in": inputs.get("width", ""), "Depth_in": inputs.get("depth", ""),
            "Diameter_in": inputs.get("diameter", ""), "Body_Height_in": inputs.get("body_height", ""), "Seat_Height_in": inputs.get("seat_height", ""),
            "Suggested_Price_USD": normalize_price(suggested_price), "Approved_Price_USD": price,
            "Category": category, "Subcategory": subcategory, "Style": style, "Period": period, "Country": country,
            "Designer_or_Maker": maker, "Materials": materials_text, "Condition_Notes": condition_notes,
            "Internal_Notes": (st.session_state.get("input_notes", "") + " | " + review_notes).strip(" |"),
            "Ready_For_Photos": "Yes", "Ready_For_Publishing": "No", "Created_Date": now, "Last_Updated": now, "SEO_Keywords": seo_text,
            "Submitted_By": st.session_state.get("submitted_by", current_user),
            "Submitted_Date": st.session_state.get("submitted_date", now),
            "Approved_By": current_user,
            "Approved_Date": now,
            "User_Role": current_role
        }

        learning_payload = {
            "Timestamp": now, "Item_ID": item_id,
            "Original_AI_Title": original.get("title", ""), "Final_Approved_Title": title,
            "Original_AI_Description": original.get("description", ""), "Final_Approved_Description": description,
            "Original_AI_Price": original.get("suggested_price_usd", ""), "Final_Approved_Price": price,
            "Title_Feedback": title_feedback, "Description_Feedback": description_feedback,
            "Price_Feedback": price_feedback, "Reference_Feedback": reference_feedback,
            "Learning_Notes": changed_notes, "Retry_Count": len(st.session_state.get("retry_history", [])),
            "Retry_History_JSON": json.dumps(st.session_state.get("retry_history", []), default=str),
            "Primary_Image_URL": primary_url,
            "High_Style_Brain_Matches_JSON": json.dumps(st.session_state.get("brain_matches", []), default=str),
            "Submitted_By": st.session_state.get("submitted_by", current_user),
            "Submitted_Date": st.session_state.get("submitted_date", now),
            "Approved_By": current_user,
            "Approved_Date": now,
            "User_Role": current_role
        }

        with st.spinner("Sending final approved item to Google Sheet..."):
            ok, msg = send_to_google_sheet(web_app_url, payload)
        if not ok:
            st.error(msg)
            st.stop()

        with st.spinner("Sending learning log..."):
            log_ok, log_msg = send_learning_log(web_app_url, learning_payload)

        st.success("Final approved item saved to Google Sheet.")
        if log_ok:
            st.success("Feedback, retry history, and Brain matches saved to Learning_Log.")
        else:
            st.warning(f"Item saved, but learning log may not have saved: {log_msg}")

        st.session_state["last_saved"] = True
        st.rerun()
