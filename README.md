# High Style AI – Task 3.3.9: Stable Generation Pipeline

This version keeps Task 3.3.8 and reduces the largest memory/CPU spike during generation.

## What changed

- Photos are analyzed once, not twice.
- Final title/description generation uses the completed visual profile and Brain matches.
- Visual analysis uses up to three photos.
- Brain matching is vectorized.
- The full 12,880-row DataFrame is no longer copied during every generation.
- The Python row-by-row scoring loop has been removed.
- High Style Brain matches are reduced to the six strongest references.

## Features retained

- Advanced Draft Manager
- Active and completed draft dashboards
- Continue Editing
- Delete Draft
- Cloudinary URL restoration
- Audit trail and learning metrics
- Employee login
- Google Sheet workflow

## GitHub upload

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Then reboot Streamlit.
