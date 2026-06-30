# High Style AI – Inventory Intake Task 3.3: Draft Inventory Queue

This version keeps everything from Task 3.2 and adds draft inventory support.

## Kept from Task 3.2

- Employee login
- Hidden Google Apps Script URL from Streamlit secrets
- High Style Brain V5 historical matching
- Feedback retry loop
- Audit Trail Preview
- Learning metrics
- Cloudinary image upload
- Google Sheet save
- Submit Another Entry reset

## New in Task 3.3

- Save Draft button
- Draft photos upload to Cloudinary
- Draft metadata saved to Google Sheets with `Action = Draft_Save`
- Saved Drafts area
- Optional draft loading with `Action = Draft_List`
- Final approved inventory can carry `Source_Draft_ID`

## Required GitHub upload

Upload all of these:

- app.py
- requirements.txt
- README.md
- data/High_Style_Deco_Master_Dataset_V5_AI_Ready_Verification.xlsx

Do not upload `__pycache__`.

## Streamlit secrets

Keep your existing secrets:

```toml
OPENAI_API_KEY = "your_openai_key"
CLOUDINARY_CLOUD_NAME = "your_cloud_name"
CLOUDINARY_API_KEY = "your_cloudinary_api_key"
CLOUDINARY_API_SECRET = "your_cloudinary_api_secret"
EMPLOYEE_PASSWORD = "choose_employee_password"
ADMIN_PASSWORD = "choose_admin_password"
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/xxxxx/exec"
```

## Apps Script update needed

To fully use drafts, the Google Apps Script needs to support:

- `Action = Draft_Save`
- `Action = Draft_List`

If the script is not updated, the rest of the app still works, but draft saving/loading will not work correctly.
