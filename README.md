# High Style AI – Task 3.3.5: Cloudinary URL Generation Fix

This hotfix addresses the crash that occurred after loading a draft and generating through the High Style Brain.

## Cause addressed

Earlier versions downloaded every restored full-resolution Cloudinary photo into Streamlit memory and then created additional image copies for AI analysis. Several large photos could overwhelm the Streamlit process while the V5 Brain was also loaded.

## What changed

- Restored draft photos remain lightweight Cloudinary URL references.
- OpenAI analyzes the public HTTPS Cloudinary URLs directly.
- No restored image bytes are downloaded into Streamlit memory.
- No base64 copy is created for restored draft photos.
- No Pillow or native image library is used for restored photos.
- Vision analysis is capped at four photos per generation.
- Existing Cloudinary URLs are reused for final approval and draft saving.

## Why the app logged out

Streamlit login state is stored in the running process. When the process crashed, the session state was lost and the login page appeared again. Fixing the crash prevents that forced logout.

## Upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Then reboot the Streamlit app.
