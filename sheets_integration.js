/**
 * Google Apps Script for Mutual Fund Portfolio Integration
 *
 * SETUP INSTRUCTIONS:
 * 1. Open your Google Sheet
 * 2. Go to Extensions > Apps Script
 * 3. Copy this entire code and paste it
 * 4. Save and authorize the script
 * 5. Refresh your sheet - you'll see a new "MF Portfolio" menu
 *
 * USAGE:
 * - Use the menu to fetch latest NAV, calculate portfolio value, etc.
 * - Set up your portfolio in the format shown below
 */

// Configuration
const MFAPI_BASE_URL = 'https://api.mfapi.in';

/**
 * Creates custom menu when spreadsheet opens
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('MF Portfolio')
    .addItem('Fetch Latest NAVs', 'fetchLatestNAVs')
    .addItem('Calculate Portfolio Value', 'calculatePortfolioValue')
    .addItem('Calculate Capital Gains', 'calculateCapitalGains')
    .addSeparator()
    .addItem('Setup Portfolio Sheet', 'setupPortfolioSheet')
    .addItem('Setup Transactions Sheet', 'setupTransactionsSheet')
    .addToUi();
}

/**
 * Fetch NAV for a specific scheme code
 */
function MFNAV(schemeCode) {
  if (!schemeCode) return 'Error: No scheme code';

  try {
    const url = `${MFAPI_BASE_URL}/mf/${schemeCode}`;
    const response = UrlFetchApp.fetch(url);
    const data = JSON.parse(response.getContentText());

    if (data && data.data && data.data.length > 0) {
      return parseFloat(data.data[0].nav);
    }

    return 'Error: No data';
  } catch (e) {
    return 'Error: ' + e.message;
  }
}

/**
 * Fetch NAV date for a specific scheme code
 */
function MFNAVDATE(schemeCode) {
  if (!schemeCode) return 'Error: No scheme code';

  try {
    const url = `${MFAPI_BASE_URL}/mf/${schemeCode}`;
    const response = UrlFetchApp.fetch(url);
    const data = JSON.parse(response.getContentText());

    if (data && data.data && data.data.length > 0) {
      return data.data[0].date;
    }

    return 'Error: No data';
  } catch (e) {
    return 'Error: ' + e.message;
  }
}

/**
 * Search for scheme by name
 */
function searchScheme(query) {
  try {
    const url = `${MFAPI_BASE_URL}/mf`;
    const response = UrlFetchApp.fetch(url);
    const schemes = JSON.parse(response.getContentText());

    const results = schemes.filter(s =>
      s.schemeName.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);

    return results;
  } catch (e) {
    Logger.log('Error searching: ' + e.message);
    return [];
  }
}

/**
 * Fetch latest NAVs for all schemes in portfolio
 */
function fetchLatestNAVs() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Portfolio');

  if (!sheet) {
    SpreadsheetApp.getUi().alert('Portfolio sheet not found! Use "Setup Portfolio Sheet" first.');
    return;
  }

  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert('No data in Portfolio sheet!');
    return;
  }

  // Assuming columns: Scheme Code (A), Scheme Name (B), Units (C), Avg NAV (D), Current NAV (E), Current Value (F)
  const schemeCodeCol = 1;
  const currentNAVCol = 5;
  const currentValueCol = 6;
  const unitsCol = 3;

  SpreadsheetApp.getActiveSpreadsheet().toast('Fetching latest NAVs...', 'Please wait');

  for (let row = 2; row <= lastRow; row++) {
    const schemeCode = sheet.getRange(row, schemeCodeCol).getValue();

    if (schemeCode) {
      try {
        const nav = MFNAV(schemeCode);
        sheet.getRange(row, currentNAVCol).setValue(nav);

        // Calculate current value
        const units = sheet.getRange(row, unitsCol).getValue();
        if (typeof nav === 'number' && units) {
          sheet.getRange(row, currentValueCol).setValue(units * nav);
        }

        SpreadsheetApp.flush();
        Utilities.sleep(500); // Rate limiting
      } catch (e) {
        Logger.log(`Error fetching NAV for ${schemeCode}: ${e.message}`);
      }
    }
  }

  SpreadsheetApp.getActiveSpreadsheet().toast('NAVs updated successfully!', 'Done', 3);
}

