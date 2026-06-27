import os, json, re, base64, uuid, tempfile
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

APP_TITLE = "High Style AI – Inventory Intake Task 2.7"

def init_state():
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0
    if "retry_history" not in st.session_state:
        st.session_state["retry_history"] = []

def clear_entry_state():
    keys_to_clear = [
        "draft", "item_id", "photo_names", "dims_inputs", "input_notes",
        "photos_for_save", "last_saved", "original_ai_draft",
        "retry_history", "height_input", "width_input", "depth_input",
        "diameter_input", "body_height_input", "seat_height_input",
        "known_info_input", "notes_input", "target_price_input"
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1
    st.session_state["retry_history"] = []

def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            key = None
    if not key or OpenAI is None:
        return None
    return OpenAI(api_key=key)

def configure_cloudinary():
    if cloudinary is None:
        return False, "Cloudinary package is not installed."
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not cloud_name or not api_key or not api_secret:
        return False, "Missing Cloudinary environment variables."
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    return True, ""

def safe_open_image(raw):
    return Image.open(BytesIO(raw)).convert("RGB")

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

def base_prompt(dims, notes, known_info, target_price):
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
        "internal_notes_for_review": "what to verify"
    }

    return f"""
You are High Style Deco's inventory cataloging assistant.

Create a polished draft inventory record.

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

def generate_draft(photos, dims, notes, known_info, target_price):
    client = get_openai_client()
    if client is None:
        return {"error": "No OPENAI_API_KEY found.", "draft": {}}

    content = [{"type": "text", "text": base_prompt(dims, notes, known_info, target_price)}]
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
        "revision_summary": "brief summary of how feedback was applied"
    }

    prompt = f"""
You are revising a High Style Deco inventory draft.

Use the user's feedback to improve the draft BEFORE it is saved to the Google Sheet.

Keep following all house rules:
- Title max 80 characters.
- No country/place of origin in title.
- No years, dates, decades, circa, c., or ca. in title.
- Description approx 200 words.
- Description must start with design period/style.
- Sales-focused, polished High Style Deco / 1stDibs tone.
- No negative condition language.
- Furniture: include exactly "Presented in excellent mint restored condition."
- Lighting: include exactly "Excellent condition. This piece has been professionally rewired to US standards and is ready for installation."

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
        return {"error": "", "draft": draft}
    except Exception as e:
        return {"error": str(e), "draft": {}}

def send_to_google_sheet(url, payload):
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
    learning_payload = dict(payload)
    learning_payload["Action"] = "Learning_Log"
    try:
        r = requests.post(url, data=json.dumps(learning_payload), headers={"Content-Type": "application/json"}, timeout=30, allow_redirects=True)
        if r.status_code >= 400:
            return False, f"Learning log HTTP {r.status_code}: {r.text[:500]}"
        return True, "Learning feedback sent."
    except Exception as e:
        return False, str(e)

init_state()
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Feedback Retry Loop: use feedback to regenerate before final Google Sheet save.")

with st.sidebar:
    st.header("Google Sheet")
    web_app_url = st.text_input("Apps Script Web App URL", type="password", placeholder="Paste URL ending in /exec")

    st.header("Cloudinary")
    c_ok, c_msg = configure_cloudinary()
    if c_ok:
        st.success("Cloudinary configured")
    else:
        st.warning(c_msg)

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
                st.image(photo, caption=f"Photo {i+1}", width="stretch")
            except Exception:
                st.caption(f"Photo {i+1}: {photo.name}")

st.header("2. Enter dimensions")
c1, c2, c3 = st.columns(3)
with c1: height = st.text_input("Height in", key="height_input")
with c2: width = st.text_input("Width in", key="width_input")
with c3: depth = st.text_input("Depth in", key="depth_input")
c4, c5, c6 = st.columns(3)
with c4: diameter = st.text_input("Diameter in", key="diameter_input")
with c5: body_height = st.text_input("Body Height in", key="body_height_input")
with c6: seat_height = st.text_input("Seat Height in", key="seat_height_input")

dims = format_dimensions(height, width, depth, diameter, body_height, seat_height)
if dims:
    st.caption(f"Formatted dimensions: {dims}")

st.header("3. Add known info")
known_info = st.text_area("Known maker/style/materials/period", height=90, key="known_info_input")
notes = st.text_area("Internal notes", height=90, key="notes_input")
target_price = st.text_input("Optional target/list price", key="target_price_input")

if st.button("Generate Draft Item Record", type="primary"):
    if not photos:
        st.warning("Upload at least one item photo.")
        st.stop()

    with st.spinner("Generating draft..."):
        result = generate_draft(photos, dims, notes, known_info, target_price)

    if result["error"]:
        st.error(result["error"])
        st.stop()

    st.session_state["draft"] = result["draft"]
    st.session_state["original_ai_draft"] = dict(result["draft"])
    st.session_state["item_id"] = generate_item_id()
    st.session_state["photo_names"] = [p.name for p in photos]
    st.session_state["dims_inputs"] = {"height": height, "width": width, "depth": depth, "diameter": diameter, "body_height": body_height, "seat_height": seat_height}
    st.session_state["input_notes"] = notes
    st.session_state["photos_for_save"] = photos
    st.session_state["retry_history"] = []

