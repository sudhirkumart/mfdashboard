/**
 * Mutual Fund Dashboard - Google Sheets Integration
 * Custom functions for fetching NAV data directly in Google Sheets
 *
 * Installation:
 * 1. Open Google Sheets
 * 2. Extensions > Apps Script
 * 3. Copy this code into Code.gs
 * 4. Save and authorize the script
 *
 * Usage in sheets:
 * =MFNAV("119551") - Get latest NAV for scheme
 * =MFNAVDATE("119551", "01-12-2023") - Get NAV on specific date
 * =MFSCHEMENAME("119551") - Get scheme name
 * =MFXIRR(A2:A10, B2:B10) - Calculate XIRR from dates and amounts
 */


/**
 * Fetch latest NAV for a mutual fund scheme
 *
 * @param {string} schemeCode The mutual fund scheme code
 * @return {number} Latest NAV value
 * @customfunction
 */
function MFNAV(schemeCode) {
  if (!schemeCode) {
    return "ERROR: Scheme code required";
  }

  try {
    var url = "https://api.mfapi.in/mf/" + schemeCode;
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var json = JSON.parse(response.getContentText());

    if (json.status === "SUCCESS" && json.data && json.data.length > 0) {
      return parseFloat(json.data[0].nav);
    } else {
      return "ERROR: Invalid scheme code";
    }
  } catch (e) {
    return "ERROR: " + e.message;
  }
}


/**
 * Fetch NAV for a specific date (or nearest previous date)
 *
 * @param {string} schemeCode The mutual fund scheme code
 * @param {string} date Date in DD-MM-YYYY format
 * @return {number} NAV value for the date
 * @customfunction
 */
function MFNAVDATE(schemeCode, date) {
  if (!schemeCode || !date) {
    return "ERROR: Scheme code and date required";
  }

  try {
    var url = "https://api.mfapi.in/mf/" + schemeCode;
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var json = JSON.parse(response.getContentText());

    if (json.status !== "SUCCESS") {
      return "ERROR: Invalid scheme code";
    }

    var targetDate = new Date(convertDateFormat(date));

    // Find NAV for date or nearest previous date
    for (var i = 0; i < json.data.length; i++) {
      var navDate = new Date(convertDateFormat(json.data[i].date));
      if (navDate <= targetDate) {
        return parseFloat(json.data[i].nav);
      }
    }

    return "ERROR: No NAV data for date";
  } catch (e) {
    return "ERROR: " + e.message;
  }
}


/**
 * Get scheme name for a scheme code
 *
 * @param {string} schemeCode The mutual fund scheme code
 * @return {string} Scheme name
 * @customfunction
 */
function MFSCHEMENAME(schemeCode) {
  if (!schemeCode) {
    return "ERROR: Scheme code required";
  }

  try {
    var url = "https://api.mfapi.in/mf/" + schemeCode;
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var json = JSON.parse(response.getContentText());

    if (json.status === "SUCCESS" && json.meta) {
      return json.meta.scheme_name;
    } else {
      return "ERROR: Invalid scheme code";
    }
  } catch (e) {
    return "ERROR: " + e.message;
  }
}


/**
 * Get latest NAV date for a scheme
 *
 * @param {string} schemeCode The mutual fund scheme code
 * @return {string} Latest NAV date
 * @customfunction
 */
function MFNAVLASTDATE(schemeCode) {
  if (!schemeCode) {
    return "ERROR: Scheme code required";
  }

  try {
    var url = "https://api.mfapi.in/mf/" + schemeCode;
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var json = JSON.parse(response.getContentText());

    if (json.status === "SUCCESS" && json.data && json.data.length > 0) {
      return json.data[0].date;
    } else {
      return "ERROR: Invalid scheme code";
    }
  } catch (e) {
    return "ERROR: " + e.message;
  }
}


/**
 * Calculate XIRR (Extended Internal Rate of Return)
 *
 * @param {range} dates Range of transaction dates
 * @param {range} amounts Range of transaction amounts (negative for investments, positive for returns)
 * @return {number} XIRR as percentage
 * @customfunction
 */
function MFXIRR(dates, amounts) {
  if (!dates || !amounts) {
    return "ERROR: Dates and amounts required";
  }

  // Convert ranges to arrays
  var dateArray = [];
  var amountArray = [];

  if (dates[0] && dates[0].length) {
    // 2D array
    for (var i = 0; i < dates.length; i++) {
      if (dates[i][0]) {
        dateArray.push(new Date(dates[i][0]));
      }
    }
  } else {
    // 1D array
    for (var i = 0; i < dates.length; i++) {
      if (dates[i]) {
        dateArray.push(new Date(dates[i]));
      }
    }
  }

  if (amounts[0] && amounts[0].length) {
    // 2D array
    for (var i = 0; i < amounts.length; i++) {
      if (amounts[i][0] !== null && amounts[i][0] !== "") {
        amountArray.push(parseFloat(amounts[i][0]));
      }
    }
  } else {
    // 1D array
    for (var i = 0; i < amounts.length; i++) {
      if (amounts[i] !== null && amounts[i] !== "") {
        amountArray.push(parseFloat(amounts[i]));
      }
    }
  }

  if (dateArray.length < 2 || amountArray.length < 2) {
    return "ERROR: At least 2 transactions required";
  }

  if (dateArray.length !== amountArray.length) {
    return "ERROR: Dates and amounts must have same length";
  }

  try {
    var xirr = calculateXIRR(dateArray, amountArray);
    return xirr * 100; // Return as percentage
  } catch (e) {
    return "ERROR: " + e.message;
  }
}


