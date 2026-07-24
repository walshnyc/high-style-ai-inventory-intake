HIGH STYLE AI — VERSION 3.6.1

NAMEERROR FIX

Version 3.6 accidentally removed the line that initializes `loaded_draft`
before the intake form is rendered. The dimensions fields then attempted to
use an undefined variable, causing:

NameError: loaded_draft is not defined

This version restores:

loaded_draft = st.session_state.get("loaded_draft", {})

The three-stage Draft / Ready for Review / Approved dashboard remains unchanged.

No Apps Script changes are required.

INSTALLATION
Replace the current Streamlit app files with this package and reboot the app.
