function doPost(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const data = JSON.parse(e.postData.contents || "{}");
    const action = String(data.Action || "").trim();

    // Draft workflow actions
    if (action === "Draft_Save") {
      return saveDraft(data);
    }

    if (action === "Draft_List") {
      return listDrafts();
    }

    if (action === "Draft_List_All") {
      return draftListAll();
    }

    if (action === "Draft_Complete") {
      return draftComplete(data);
    }

    if (action === "Draft_Delete") {
      return draftDelete(data);
    }

    if (action === "Learning_Rules") {
      return learningRules(data);
    }

    // Learning log
    if (action === "Learning_Log") {
      appendRow(ss, "Learning_Log", [
        data.Timestamp || "",
        data.Item_ID || "",
        data.Original_AI_Title || "",
        data.Final_Approved_Title || "",
        data.Original_AI_Description || "",
        data.Final_Approved_Description || "",
        data.Original_AI_Price || "",
        data.Final_Approved_Price || "",
        data.Title_Feedback || "",
        data.Description_Feedback || "",
        data.Price_Feedback || "",
        data.Reference_Feedback || "",
        data.Learning_Notes || "",
        data.Retry_Count || "",
        data.Retry_History_JSON || "",
        data.Primary_Image_URL || "",
        data.High_Style_Brain_Matches_JSON || "",
        data.Submitted_By || "",
        data.Submitted_Date || "",
        data.Approved_By || "",
        data.Approved_Date || "",
        data.User_Role || "",
        data.Original_Title_Length || "",
        data.Final_Title_Length || "",
        data.Original_Description_Word_Count || "",
        data.Final_Description_Word_Count || "",
        data.Title_Change_Score || "",
        data.Description_Change_Score || "",
        data.Overall_Edit_Score || "",
        data.Audit_Trail_JSON || "",
        data.Source_Draft_ID || "",
        data.Shoot_List_Month || "",
        data.Shoot_List_Tab || "",
        data.Learned_Rules_Applied_JSON || "",
        data.House_Rules_Check_JSON || "",
        data.Rule_Repair_History_JSON || ""
      ]);

      return jsonResponse({
        result: "success",
        type: "learning_log"
      });
    }

    // Permanent Master Inventory + automatic monthly Shoot List.
    // This action is also the fallback for older app versions with no Action.
    if (action === "Inventory_Save" || action === "") {
      const masterSheet = getOrCreateMasterInventorySheet_(ss);
      const shootMonth = normalizeShootMonth_(data.Shoot_List_Month);
      const shootTabName = sanitizeSheetName_(
        data.Shoot_List_Tab || ("Shoot List - " + shootMonth)
      );
      const shootSheet = getOrCreateMonthlyShootSheet_(
        ss,
        shootTabName
      );

      const masterRecord = buildMasterInventoryRecord_(data);
      const masterResult = upsertObjectRow_(
        masterSheet,
        "Item_ID",
        data.Item_ID,
        masterRecord
      );

      const shootRecord = {
        "Item_ID": data.Item_ID || "",
        "Primary_Image": data.Primary_Image || "",
        "Primary_Image_URL": data.Primary_Image_URL || "",
        "Title": data.Title || "",
        "Dimensions": data.Dimensions || "",
        "Approved_Price_USD": data.Approved_Price_USD || "",
        "Description": data.Description || "",
        "Status": data.Status || "Awaiting Photography",
        "Category": data.Category || "",
        "Subcategory": data.Subcategory || "",
        "Shoot_List_Month": shootMonth,
        "Approved_By": data.Approved_By || "",
        "Approved_Date": data.Approved_Date || "",
        "Master_Inventory_ID": data.Item_ID || ""
      };

      const shootResult = upsertObjectRow_(
        shootSheet,
        "Item_ID",
        data.Item_ID,
        shootRecord
      );

      upsertObjectRow_(
        getOrCreateSheetWithHeaders_(
          ss,
          "Price_Tags",
          ["Item_ID", "Title", "Dimensions", "Approved_Price_USD"]
        ),
        "Item_ID",
        data.Item_ID,
        {
          "Item_ID": data.Item_ID || "",
          "Title": data.Title || "",
          "Dimensions": data.Dimensions || "",
          "Approved_Price_USD": data.Approved_Price_USD || ""
        }
      );

      upsertObjectRow_(
        getOrCreateSheetWithHeaders_(
          ss,
          "Listing_Copy",
          [
            "Item_ID",
            "Title",
            "Description",
            "SEO_Keywords",
            "Ready_For_1stDibs",
            "Ready_For_Chairish"
          ]
        ),
        "Item_ID",
        data.Item_ID,
        {
          "Item_ID": data.Item_ID || "",
          "Title": data.Title || "",
          "Description": data.Description || "",
          "SEO_Keywords": data.SEO_Keywords || "",
          "Ready_For_1stDibs": "Yes",
          "Ready_For_Chairish": "Yes"
        }
      );

      return jsonResponse({
        result: "success",
        type: "inventory_save",
        item_id: data.Item_ID || "",
        master_sheet: "Master_Inventory",
        master_operation: masterResult.operation,
        master_row: masterResult.row,
        shoot_list_month: shootMonth,
        shoot_list_sheet: shootTabName,
        shoot_list_operation: shootResult.operation,
        shoot_list_row: shootResult.row
      });
    }

    return jsonResponse({
      result: "error",
      message: "Unknown action: " + action
    });

  } catch (err) {
    return jsonResponse({
      result: "error",
      message: err && err.stack ? err.stack : String(err)
    });
  }
}