/**
 * Calculate total portfolio value and gains
 */
function calculatePortfolioValue() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Portfolio');

  if (!sheet) {
    SpreadsheetApp.getUi().alert('Portfolio sheet not found!');
    return;
  }

  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert('No data in Portfolio sheet!');
    return;
  }

  let totalInvested = 0;
  let totalCurrent = 0;

  // Calculate for each row
  for (let row = 2; row <= lastRow; row++) {
    const units = sheet.getRange(row, 3).getValue();
    const avgNAV = sheet.getRange(row, 4).getValue();
    const currentNAV = sheet.getRange(row, 5).getValue();

    if (units && avgNAV && currentNAV) {
      const invested = units * avgNAV;
      const current = units * currentNAV;
      const gain = current - invested;
      const gainPct = (gain / invested * 100).toFixed(2);

      totalInvested += invested;
      totalCurrent += current;

      // Update calculated columns
      sheet.getRange(row, 6).setValue(current); // Current Value
      sheet.getRange(row, 7).setValue(gain); // Gain/Loss
      sheet.getRange(row, 8).setValue(gainPct + '%'); // Gain %
    }
  }

  const totalGain = totalCurrent - totalInvested;
  const totalGainPct = totalInvested > 0 ? (totalGain / totalInvested * 100).toFixed(2) : 0;

  // Show summary
  const message = `Portfolio Summary:\n\n` +
    `Total Invested: Rs.${totalInvested.toFixed(2)}\n` +
    `Current Value: Rs.${totalCurrent.toFixed(2)}\n` +
    `Total Gain/Loss: Rs.${totalGain.toFixed(2)} (${totalGainPct}%)`;

  SpreadsheetApp.getUi().alert('Portfolio Calculated', message, SpreadsheetApp.getUi().ButtonSet.OK);
}

/**
 * Calculate capital gains from transactions (FIFO method)
 */
function calculateCapitalGains() {
  const txnSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Transactions');

  if (!txnSheet) {
    SpreadsheetApp.getUi().alert('Transactions sheet not found! Use "Setup Transactions Sheet" first.');
    return;
  }

  const lastRow = txnSheet.getLastRow();
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert('No transactions found!');
    return;
  }

  // Get all transactions
  const data = txnSheet.getRange(2, 1, lastRow - 1, 6).getValues();

  // Group by scheme
  const schemes = {};

  data.forEach(row => {
    const [date, schemeCode, schemeName, type, units, nav] = row;

    if (!schemeCode) return;

    if (!schemes[schemeCode]) {
      schemes[schemeCode] = {
        name: schemeName,
        buys: [],
        sells: []
      };
    }

    const transaction = { date, units, nav };

    if (type === 'BUY') {
      schemes[schemeCode].buys.push(transaction);
    } else if (type === 'SELL') {
      schemes[schemeCode].sells.push(transaction);
    }
  });

  // Calculate gains using FIFO
  let totalSTCG = 0;
  let totalLTCG = 0;
  const gainsDetails = [];

  for (const [code, data] of Object.entries(schemes)) {
    const buyQueue = [...data.buys];

    data.sells.forEach(sell => {
      let unitsToSell = sell.units;

      while (unitsToSell > 0 && buyQueue.length > 0) {
        const buy = buyQueue[0];
        const unitsFromBuy = Math.min(unitsToSell, buy.units);

        // Calculate holding period
        const buyDate = new Date(buy.date);
        const sellDate = new Date(sell.date);
        const holdingDays = Math.floor((sellDate - buyDate) / (1000 * 60 * 60 * 24));

        // Calculate gain
        const purchaseAmount = unitsFromBuy * buy.nav;
        const saleAmount = unitsFromBuy * sell.nav;
        const gain = saleAmount - purchaseAmount;

        // Determine type (assuming equity - 1 year)
        const isLTCG = holdingDays >= 365;

        if (isLTCG) {
          totalLTCG += gain;
        } else {
          totalSTCG += gain;
        }

        gainsDetails.push({
          scheme: data.name,
          saleDate: sell.date,
          units: unitsFromBuy,
          purchaseAmt: purchaseAmount,
          saleAmt: saleAmount,
          gain: gain,
          type: isLTCG ? 'LTCG' : 'STCG'
        });

        unitsToSell -= unitsFromBuy;
        buy.units -= unitsFromBuy;

        if (buy.units <= 0) {
          buyQueue.shift();
        }
      }
    });
  }

  // Create or update Capital Gains sheet
  let gainsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Capital Gains');
  if (!gainsSheet) {
    gainsSheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet('Capital Gains');
  } else {
    gainsSheet.clear();
  }

  // Headers
  gainsSheet.getRange(1, 1, 1, 7).setValues([[
    'Sale Date', 'Scheme', 'Units', 'Purchase Amount', 'Sale Amount', 'Gain/Loss', 'Type'
  ]]).setFontWeight('bold').setBackground('#667eea').setFontColor('white');

  // Data
  if (gainsDetails.length > 0) {
    const outputData = gainsDetails.map(g => [
      g.saleDate,
      g.scheme,
      g.units,
      g.purchaseAmt,
      g.saleAmt,
      g.gain,
      g.type
    ]);

    gainsSheet.getRange(2, 1, outputData.length, 7).setValues(outputData);
  }

  // Summary
  const message = `Capital Gains Summary:\n\n` +
    `Short Term Capital Gains (STCG): Rs.${totalSTCG.toFixed(2)}\n` +
    `Long Term Capital Gains (LTCG): Rs.${totalLTCG.toFixed(2)}\n` +
    `Total Capital Gains: Rs.${(totalSTCG + totalLTCG).toFixed(2)}`;

  SpreadsheetApp.getUi().alert('Capital Gains Calculated', message, SpreadsheetApp.getUi().ButtonSet.OK);
}

