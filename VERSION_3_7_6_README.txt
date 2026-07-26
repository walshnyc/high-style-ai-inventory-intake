HIGH STYLE AI — VERSION 3.7.6
CLEAR APPROVED ITEM STATE FIX

PROBLEM FIXED

After opening an approved item and clicking Clear and Start New Entry, the app
could raise:

NameError: name 'inputs' is not defined

ROOT CAUSE

The defensive dimensions-state check added in Version 3.7.5 tested the variable
'inputs' before assigning it.

CHANGES

- 'inputs' is now always initialized from session state before validation.
- Both Clear and Start New Entry buttons rebuild a valid empty dimensions state.
- Approved editing flags and saved approved IDs are cleared before rerunning.
- Clearing an approved item no longer removes or alters the approved listing.
- Reopening the approved item continues restoring its saved information.

DEPLOYMENT

This is a frontend-only update.

1. Unzip this package.
2. Upload all files to the existing GitHub repository.
3. Replace matching files.
4. Commit.
5. Allow Streamlit to redeploy.

Continue using Backend Version 3.6.0.
