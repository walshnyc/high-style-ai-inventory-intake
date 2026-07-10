# High Style AI – Task 3.3.1: Streamlit Startup Stability Fix

This hotfix keeps all Task 3.3 features and addresses the Streamlit Community Cloud startup segmentation fault.

## What changed

- Pins Python package versions instead of installing unpredictable latest releases
- Pins `pillow-heif==0.13.0`
- Pins `pillow==10.4.0`
- Loads the native HEIC plugin only when an image needs it
- Keeps:
  - Draft Inventory Queue
  - Audit trail and learning metrics
  - Employee login
  - Hidden Google Sheet connection
  - High Style Brain
  - Cloudinary
  - Feedback retry loop

## Upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Do not upload `__pycache__`.

## Streamlit

After committing the files:

1. Open the app in Streamlit Community Cloud.
2. Open Manage app.
3. Reboot the app.
4. Watch the logs until the app reaches Running.
