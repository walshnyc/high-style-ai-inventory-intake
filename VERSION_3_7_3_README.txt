HIGH STYLE AI — VERSION 3.7.3
FRIENDLY SHOOT MONTH DISPLAY

FIXED

When reopening a saved draft, the Target monthly shoot list field could display
a raw timestamp such as:

2026-08-01T04:00:00.000Z

It now displays:

August 2026

CHANGES

- ISO timestamps are normalized into Month YYYY.
- YYYY-MM and YYYY-MM-DD saved values are also supported.
- The correct friendly month is automatically selected when reopening a draft.
- The lifecycle destination caption uses the same friendly month.
- Future saves preserve the friendly month label.

DEPLOYMENT

This is a frontend-only update.

Upload the contents of this ZIP to GitHub, replace matching files, commit, and
allow Streamlit to redeploy.

Continue using Backend Version 3.6.0.