function appendRow(ss, sheetName, row) {
  let sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }

  sheet.appendRow(row);
}


function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}


function getDraftHeaders_() {
  return [
    "Draft_ID",
    "Status",
    "Submitted_By",
    "Submitted_Date",
    "Photo_URLs_JSON",
    "Primary_Image_URL",
    "Height_in",
    "Width_in",
    "Depth_in",
    "Diameter_in",
    "Body_Height_in",
    "Seat_Height_in",
    "Dimensions",
    "Known_Info",
    "Internal_Notes",
    "Target_Price",
    "Shoot_List_Month",
    "Last_Updated",
    "User_Role",
    "Completed_By",
    "Completed_Date",
    "Deleted_By",
    "Deleted_Date"
  ];
}


function getOrCreateDraftSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("Draft_Inventory");
  const requiredHeaders = getDraftHeaders_();

  if (!sheet) {
    sheet = ss.insertSheet("Draft_Inventory");
    sheet.getRange(1, 1, 1, requiredHeaders.length).setValues([requiredHeaders]);
    return sheet;
  }

  // Make sure older Draft_Inventory tabs gain any newly required columns.
  const lastColumn = Math.max(sheet.getLastColumn(), 1);
  let existingHeaders = sheet
    .getRange(1, 1, 1, lastColumn)
    .getValues()[0]
    .map(value => String(value || "").trim());

  if (existingHeaders.every(header => header === "")) {
    sheet.getRange(1, 1, 1, requiredHeaders.length).setValues([requiredHeaders]);
    return sheet;
  }

  const missingHeaders = requiredHeaders.filter(
    header => existingHeaders.indexOf(header) === -1
  );

  if (missingHeaders.length > 0) {
    const startColumn = existingHeaders.length + 1;
    sheet
      .getRange(1, startColumn, 1, missingHeaders.length)
      .setValues([missingHeaders]);
  }

  return sheet;
}


function getHeaderMap_(sheet) {
  const headers = sheet
    .getRange(1, 1, 1, sheet.getLastColumn())
    .getValues()[0]
    .map(value => String(value || "").trim());

  const map = {};
  headers.forEach((header, index) => {
    if (header) {
      map[header] = index;
    }
  });

  return {
    headers: headers,
    map: map
  };
}


