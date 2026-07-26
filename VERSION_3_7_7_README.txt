HIGH STYLE AI — VERSION 3.7.7
CANONICAL APPROVED UPDATES

This frontend accompanies Backend 3.6.1.

Approved-item updates consistently reuse the approved Item_ID for the inventory
save, learning log, and local editor state.

The backend resolves the final canonical ID from Source_Draft_ID and updates the
existing Master_Inventory and Shoot List rows rather than appending new rows.

DEPLOYMENT ORDER

1. Install and deploy Backend 3.6.1.
2. Upload this frontend ZIP to GitHub.
3. Replace matching files and commit.
4. Allow Streamlit to redeploy.