/**
 * Setup Portfolio sheet with proper structure
 */
function setupPortfolioSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Portfolio');

  if (!sheet) {
    sheet = ss.insertSheet('Portfolio');
  }

  sheet.clear();

  // Headers
  const headers = [
    'Scheme Code', 'Scheme Name', 'Units', 'Avg NAV',
    'Current NAV', 'Current Value', 'Gain/Loss', 'Gain %'
  ];

  sheet.getRange(1, 1, 1, headers.length)
    .setValues([headers])
    .setFontWeight('bold')
    .setBackground('#667eea')
    .setFontColor('white');

  // Example data
  sheet.getRange(2, 1, 1, 4).setValues([['119551', 'HDFC Equity Fund', 100, 50]]);

  // Formulas for row 2 (user can copy down)
  sheet.getRange(2, 5).setFormula('=MFNAV(A2)'); // Current NAV
  sheet.getRange(2, 6).setFormula('=C2*E2'); // Current Value
  sheet.getRange(2, 7).setFormula('=F2-(C2*D2)'); // Gain/Loss
  sheet.getRange(2, 8).setFormula('=IF(C2*D2>0, (G2/(C2*D2)*100)&"%", "")'); // Gain %

  sheet.autoResizeColumns(1, headers.length);

  SpreadsheetApp.getActiveSpreadsheet().toast('Portfolio sheet setup complete!', 'Done', 3);
}

/**
 * Setup Transactions sheet with proper structure
 */
function setupTransactionsSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Transactions');

  if (!sheet) {
    sheet = ss.insertSheet('Transactions');
  }

  sheet.clear();

  // Headers
  const headers = ['Date', 'Scheme Code', 'Scheme Name', 'Type', 'Units', 'NAV'];

  sheet.getRange(1, 1, 1, headers.length)
    .setValues([headers])
    .setFontWeight('bold')
    .setBackground('#667eea')
    .setFontColor('white');

  // Example data
  sheet.getRange(2, 1, 2, 6).setValues([
    [new Date('2024-01-15'), '119551', 'HDFC Equity Fund', 'BUY', 50, 45.50],
    [new Date('2024-06-20'), '119551', 'HDFC Equity Fund', 'BUY', 50, 52.30]
  ]);

  // Data validation for Type column
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['BUY', 'SELL'], true)
    .build();
  sheet.getRange(2, 4, 1000, 1).setDataValidation(rule);

  sheet.autoResizeColumns(1, headers.length);

  SpreadsheetApp.getActiveSpreadsheet().toast('Transactions sheet setup complete!', 'Done', 3);
}
