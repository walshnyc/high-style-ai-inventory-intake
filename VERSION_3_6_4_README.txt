HIGH STYLE AI — VERSION 3.6.4
COMPLETE DRAFT PERSISTENCE & AUTOMATIC DASHBOARD

CHANGES
1. Generated drafts now save automatically.
2. Draft_Inventory stores both original intake information and the complete AI output.
3. Opening a draft restores the generated title, description, suggested price,
   confidence, category, subcategory, style, period, country, maker, materials,
   dimensions, condition notes, price-tag text, SEO keywords, review notes,
   Brain context, learned rules, repair history, and retry history.
4. Save Draft continues to work for partial intake records.
5. If Save Draft is used after generation, it updates the same record with the complete AI draft.
6. The Saved Work dashboard loads automatically.
7. The Refresh button has been removed.
8. The dashboard cache is cleared after draft saves, generation, deletion, and approval.
9. Generated titles are shown on draft cards when available.

REQUIRES BACKEND 3.5.2
Install the included separate Apps Script backend update before relying on complete
generated-draft restoration. Older draft rows remain compatible.

FRONTEND INSTALLATION
Upload the contents of this ZIP to the existing GitHub repository and replace
matching files. Streamlit should redeploy automatically.