function saveDraft(data) {
  const sheet = getOrCreateDraftSheet_();
  const headerInfo = getHeaderMap_(sheet);
  const headers = headerInfo.headers;
  const headerMap = headerInfo.map;
  const draftId = String(data.Draft_ID || "").trim();

  if (!draftId) {
    return jsonResponse({
      result: "error",
      message: "Draft_ID is required."
    });
  }

  const lastRow = sheet.getLastRow();
  const values = lastRow >= 2
    ? sheet.getRange(2, 1, lastRow - 1, headers.length).getValues()
    : [];

  let existingRowNumber = -1;

  for (let index = 0; index < values.length; index++) {
    if (String(values[index][headerMap["Draft_ID"]] || "").trim() === draftId) {
      existingRowNumber = index + 2;
      break;
    }
  }

  let rowData = new Array(headers.length).fill("");

  // Preserve existing completion/deletion metadata when updating a row.
  if (existingRowNumber !== -1) {
    rowData = sheet
      .getRange(existingRowNumber, 1, 1, headers.length)
      .getValues()[0];
  }

  const fieldValues = {
    Draft_ID: draftId,
    Status: data.Status || "Draft",
    Submitted_By: data.Submitted_By || "",
    Submitted_Date: data.Submitted_Date || "",
    Photo_URLs_JSON: data.Photo_URLs_JSON || "",
    Primary_Image_URL: data.Primary_Image_URL || "",
    Height_in: data.Height_in || "",
    Width_in: data.Width_in || "",
    Depth_in: data.Depth_in || "",
    Diameter_in: data.Diameter_in || "",
    Body_Height_in: data.Body_Height_in || "",
    Seat_Height_in: data.Seat_Height_in || "",
    Dimensions: data.Dimensions || "",
    Known_Info: data.Known_Info || "",
    Internal_Notes: data.Internal_Notes || "",
    Target_Price: data.Target_Price || "",
    Shoot_List_Month: data.Shoot_List_Month || "",
    Last_Updated: data.Last_Updated || new Date(),
    User_Role: data.User_Role || ""
  };

  Object.keys(fieldValues).forEach(field => {
    if (headerMap[field] !== undefined) {
      rowData[headerMap[field]] = fieldValues[field];
    }
  });

  if (existingRowNumber !== -1) {
    sheet
      .getRange(existingRowNumber, 1, 1, headers.length)
      .setValues([rowData]);

    return jsonResponse({
      result: "success",
      message: "Draft updated",
      draft_id: draftId
    });
  }

  sheet.appendRow(rowData);

  return jsonResponse({
    result: "success",
    message: "Draft saved",
    draft_id: draftId
  });
}


function listDrafts() {
  const drafts = getDraftObjects_()
    .filter(draft => String(draft.Status || "").toLowerCase() === "draft")
    .sort(sortDraftsNewestFirst_);

  return jsonResponse({
    result: "success",
    drafts: drafts
  });
}


function draftListAll() {
  const drafts = getDraftObjects_()
    .filter(draft => String(draft.Status || "").toLowerCase() !== "deleted")
    .sort(sortDraftsNewestFirst_);

  return jsonResponse({
    result: "success",
    drafts: drafts
  });
}


function getDraftObjects_() {
  const sheet = getOrCreateDraftSheet_();
  const lastRow = sheet.getLastRow();
  const lastColumn = sheet.getLastColumn();

  if (lastRow < 2 || lastColumn < 1) {
    return [];
  }

  const values = sheet
    .getRange(1, 1, lastRow, lastColumn)
    .getValues();

  const headers = values[0].map(value => String(value || "").trim());
  const draftIdColumn = headers.indexOf("Draft_ID");

  return values
    .slice(1)
    .filter(row => {
      if (draftIdColumn === -1) {
        return row.some(cell => String(cell || "").trim() !== "");
      }

      return String(row[draftIdColumn] || "").trim() !== "";
    })
    .map(row => {
      const draft = {};

      headers.forEach((header, index) => {
        if (header) {
          draft[header] = serializeSheetValue_(row[index]);
        }
      });

      return draft;
    });
}


function serializeSheetValue_(value) {
  if (value instanceof Date) {
    return value.toISOString();
  }

  return value;
}


function sortDraftsNewestFirst_(a, b) {
  const aTime = draftTimestamp_(a);
  const bTime = draftTimestamp_(b);
  return bTime - aTime;
}


