# High Style AI – Inventory Intake Task 2.7.1: Full Form Reset Fix

This version fixes the reset bug where dimensions, title, description, price, notes, feedback, or draft fields could stay populated after clicking **Start New Entry / Clear Current Form** or **Submit Another Entry**.

## Fixes

- Clear Current Form resets uploaded photos
- Clear Current Form resets dimensions
- Clear Current Form resets known info and notes
- Clear Current Form resets generated title, description, price, category, materials, feedback, and retry history
- Submit Another Entry also resets all form fields
- HEIC / HEIF support remains included
- Cloudinary, Google Sheets, feedback retry loop, and Learning_Log remain included

## Deploy

Upload these three files to GitHub:
- app.py
- requirements.txt
- README.md
