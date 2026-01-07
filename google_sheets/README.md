# Google Sheets Integration

Custom functions for fetching mutual fund data directly in Google Sheets using MFAPI.in.

## Installation

1. Open your Google Sheet
2. Go to **Extensions** > **Apps Script**
3. Delete any existing code in the editor
4. Copy the entire contents of `Code.gs` and paste it
5. Click the **Save** icon (💾) and name your project (e.g., "MF Dashboard")
6. Close the Apps Script editor

## Authorization

The first time you use any custom function:
1. Google will ask you to authorize the script
2. Click "Review Permissions"
3. Select your Google account
4. Click "Advanced" > "Go to [Your Project Name] (unsafe)"
5. Click "Allow"

## Available Functions

### MFNAV
Get the latest NAV for a mutual fund scheme.

**Syntax:** `=MFNAV(scheme_code)`

**Example:**
```
=MFNAV("119551")
```
Returns: `750.25` (latest NAV)

### MFNAVDATE
Get NAV for a specific date (or nearest previous date).

**Syntax:** `=MFNAVDATE(scheme_code, date)`

**Example:**
```
=MFNAVDATE("119551", "01-12-2023")
```
Returns: NAV as of December 1, 2023

### MFSCHEMENAME
Get the full name of a mutual fund scheme.

**Syntax:** `=MFSCHEMENAME(scheme_code)`

**Example:**
```
=MFSCHEMENAME("119551")
```
Returns: `"HDFC Top 100 Fund - Growth Option"`

### MFNAVLASTDATE
Get the date of the latest NAV.

**Syntax:** `=MFNAVLASTDATE(scheme_code)`

**Example:**
```
=MFNAVLASTDATE("119551")
```
Returns: `"03-01-2024"`

### MFXIRR
Calculate XIRR (Extended Internal Rate of Return) for your investments.

**Syntax:** `=MFXIRR(dates_range, amounts_range)`

**Example:**
```
=MFXIRR(A2:A10, B2:B10)
```
Where:
- Column A contains transaction dates
- Column B contains amounts (negative for investments, positive for redemptions/current value)

### MFABSRETURN
Calculate absolute return percentage.

**Syntax:** `=MFABSRETURN(invested, current_value)`

**Example:**
```
=MFABSRETURN(100000, 125000)
```
Returns: `25` (25% return)

### MFCAGR
Calculate CAGR (Compound Annual Growth Rate).

**Syntax:** `=MFCAGR(invested, current_value, years)`

**Example:**
```
=MFCAGR(100000, 150000, 3)
```
Returns: CAGR over 3 years

## Sample Portfolio Sheet

Create a portfolio tracker with these columns:

| Scheme Code | Scheme Name | Units | Purchase NAV | Invested | Current NAV | Current Value | Gain/Loss | Return % |
|-------------|-------------|-------|--------------|----------|-------------|---------------|-----------|----------|
| 119551 | =MFSCHEMENAME(A2) | 100 | 600 | =C2*D2 | =MFNAV(A2) | =C2*F2 | =G2-E2 | =H2/E2*100 |

## Custom Menu

After installation, you'll see a **MF Dashboard** menu with options:
- **Refresh All NAVs** - Force recalculation of all MFNAV functions
- **Show Help** - Display help dialog with function reference

## Tips

1. **Caching**: Google Sheets caches function results. Use "Refresh All NAVs" from the menu to force updates.

2. **Error Handling**: Functions return "ERROR: message" if something goes wrong. Common errors:
   - Invalid scheme code
   - Network issues
   - Missing parameters

3. **Rate Limits**: The MFAPI.in API is free but may have rate limits. Avoid making hundreds of calls simultaneously.

4. **Scheme Codes**: Find scheme codes at [MFAPI.in](https://www.mfapi.in/)

## Example Portfolio Template

```
| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Scheme Code | Scheme Name | Units | Avg Buy | Invested | Current NAV | Current Value | Gain/Loss | Return % |
| 119551 | =MFSCHEMENAME(A2) | 150 | 620 | =C2*D2 | =MFNAV(A2) | =C2*F2 | =G2-E2 | =H2/E2*100 |
| 118989 | =MFSCHEMENAME(A3) | 200 | 45 | =C3*D3 | =MFNAV(A3) | =C3*F3 | =G3-E3 | =H3/E3*100 |
| | | | TOTAL | =SUM(E2:E3) | | =SUM(G2:G3) | =SUM(H2:H3) | =I5/E5*100 |
```

## XIRR Calculation Example

For SIP investments:

| Date | Amount |
|------|--------|
| 01-01-2023 | -5000 |
| 01-02-2023 | -5000 |
| 01-03-2023 | -5000 |
| 03-01-2024 | 17500 |

Formula: `=MFXIRR(A2:A5, B2:B5)`

Note: Investments are negative, redemptions/current value are positive.

## Troubleshooting

**Functions not working:**
- Ensure you've authorized the script
- Check your internet connection
- Verify scheme codes are correct

**"Loading..." never finishes:**
- Try refreshing the sheet
- Check if the API is accessible: https://api.mfapi.in/mf/119551
- Use "Refresh All NAVs" from the menu

**XIRR returns error:**
- Ensure you have at least 2 transactions
- Check date formats are valid
- Verify amounts are numbers (not text)
- Investment amounts should be negative

## Support

For issues with:
- **Custom functions**: Check the Apps Script execution logs (Extensions > Apps Script > Executions)
- **MFAPI.in**: Visit https://www.mfapi.in/
- **Google Sheets API limits**: https://developers.google.com/apps-script/guides/services/quotas