function draftTimestamp_(draft) {
  const candidates = [
    draft.Last_Updated,
    draft.Completed_Date,
    draft.Submitted_Date
  ];

  for (let index = 0; index < candidates.length; index++) {
    const timestamp = new Date(candidates[index] || 0).getTime();

    if (!isNaN(timestamp) && timestamp > 0) {
      return timestamp;
    }
  }

  return 0;
}


function draftComplete(data) {
  const sheet = getOrCreateDraftSheet_();
  const headerInfo = getHeaderMap_(sheet);
  const headerMap = headerInfo.map;
  const draftId = String(data.Draft_ID || "").trim();

  if (!draftId) {
    return jsonResponse({
      result: "error",
      message: "Draft_ID is required."
    });
  }

  const lastRow = sheet.getLastRow();

  if (lastRow < 2) {
    return jsonResponse({
      result: "error",
      message: "Draft not found."
    });
  }

  const draftIds = sheet
    .getRange(2, headerMap["Draft_ID"] + 1, lastRow - 1, 1)
    .getValues();

  for (let index = 0; index < draftIds.length; index++) {
    if (String(draftIds[index][0] || "").trim() === draftId) {
      const rowNumber = index + 2;

      sheet
        .getRange(rowNumber, headerMap["Status"] + 1)
        .setValue("Completed");

      sheet
        .getRange(rowNumber, headerMap["Completed_By"] + 1)
        .setValue(data.Completed_By || "");

      sheet
        .getRange(rowNumber, headerMap["Completed_Date"] + 1)
        .setValue(data.Completed_Date || new Date());

      sheet
        .getRange(rowNumber, headerMap["Last_Updated"] + 1)
        .setValue(data.Completed_Date || new Date());

      return jsonResponse({
        result: "success",
        message: "Draft completed.",
        draft_id: draftId
      });
    }
  }

  return jsonResponse({
    result: "error",
    message: "Draft not found."
  });
}


function draftDelete(data) {
  const sheet = getOrCreateDraftSheet_();
  const headerInfo = getHeaderMap_(sheet);
  const headerMap = headerInfo.map;
  const draftId = String(data.Draft_ID || "").trim();

  if (!draftId) {
    return jsonResponse({
      result: "error",
      message: "Draft_ID is required."
    });
  }

  const lastRow = sheet.getLastRow();

  if (lastRow < 2) {
    return jsonResponse({
      result: "error",
      message: "Draft not found."
    });
  }

  const draftIds = sheet
    .getRange(2, headerMap["Draft_ID"] + 1, lastRow - 1, 1)
    .getValues();

  for (let index = 0; index < draftIds.length; index++) {
    if (String(draftIds[index][0] || "").trim() === draftId) {
      const rowNumber = index + 2;

      // Audit-safe delete: keep the row but remove it from dashboards.
      sheet
        .getRange(rowNumber, headerMap["Status"] + 1)
        .setValue("Deleted");

      sheet
        .getRange(rowNumber, headerMap["Deleted_By"] + 1)
        .setValue(data.Deleted_By || "");

      sheet
        .getRange(rowNumber, headerMap["Deleted_Date"] + 1)
        .setValue(data.Deleted_Date || new Date());

      sheet
        .getRange(rowNumber, headerMap["Last_Updated"] + 1)
        .setValue(data.Deleted_Date || new Date());

      return jsonResponse({
        result: "success",
        message: "Draft deleted.",
        draft_id: draftId
      });
    }
  }

  return jsonResponse({
    result: "error",
    message: "Draft not found."
  });
}

/* ================================================================
   TASK 3.4.4 — MASTER INVENTORY + MONTHLY SHOOT LISTS
   ================================================================ */

