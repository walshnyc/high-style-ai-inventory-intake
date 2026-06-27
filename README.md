# High Style AI – Inventory Intake Task 3.1.1: Hidden Google Sheet Connection

This version keeps Task 3.1 employee access and removes the need for anyone to paste the Apps Script Web App URL inside the app.

## What this adds

- Google Apps Script URL is stored in Streamlit Secrets
- Sidebar now shows `Google Sheet connected`
- Employees cannot paste the wrong URL
- Keeps login screen
- Keeps employee submitter / approver tracking
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

Do not upload `__pycache__`.

## Streamlit secrets

Use this format:

```toml
OPENAI_API_KEY = "your_openai_key"

CLOUDINARY_CLOUD_NAME = "your_cloud_name"
CLOUDINARY_API_KEY = "your_cloudinary_api_key"
CLOUDINARY_API_SECRET = "your_cloudinary_api_secret"

EMPLOYEE_PASSWORD = "choose_employee_password"
ADMIN_PASSWORD = "choose_admin_password"

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/xxxxx/exec"
```

## Login

Admin:
- Name: Paul
- Password: your `ADMIN_PASSWORD`

Employee:
- Name: employee name
- Password: your `EMPLOYEE_PASSWORD`
