# High Style AI – Inventory Intake Task 3.0: High Style Brain Reference

This is the corrected Task 3.0 package.

## What this version does

- Loads the High Style Deco V5 Brain spreadsheet from the `data/` folder
- Searches V5 for similar historical High Style Deco records before writing
- Shows matched historical examples in the app
- Forces OpenAI to use the V5 examples for title and description generation
- Uses the V5 examples again during feedback retry
- Keeps Cloudinary, Google Sheets save, Learning_Log, HEIC support, reset fixes, and dimension save behavior

## Required GitHub upload

Upload all of these to GitHub:

- app.py
- requirements.txt
- README.md
- data/High_Style_Deco_Master_Dataset_V5_AI_Ready_Verification.xlsx

## Streamlit secrets

Use:

```toml
OPENAI_API_KEY = "your_openai_key"

CLOUDINARY_CLOUD_NAME = "your_cloud_name"
CLOUDINARY_API_KEY = "your_cloudinary_api_key"
CLOUDINARY_API_SECRET = "your_cloudinary_api_secret"
```
