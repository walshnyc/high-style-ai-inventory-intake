HIGH STYLE AI — VERSION 3.5.3

GOOGLE SHEET SAVE VERIFICATION FIX

The previous frontend treated any HTTP 200 response as a successful save.
Google Apps Script can return HTTP 200 while the JSON body says:
{"result": "error", "message": "..."}

This version now:
- requires Apps Script to return result=success;
- displays the exact backend error when a save fails;
- confirms the Master Inventory and monthly Shoot List tab names when saved;
- verifies Learning_Log responses as well;
- does not mark the draft completed when inventory saving fails.

No Apps Script change is required yet.

INSTALLATION
Replace the current Streamlit app files with this package and reboot.
Then approve one test item. If the backend rejects the save, copy the full
red error shown by the app and use it to identify the exact Apps Script issue.
