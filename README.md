# High Style AI – Task 3.4.3

## Enforced House Rules + Feedback Learning

This version adds a validation and learning layer on top of the Smart Brain.

### Enforced title rules

- Maximum 80 characters
- Must include the item type
- No place of origin
- No year, date, decade, circa, c., or ca.

### Enforced description rules

- Mandatory 190–220 words
- Begins with the period or style
- Prohibited condition phrases rejected
- Exact furniture condition sentence required
- Exact lighting rewiring sentence required

### Automatic repair

After generation, the app checks every mandatory rule. Failed drafts are
automatically rewritten and checked again up to two times before being shown.

### Persistent feedback learning

The app requests:

- active structured rules from the `Learned_Rules` tab
- recent useful feedback from `Learning_Log`

Those rules are inserted into both initial generation and feedback retry prompts.

### Approval protection

The Approve & Save button is disabled until every mandatory house rule passes.

## Upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- the complete data folder

The included Apps Script additions must also be added to Code.gs and deployed
as a new web-app version.