if "draft" in st.session_state:
    draft = st.session_state["draft"]
    original = st.session_state.get("original_ai_draft", draft)
    inputs = st.session_state["dims_inputs"]

    st.divider()
    st.header("4. Review / Edit Draft")

    item_id = st.text_input("Item ID", value=st.session_state["item_id"])
    title = st.text_input("Title", value=str(draft.get("title", "")), max_chars=80)
    st.caption(f"Title length: {len(title)} / 80")
    description = st.text_area("Description", value=str(draft.get("description", "")), height=260)
    st.caption(f"Approx word count: {len(description.split())}")

    c1, c2, c3 = st.columns(3)
    with c1: suggested_price = st.text_input("Suggested Price USD", value=str(draft.get("suggested_price_usd", "")))
    with c2: approved_price = st.text_input("Approved Price USD", value=str(draft.get("suggested_price_usd", "")))
    with c3: confidence = st.text_input("AI Confidence", value=str(draft.get("ai_confidence_0_to_100", "")))

    c4, c5, c6 = st.columns(3)
    with c4: category = st.text_input("Category", value=str(draft.get("category", "")))
    with c5: subcategory = st.text_input("Subcategory", value=str(draft.get("subcategory", "")))
    with c6: style = st.text_input("Style", value=str(draft.get("style", "")))

    c7, c8, c9 = st.columns(3)
    with c7: period = st.text_input("Period", value=str(draft.get("period", "")))
    with c8: country = st.text_input("Country / Region", value=str(draft.get("country", "")))
    with c9: maker = st.text_input("Designer / Maker", value=str(draft.get("designer_or_maker", "")))

    mats = draft.get("materials", [])
    materials_text = ", ".join(mats) if isinstance(mats, list) else str(mats)
    seo = draft.get("seo_keywords", [])
    seo_text = ", ".join(seo) if isinstance(seo, list) else str(seo)

    materials_text = st.text_input("Materials", value=materials_text)
    dims_final = st.text_input("Dimensions", value=dims)
    condition_notes = st.text_area("Condition Notes", value=str(draft.get("condition_notes", "")), height=90)
    st.text_area("Price Tag Text", value=str(draft.get("price_tag_text", "")), height=140)
    seo_text = st.text_input("SEO Keywords", value=seo_text)
    review_notes = st.text_area("Internal Notes for Review", value=str(draft.get("internal_notes_for_review", "")), height=100)

    st.subheader("5. Feedback / Retry")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        title_feedback = st.selectbox("Title quality", ["Excellent", "Good", "Needs edits", "Poor"])
    with f2:
        description_feedback = st.selectbox("Description quality", ["Excellent", "Good", "Needs edits", "Poor"])
    with f3:
        price_feedback = st.selectbox("Price suggestion", ["About right", "Too high", "Too low", "Not enough data"])
    with f4:
        reference_feedback = st.selectbox("Reference quality", ["Good references", "Some useful", "Not useful", "Not used"])

    changed_notes = st.text_area(
        "Feedback for AI before saving",
        placeholder="Tell the AI what to fix. Example: make title shorter, remove maker attribution, make description more sales focused, price too low.",
        height=110
    )

    col_retry, col_dummy = st.columns([1, 2])
    with col_retry:
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
                "current_materials": materials_text
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
                "seo_keywords": seo_text
            })

            with st.spinner("Rewriting draft using your feedback..."):
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
                st.success("AI revised the draft using your feedback.")
                st.rerun()

    if st.session_state.get("retry_history"):
        with st.expander(f"Retry history ({len(st.session_state['retry_history'])})"):
            for i, entry in enumerate(st.session_state["retry_history"], 1):
                st.markdown(f"**Retry {i} — {entry.get('timestamp','')}**")
                st.write("Feedback:", entry.get("feedback", {}).get("feedback_notes", ""))
                st.write("Before title:", entry.get("before", {}).get("title", ""))
                st.write("After title:", entry.get("after", {}).get("title", ""))

    st.subheader("Shoot List Row Preview")
    preview = pd.DataFrame([{"Image": "Cloudinary thumbnail will appear in Google Sheet", "Title": title, "Dimensions": dims_final, "Price": normalize_price(approved_price), "Description": description, "Status": "Approved"}])
    st.dataframe(preview, width="stretch", hide_index=True)

    st.header("6. Approve & Save Final Version to Google Sheet")

    if st.session_state.get("last_saved"):
        st.success("Saved successfully.")
        if st.button("Submit Another Entry", type="primary"):
            clear_entry_state()
            st.rerun()

    elif not web_app_url:
        st.warning("Paste your Apps Script Web App URL in the sidebar.")
    elif not c_ok:
        st.warning("Cloudinary is not configured in Terminal.")
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
            "Ready_For_Photos": "Yes", "Ready_For_Publishing": "No", "Created_Date": now, "Last_Updated": now, "SEO_Keywords": seo_text
        }

        learning_payload = {
            "Timestamp": now,
            "Item_ID": item_id,
            "Original_AI_Title": original.get("title", ""),
            "Final_Approved_Title": title,
            "Original_AI_Description": original.get("description", ""),
            "Final_Approved_Description": description,
            "Original_AI_Price": original.get("suggested_price_usd", ""),
            "Final_Approved_Price": price,
            "Title_Feedback": title_feedback,
            "Description_Feedback": description_feedback,
            "Price_Feedback": price_feedback,
            "Reference_Feedback": reference_feedback,
            "Learning_Notes": changed_notes,
            "Retry_Count": len(st.session_state.get("retry_history", [])),
            "Retry_History_JSON": json.dumps(st.session_state.get("retry_history", []), default=str),
            "Primary_Image_URL": primary_url
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
            st.success("Feedback and retry history saved to Learning_Log.")
        else:
            st.warning(f"Item saved, but learning log may not have saved: {log_msg}")

        st.session_state["last_saved"] = True
        st.rerun()
