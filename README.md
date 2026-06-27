# High Style AI – Inventory Intake Task 2.7.3: Dimension Save Fix

This version fixes a dimension-saving issue after using **Try Again With Feedback**.

## Fixes

- Preserves the original entered dimensions through retry refreshes
- Uses the final reviewed `Dimensions` field when saving to Google Sheets
- Keeps individual Height / Width / Depth / Diameter / Body Height / Seat Height values from the original dimension inputs
- Keeps all 2.7.2 fixes:
  - feedback retry refresh
  - full form reset
  - HEIC support
  - Cloudinary upload
  - Google Sheets save
  - Learning_Log

## Deploy

Upload these three files to GitHub:
- app.py
- requirements.txt
- README.md

Streamlit should auto-redeploy after the GitHub commit.
