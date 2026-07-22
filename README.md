# High Style AI — Task 3.4.4

## Permanent Master Inventory + Automatic Monthly Shoot Lists

### New approval workflow

Every approved item is:

1. inserted or updated in `Master_Inventory`;
2. inserted or updated in the selected monthly tab, such as
   `Shoot List - August 2026`;
3. updated in `Price_Tags`;
4. updated in `Listing_Copy`;
5. recorded in `Learning_Log`.

The `Item_ID` is the permanent key. Re-saving the same item updates its existing
row instead of creating a duplicate.

### Monthly selection

The app defaults to the next calendar month and allows the current month plus
the following six months. A saved draft remembers its selected shoot month.

### Existing inventory

On the first approved save, the Apps Script safely creates `Master_Inventory`.
When the old `Intake_Master` exists and the new master is empty, its existing
rows are copied into the new master one time. The old tab is not deleted.

### Apps Script deployment

Use the included file:

`Code.gs_FULL_REPLACEMENT_Task3_4_4.gs`

This is a complete replacement for your current `Code.gs`. It already contains:

- draft actions;
- Learning_Log;
- Learning_Rules from Task 3.4.3;
- Master_Inventory;
- monthly shoot-list creation;
- Price_Tags and Listing_Copy updates.

After replacing Code.gs:

1. Save.
2. Deploy → Manage deployments.
3. Edit the web app.
4. Choose New version.
5. Deploy.

Your Streamlit secret URL does not need to change.

### GitHub deployment

Upload:

- `app.py`
- `requirements.txt`
- `README.md`
- the complete `data` folder

Then reboot the Streamlit application.
