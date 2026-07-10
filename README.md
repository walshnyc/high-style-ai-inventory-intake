# High Style AI – Task 3.3.8: Advanced Draft Manager

This version keeps all Task 3.3.7 features and adds a more polished draft-management experience.

## Active Drafts

- Thumbnail preview
- Draft ID
- Employee
- Saved and last-updated dates
- Readiness status:
  - Needs Photos
  - Needs Info
  - In Progress
  - Ready to Generate
- Missing-information indicators
- Search
- Sort by newest, oldest, or readiness
- Continue Editing button
- Delete Draft button with confirmation

## Completed Drafts

- Searchable archive
- Sort by newest or oldest completion
- Completion employee and date
- Friendly photo/details card

## Apps Script actions required

Existing:

- Draft_Save
- Draft_List
- Draft_List_All
- Draft_Complete

New:

- Draft_Delete

`Draft_Delete` should find the matching `Draft_ID` in `Draft_Inventory` and delete that row, or mark it `Deleted` if you prefer an audit-safe archive.

## GitHub upload

Upload:

- app.py
- requirements.txt
- README.md
- data folder

Then reboot Streamlit.
