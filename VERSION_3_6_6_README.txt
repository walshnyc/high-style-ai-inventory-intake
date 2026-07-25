HIGH STYLE AI — VERSION 3.6.6
UNIFIED INVENTORY LIFECYCLE

CORE WORKFLOW

Every saved item now exists immediately in:
- Draft_Inventory
- Master_Inventory
- the designated monthly Shoot List

The same Item_ID is retained throughout the item's lifecycle.

STATUS FLOW

Partial Save:
Draft

Generated / Edited Save:
Ready for Review

Approval:
Approved

WHAT THIS MEANS

- Employees may save after uploading only photos and partial information.
- The item still appears in Master_Inventory and the selected Shoot List.
- Generated AI information updates the same rows.
- Further edits and Save Draft update the same rows.
- Approve & Send updates those exact rows to Approved.
- Approval does not create a second Master Inventory or Shoot List row.
- Both drafts and approved items remain on the monthly Shoot List for the
  physical photo shoot.
- If the designated shoot month changes, Backend 3.6.0 moves the item to the
  new monthly Shoot List and removes its stale row from the previous month.

INSTALLATION

1. Install Backend 3.6.0 in Google Apps Script first.
2. Deploy it as a New version while keeping the existing web-app URL.
3. Upload this frontend ZIP's contents to the existing GitHub repository.
4. Replace matching files and commit.
5. Allow Streamlit to redeploy.

This frontend requires Backend 3.6.0.