function getMasterInventoryHeaders_() {
  return [
    "Item_ID",
    "Status",
    "Shoot_List_Month",
    "Shoot_List_Tab",
    "Primary_Image",
    "Primary_Image_URL",
    "Additional_Images",
    "AI_Confidence",
    "Title",
    "Description",
    "Dimensions",
    "Height_in",
    "Width_in",
    "Depth_in",
    "Diameter_in",
    "Body_Height_in",
    "Seat_Height_in",
    "Suggested_Price_USD",
    "Approved_Price_USD",
    "Category",
    "Subcategory",
    "Style",
    "Period",
    "Country",
    "Designer_or_Maker",
    "Materials",
    "Condition_Notes",
    "Internal_Notes",
    "Ready_For_Photos",
    "Ready_For_Publishing",
    "Created_Date",
    "Last_Updated",
    "SEO_Keywords",
    "Submitted_By",
    "Submitted_Date",
    "Approved_By",
    "Approved_Date",
    "User_Role",
    "Source_Draft_ID",
    "Retry_Count",
    "Original_AI_Title",
    "Original_AI_Description",
    "Original_AI_Price",
    "Final_Title_Length",
    "Final_Description_Word_Count",
    "Title_Change_Score",
    "Description_Change_Score",
    "Overall_Edit_Score"
  ];
}


function getMonthlyShootHeaders_() {
  return [
    "Item_ID",
    "Primary_Image",
    "Primary_Image_URL",
    "Title",
    "Dimensions",
    "Approved_Price_USD",
    "Description",
    "Status",
    "Category",
    "Subcategory",
    "Shoot_List_Month",
    "Approved_By",
    "Approved_Date",
    "Master_Inventory_ID"
  ];
}


function getOrCreateSheetWithHeaders_(ss, sheetName, requiredHeaders) {
  let sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }

  const lastColumn = Math.max(sheet.getLastColumn(), 1);
  const lastRow = Math.max(sheet.getLastRow(), 1);
  let headers = sheet
    .getRange(1, 1, 1, lastColumn)
    .getValues()[0]
    .map(value => String(value || "").trim());

  if (lastRow === 1 && headers.every(header => header === "")) {
    sheet
      .getRange(1, 1, 1, requiredHeaders.length)
      .setValues([requiredHeaders]);
    headers = requiredHeaders.slice();
  } else {
    const missing = requiredHeaders.filter(
      header => headers.indexOf(header) === -1
    );

    if (missing.length > 0) {
      sheet
        .getRange(1, headers.length + 1, 1, missing.length)
        .setValues([missing]);
      headers = headers.concat(missing);
    }
  }

  sheet.setFrozenRows(1);
  return sheet;
}


function getOrCreateMasterInventorySheet_(ss) {
  const headers = getMasterInventoryHeaders_();
  const sheet = getOrCreateSheetWithHeaders_(
    ss,
    "Master_Inventory",
    headers
  );

  // One-time safe migration from the former Intake_Master tab.
  const legacy = ss.getSheetByName("Intake_Master");

  if (
    legacy
    && sheet.getLastRow() <= 1
    && legacy.getLastRow() > 1
  ) {
    const legacyValues = legacy.getDataRange().getValues();
    const legacyHeaders = legacyValues[0].map(
      value => String(value || "").trim()
    );
    const targetHeaders = sheet
      .getRange(1, 1, 1, sheet.getLastColumn())
      .getValues()[0]
      .map(value => String(value || "").trim());

    const outputRows = [];

    for (let rowIndex = 1; rowIndex < legacyValues.length; rowIndex++) {
      const source = {};
      legacyHeaders.forEach((header, columnIndex) => {
        if (header) {
          source[header] = legacyValues[rowIndex][columnIndex];
        }
      });

      if (!String(source.Item_ID || "").trim()) {
        continue;
      }

      outputRows.push(
        targetHeaders.map(header => source[header] || "")
      );
    }

    if (outputRows.length > 0) {
      sheet
        .getRange(2, 1, outputRows.length, targetHeaders.length)
        .setValues(outputRows);
    }
  }

  return sheet;
}


function getOrCreateMonthlyShootSheet_(ss, sheetName) {
  const sheet = getOrCreateSheetWithHeaders_(
    ss,
    sheetName,
    getMonthlyShootHeaders_()
  );

  sheet.setFrozenRows(1);
  return sheet;
}


function sanitizeSheetName_(value) {
  let name = String(value || "").trim();
  name = name.replace(/[\\\/\?\*\[\]\:]/g, "-");
  name = name.replace(/\s+/g, " ");
  name = name.substring(0, 100);
  return name || "Shoot List";
}


