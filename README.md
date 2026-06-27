# High Style AI – Inventory Intake Task 3.1: Employee Access + Submitter Tracking

This version keeps Task 3.0 High Style Brain and adds a simple employee access layer.

## What this adds

- Simple login screen
- Tracks who submitted the item
- Tracks who approved/saved the item
- Saves submitter/approver fields to Google Sheets payload
- Keeps High Style Brain V5 matching
- Keeps Cloudinary image upload
- Keeps Google Sheet save
- Keeps feedback retry loop and Learning_Log

## Required GitHub upload

Upload all of these:

- app.py
- requirements.txt
- README.md
- data/High_Style_Deco_Master_Dataset_V5_AI_Ready_Verification.xlsx

## Streamlit secrets

Recommended simple version:

```toml
OPENAI_API_KEY = "your_openai_key"

CLOUDINARY_CLOUD_NAME = "your_cloud_name"
CLOUDINARY_API_KEY = "your_cloudinary_api_key"
CLOUDINARY_API_SECRET = "your_cloudinary_api_secret"

EMPLOYEE_PASSWORD = "choose_employee_password"
ADMIN_PASSWORD = "choose_admin_password"
```

Optional named-user version:

```toml
EMPLOYEE_USERS = "Paul:paul_password:Admin,Employee Name:employee_password:Employee"
```

If you use `EMPLOYEE_USERS`, the app shows a user dropdown. If not, it asks for a name and password.

## Google Apps Script note

To store the new fields in Google Sheets, add these headers/fields to your Apps Script row order later:

- Submitted_By
- Submitted_Date
- Approved_By
- Approved_Date
- User_Role

The app should still send the existing fields as before.
