HIGH STYLE AI — VERSION 3.6

THREE-STAGE WORKFLOW DASHBOARD

The Draft Dashboard is now organized into:

1. 🟠 Drafts
   - Missing information or not yet ready for generation.
   - Click Open Draft to continue the intake.

2. 🔵 Ready for Review
   - Complete intake records ready to generate, review, refine, and approve.
   - Click Open Draft to continue working.

3. 🟢 Approved
   - Successfully saved to Master_Inventory and the selected monthly Shoot List.
   - Kept as a searchable, read-only visual archive.

IMPORTANT STATUS FIX
Approved/Completed status now takes priority over intake completeness.
An approved item can no longer display as “In Progress” because an optional
draft field is missing.

APPROVAL BEHAVIOR
After a successful inventory save:
- the source draft is marked complete in Google Sheets;
- the local dashboard updates immediately;
- the thumbnail moves into the Approved tab.

No Apps Script change is required if Task 3.5 Draft_Complete and Draft_List_All
are already working in the current deployment.

INSTALLATION
Replace the current Streamlit app files with this package and reboot the app.
Continue using the current Task 3.5 Apps Script backend.
