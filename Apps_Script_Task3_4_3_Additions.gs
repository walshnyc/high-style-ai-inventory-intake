/*
TASK 3.4.3 — APPS SCRIPT ADDITIONS

1. Add this routing block inside doPost(e), before the normal inventory save:

if (action === "Learning_Rules") {
  return learningRules(data);
}

2. Paste the functions below at the bottom of Code.gs.
*/


function getOrCreateLearnedRulesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("Learned_Rules");

  const headers = [
    "Rule_ID",
    "Area",
    "Rule",
    "Category",
    "Priority",
    "Times_Reinforced",
    "Last_Used",
    "Active"
  ];

  if (!sheet) {
    sheet = ss.insertSheet("Learned_Rules");
    sheet
      .getRange(1, 1, 1, headers.length)
      .setValues([headers]);
  }

  return sheet;
}


function learningRules(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const category = String(data.Category || "").trim().toLowerCase();
  const limit = Math.max(
    1,
    Math.min(Number(data.Limit || 40), 100)
  );

  const rules = [];

  // A. Structured persistent rules.
  const rulesSheet = getOrCreateLearnedRulesSheet_();
  const rulesValues = rulesSheet.getDataRange().getValues();

  if (rulesValues.length >= 2) {
    const headers = rulesValues[0];

    for (let rowIndex = 1; rowIndex < rulesValues.length; rowIndex++) {
      const row = rulesValues[rowIndex];
      const rule = {};

      headers.forEach((header, columnIndex) => {
        rule[header] = row[columnIndex];
      });

      const active = String(rule.Active || "Yes").trim().toLowerCase();
      const ruleCategory = String(
        rule.Category || "All"
      ).trim().toLowerCase();

      if (!["yes", "true", "1", "active"].includes(active)) {
        continue;
      }

      if (
        category
        && !["", "all", category].includes(ruleCategory)
      ) {
        continue;
      }

      if (String(rule.Rule || "").trim()) {
        rules.push(rule);
      }
    }
  }

  // B. Recent reinforced feedback from Learning_Log.
  // This makes existing feedback useful even before Learned_Rules is populated.
  const learningSheet = ss.getSheetByName("Learning_Log");

  if (learningSheet && learningSheet.getLastRow() >= 2) {
    const values = learningSheet.getDataRange().getValues();
    const headers = values[0];

    const titleFeedbackColumn = headers.indexOf("Title_Feedback");
    const descriptionFeedbackColumn = headers.indexOf(
      "Description_Feedback"
    );
    const priceFeedbackColumn = headers.indexOf("Price_Feedback");
    const referenceFeedbackColumn = headers.indexOf(
      "Reference_Feedback"
    );
    const notesColumn = headers.indexOf("Learning_Notes");

    const feedbackColumns = [
      ["Title", titleFeedbackColumn],
      ["Description", descriptionFeedbackColumn],
      ["Price", priceFeedbackColumn],
      ["Reference", referenceFeedbackColumn],
      ["General", notesColumn]
    ];

    const startRow = Math.max(1, values.length - 75);
    const seen = new Set(
      rules.map(rule => String(rule.Rule || "").trim().toLowerCase())
    );

    for (
      let rowIndex = values.length - 1;
      rowIndex >= startRow && rules.length < limit;
      rowIndex--
    ) {
      feedbackColumns.forEach(([area, columnIndex]) => {
        if (columnIndex < 0 || rules.length >= limit) {
          return;
        }

        const text = String(
          values[rowIndex][columnIndex] || ""
        ).trim();

        const normalized = text.toLowerCase();

        if (
          text.length >= 8
          && normalized !== "none"
          && !seen.has(normalized)
        ) {
          rules.push({
            Rule_ID: "LOG-" + rowIndex + "-" + area,
            Area: area,
            Rule: text,
            Category: "All",
            Priority: "Medium",
            Times_Reinforced: 1,
            Last_Used: "",
            Active: "Yes"
          });

          seen.add(normalized);
        }
      });
    }
  }

  const priorityOrder = {
    Critical: 0,
    High: 1,
    Medium: 2,
    Low: 3
  };

  rules.sort((a, b) => {
    const priorityDifference =
      (priorityOrder[String(a.Priority || "Medium")] ?? 2)
      - (priorityOrder[String(b.Priority || "Medium")] ?? 2);

    if (priorityDifference !== 0) {
      return priorityDifference;
    }

    return Number(b.Times_Reinforced || 0)
      - Number(a.Times_Reinforced || 0);
  });

  return jsonResponse({
    result: "success",
    rules: rules.slice(0, limit)
  });
}