/**
 * Calculate absolute return percentage
 *
 * @param {number} invested Total invested amount
 * @param {number} currentValue Current portfolio value
 * @return {number} Absolute return as percentage
 * @customfunction
 */
function MFABSRETURN(invested, currentValue) {
  if (!invested || invested == 0) {
    return 0;
  }

  return ((currentValue - invested) / invested) * 100;
}


/**
 * Calculate CAGR (Compound Annual Growth Rate)
 *
 * @param {number} invested Initial investment
 * @param {number} currentValue Current value
 * @param {number} years Number of years
 * @return {number} CAGR as percentage
 * @customfunction
 */
function MFCAGR(invested, currentValue, years) {
  if (!invested || invested <= 0 || !currentValue || currentValue <= 0 || !years || years <= 0) {
    return "ERROR: Invalid inputs";
  }

  var cagr = (Math.pow(currentValue / invested, 1 / years) - 1) * 100;
  return cagr;
}


/**
 * Helper function to calculate XIRR using Newton-Raphson method
 */
function calculateXIRR(dates, amounts, guess) {
  guess = guess || 0.1;

  var maxIter = 100;
  var tolerance = 0.000001;

  var rate = guess;

  for (var i = 0; i < maxIter; i++) {
    var npv = 0;
    var dnpv = 0;

    var baseDate = dates[0];

    for (var j = 0; j < dates.length; j++) {
      var days = (dates[j] - baseDate) / (1000 * 60 * 60 * 24);
      var years = days / 365.0;

      var factor = Math.pow(1 + rate, years);
      npv += amounts[j] / factor;
      dnpv -= years * amounts[j] / (factor * (1 + rate));
    }

    if (Math.abs(npv) < tolerance) {
      return rate;
    }

    if (Math.abs(dnpv) < 0.0000000001) {
      throw new Error("XIRR calculation failed - derivative too small");
    }

    rate = rate - npv / dnpv;

    // Prevent extreme values
    if (rate < -0.99) rate = -0.99;
    if (rate > 10) rate = 10;
  }

  if (Math.abs(npv) > 0.01) {
    throw new Error("XIRR did not converge");
  }

  return rate;
}


/**
 * Helper function to convert date format from DD-MM-YYYY to YYYY-MM-DD
 */
function convertDateFormat(dateStr) {
  var parts = dateStr.split('-');
  if (parts.length === 3) {
    return parts[2] + '-' + parts[1] + '-' + parts[0];
  }
  return dateStr;
}


/**
 * Create a custom menu in Google Sheets
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('MF Dashboard')
      .addItem('Refresh All NAVs', 'refreshAllNAVs')
      .addItem('Show Help', 'showHelp')
      .addToUi();
}


/**
 * Refresh all MFNAV formulas in the active sheet
 */
function refreshAllNAVs() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getDataRange();
  var formulas = range.getFormulas();

  var count = 0;

  for (var i = 0; i < formulas.length; i++) {
    for (var j = 0; j < formulas[i].length; j++) {
      if (formulas[i][j].indexOf('MFNAV') !== -1) {
        // Force recalculation by adding and removing a space
        var cell = sheet.getRange(i + 1, j + 1);
        var formula = cell.getFormula();
        cell.setFormula(formula + " ");
        SpreadsheetApp.flush();
        cell.setFormula(formula);
        count++;
      }
    }
  }

  SpreadsheetApp.getUi().alert('Refreshed ' + count + ' NAV formulas');
}


/**
 * Show help dialog with function documentation
 */
function showHelp() {
  var html = HtmlService.createHtmlOutput(
    '<h2>MF Dashboard Functions</h2>' +
    '<p><b>=MFNAV("scheme_code")</b><br>Get latest NAV</p>' +
    '<p><b>=MFNAVDATE("scheme_code", "DD-MM-YYYY")</b><br>Get NAV on specific date</p>' +
    '<p><b>=MFSCHEMENAME("scheme_code")</b><br>Get scheme name</p>' +
    '<p><b>=MFNAVLASTDATE("scheme_code")</b><br>Get latest NAV date</p>' +
    '<p><b>=MFXIRR(dates, amounts)</b><br>Calculate XIRR</p>' +
    '<p><b>=MFABSRETURN(invested, current)</b><br>Calculate absolute return %</p>' +
    '<p><b>=MFCAGR(invested, current, years)</b><br>Calculate CAGR %</p>' +
    '<hr>' +
    '<p><b>Example:</b><br>=MFNAV("119551") returns latest NAV for HDFC Top 100 Fund</p>'
  ).setWidth(500).setHeight(400);

  SpreadsheetApp.getUi().showModalDialog(html, 'MF Dashboard Help');
}
