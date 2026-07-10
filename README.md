# High Style AI – Task 3.3.4: Safe Draft Photo Processing

This hotfix addresses a Streamlit segmentation fault that occurred while generating from restored draft photos.

## What changed

- Restored Cloudinary images are no longer reopened or re-encoded with Pillow.
- Restored image bytes are passed directly to AI as data URLs.
- Restored images display directly from their Cloudinary URLs.
- Final approval reuses the existing Cloudinary primary image URL instead of uploading it again.
- HEIC native support only initializes for filenames ending in `.heic` or `.heif`.
- Cloudinary downloads are validated to ensure they are actual image responses.

## Features retained

- Draft save/list/load
- Restored draft photos
- Friendly draft cards
- Audit trail and learning metrics
- High Style Brain
- Employee login
- Hidden Google Sheet connection
- Feedback retry loop

## Upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Then reboot the Streamlit app.