function normalizeShootMonth_(value) {
  const text = String(value || "").trim();

  if (text) {
    return text;
  }

  const now = new Date();
  const next = new Date(now.getFullYear(), now.getMonth() + 1, 1);

  return Utilities.formatDate(
    next,
    Session.getScriptTimeZone(),
    "MMMM yyyy"
  );
}


function buildMasterInventoryRecord_(data) {
  const record = {};
  getMasterInventoryHeaders_().forEach(header => {
    record[header] = data[header] || "";
  });

  record.Item_ID = data.Item_ID || "";
  record.Status = data.Status || "Awaiting Photography";
  record.Shoot_List_Month = normalizeShootMonth_(
    data.Shoot_List_Month
  );
  record.Shoot_List_Tab = sanitizeSheetName_(
    data.Shoot_List_Tab
    || ("Shoot List - " + record.Shoot_List_Month)
  );

  return record;
}


function upsertObjectRow_(sheet, keyHeader, keyValue, record) {
  const key = String(keyValue || "").trim();

  if (!key) {
    throw new Error(
      "Cannot save row because " + keyHeader + " is blank."
    );
  }

  const headerInfo = getHeaderMap_(sheet);
  const headers = headerInfo.headers;
  const keyColumnIndex = headerInfo.map[keyHeader];

  if (keyColumnIndex === undefined) {
    throw new Error(
      "Sheet " + sheet.getName()
      + " is missing key column " + keyHeader + "."
    );
  }

  let targetRow = sheet.getLastRow() + 1;
  let operation = "inserted";

  if (sheet.getLastRow() >= 2) {
    const keys = sheet
      .getRange(
        2,
        keyColumnIndex + 1,
        sheet.getLastRow() - 1,
        1
      )
      .getDisplayValues();

    for (let index = keys.length - 1; index >= 0; index--) {
      if (String(keys[index][0] || "").trim() === key) {
        targetRow = index + 2;
        operation = "updated";
        break;
      }
    }
  }

  const row = headers.map(header => {
    const value = record[header];
    return value === undefined || value === null ? "" : value;
  });

  sheet
    .getRange(targetRow, 1, 1, headers.length)
    .setValues([row]);

  return {
    operation: operation,
    row: targetRow
  };
}


/* ================================================================
   TASK 3.4.3 — PERSISTENT LEARNED RULE RETRIEVAL
   Included here so this file is the only Apps Script update required.
   ================================================================ */

function getOrCreateLearnedRulesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return getOrCreateSheetWithHeaders_(
    ss,
    "Learned_Rules",
    [
      "Rule_ID",
      "Area",
      "Rule",
      "Category",
      "Priority",
      "Times_Reinforced",
      "Last_Used",
      "Active"
    ]
  );
}


function learningRules(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const category = String(
    data.Category || ""
  ).trim().toLowerCase();

  const limit = Math.max(
    1,
    Math.min(Number(data.Limit || 40), 100)
  );

  const rules = [];
  const rulesSheet = getOrCreateLearnedRulesSheet_();
  const rulesValues = rulesSheet.getDataRange().getValues();

  if (rulesValues.length >= 2) {
    const headers = rulesValues[0];

    for (
      let rowIndex = 1;
      rowIndex < rulesValues.length;
      rowIndex++
    ) {
      const row = rulesValues[rowIndex];
      const rule = {};

      headers.forEach((header, columnIndex) => {
        rule[header] = row[columnIndex];
      });

      const active = String(
        rule.Active || "Yes"
      ).trim().toLowerCase();

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

  const learningSheet = ss.getSheetByName("Learning_Log");

  if (learningSheet && learningSheet.getLastRow() >= 2) {
    const values = learningSheet.getDataRange().getValues();
    const headers = values[0];

    const feedbackColumns = [
      ["Title", headers.indexOf("Title_Feedback")],
      [
        "Description",
        headers.indexOf("Description_Feedback")
      ],
      ["Price", headers.indexOf("Price_Feedback")],
      [
        "Reference",
        headers.indexOf("Reference_Feedback")
      ],
      ["General", headers.indexOf("Learning_Notes")]
    ];

    const startRow = Math.max(1, values.length - 75);
    const seen = new Set(
      rules.map(
        rule => String(rule.Rule || "").trim().toLowerCase()
      )
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
