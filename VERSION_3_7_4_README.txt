HIGH STYLE AI — VERSION 3.7.4
APPROVED ITEM EDITING

Approved items now have an Edit Approved Item button.

When opened:
- the complete approved record loads back into the app
- photos and generated information are restored
- the existing permanent Item_ID is preserved
- the item remains Approved

After editing:
- Save Draft updates the same Draft_Inventory working record
- Update Approved Item updates the same Master_Inventory row
- the designated monthly Shoot List row is updated
- no duplicate inventory or Shoot List rows are created

The original approval details are preserved, while Last_Updated,
Last_Edited_By, and Last_Edited_Date record the later correction.

DEPLOYMENT

This is a frontend-only update.

Upload the ZIP contents to GitHub, replace matching files, commit, and allow
Streamlit to redeploy.

Continue using Backend Version 3.6.0.
