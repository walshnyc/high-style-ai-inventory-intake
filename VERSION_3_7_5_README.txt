HIGH STYLE AI — VERSION 3.7.5
APPROVED ITEM RESTORE FIX

PROBLEM FIXED

After opening an approved item, clicking Clear and Start New Entry, and then
opening the approved item again, the app could raise:

KeyError: dims_inputs

The approved item could also reopen with only the basic intake information.

ROOT CAUSE

Clear and Start New Entry removed the dimensions session-state object.
Reopening an approved item restored the saved record, but did not always rebuild
that state object or reconstruct the full editable listing from the approved
Master Inventory fields.

CHANGES

- Reopening any saved item now rebuilds the complete dimensions state.
- Direct dims_inputs access now has a safe fallback.
- Approved items reconstruct the full editable listing from:
  Title, Description, prices, attribution, materials, dimensions, condition,
  SEO keywords, confidence, and other approved fields.
- Known information, internal notes, target price, and shoot month are restored.
- Clear and Start New Entry resets dimensions to a valid empty structure rather
  than leaving the state key missing.
- The approved record remains safely listed if the user clears without saving.
- Opening it again restores the complete saved approved information.

DEPLOYMENT

This is a frontend-only stability update.

Upload the ZIP contents to GitHub, replace matching files, commit, and allow
Streamlit to redeploy.

Continue using Backend Version 3.6.0.
