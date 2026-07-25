HIGH STYLE AI — VERSION 3.7.0
STABILITY REFACTOR

FIXED

Version 3.7.0 fixes the StreamlitDuplicateElementId error that occurred after
generating a draft.

The app contained more than one button labeled:
- Save Draft
- Clear and Start New Entry

Streamlit can assign duplicate internal IDs when repeated widgets do not have
explicit keys. Every important action button now has its own stable key.

BUTTONS NOW KEYED SEPARATELY

- Generate Draft
- Initial Intake Save Draft
- Top Clear and Start New Entry
- Review Approve & Send to Google Sheet
- Review Save Draft
- Review Clear and Start New Entry

PRESERVED WORKFLOW

Backend 3.6.0 remains unchanged.

Saving a draft still creates or updates the same item in:
- Draft_Inventory
- Master_Inventory
- the designated monthly Shoot List

Approving later updates the same Item_ID rows and changes the status to
Approved without creating duplicate inventory or Shoot List entries.

DEPLOYMENT

This is a frontend-only update.

1. Unzip this package.
2. Upload all files inside it to the existing GitHub repository.
3. Replace matching files.
4. Commit the changes.
5. Let Streamlit redeploy.

Continue using Backend Version 3.6.0. No Apps Script update is required.
