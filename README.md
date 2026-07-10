# High Style AI – Task 3.3.3: Restore Draft Photos

This version keeps all Task 3.3.2 features and restores saved Cloudinary images when a user loads a draft.

## What changed

When the user clicks `Load This Draft`:

- All saved Cloudinary photo URLs are downloaded into the active Streamlit session.
- The photos appear in the main photo section.
- The restored photos are automatically passed into High Style Brain analysis and AI generation.
- The user does not need to re-upload the photos.
- New photos may still be added alongside the restored photos.
- Re-saving the draft preserves the existing Cloudinary URLs and uploads only newly added files.

## Streamlit limitation

The browser-native file uploader cannot be programmatically populated. Instead, restored photos are displayed immediately above the upload control and are treated internally exactly like uploaded files.

## Upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Do not upload `__pycache__`.

After committing, reboot the Streamlit app.
