HIGH STYLE AI — VERSION 3.7.1
SAVED DRAFTS DASHBOARD FIX

PROBLEM FIXED

Save Draft successfully wrote the item to Google Sheets, but the app dashboard
only treated records whose Status was exactly "Draft" as active saved work.

Generated and edited drafts are saved as "Ready for Review", so they were
incorrectly hidden from the app even though they existed in Draft_Inventory.

CHANGES

- Draft, Ready for Review, Review, and Awaiting Review are now treated as
  active editable saved work.
- Ready for Review items appear in the Review tab.
- Approved and Completed items appear in the Approved tab.
- Reopening a saved review item restores the complete AI-generated information.
- Saving again continues updating the same Draft_Inventory, Master_Inventory,
  and monthly Shoot List rows.

DEPLOYMENT

This is a frontend-only update.

Upload the contents of this ZIP to the existing GitHub repository, replace
matching files, commit, and allow Streamlit to redeploy.

Continue using Backend Version 3.6.0. No Apps Script update is required.
