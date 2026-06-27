# High Style AI – Inventory Intake Task 3.0: High Style Brain Reference

This version forces the app to use the High Style Deco V5 historical dataset before generating titles and descriptions.

## What changed
- Loads V5 from the `data/` folder
- Creates an AI image/profile summary
- Searches the V5 brain for similar historical High Style Deco records
- Shows the matched examples in the app
- Passes those examples into OpenAI before title/description generation
- Retry feedback also includes the same High Style Brain matches
- Keeps Cloudinary, Google Sheets save, Learning_Log, HEIC support, reset fixes, and dimension save fix

## Included data folder
['High_Style_Deco_Master_Dataset_V5_AI_Ready_Verification.xlsx']

## GitHub deployment
Upload the full contents of this folder to GitHub, including the `data` folder and V5 Excel file.

Minimum files/folders:
- app.py
- requirements.txt
- README.md
- data/High_Style_Deco_Master_Dataset_V5_AI_Ready_Verification.xlsx
