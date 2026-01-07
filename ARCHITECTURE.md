# MF Dashboard - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Web Dashboard│  │ CLI Terminal │  │ Google Sheets│             │
│  │ (Browser)    │  │ (Console)    │  │ (Spreadsheet)│             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                      │
└─────────┼──────────────────┼──────────────────┼──────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────┐       ┌────────────────────┐               │
│  │   web_app.py       │       │  portfolio_app.py  │               │
│  │  (Flask Server)    │       │  (CLI Interface)   │               │
│  └────────┬───────────┘       └────────┬───────────┘               │
│           │                             │                           │
│           └─────────────┬───────────────┘                           │
│                         │                                           │
│                         ▼                                           │
│           ┌─────────────────────────────┐                          │
│           │   portfolio_manager.py      │                          │
│           │  • Portfolio Management     │                          │
│           │  • Transaction Tracking     │                          │
│           │  • Capital Gains (FIFO)     │                          │
│           │  • Holdings Calculation     │                          │
│           └────────┬────────────────────┘                          │
│                    │                                                │
└────────────────────┼────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │           mfapi_fetcher.py                         │            │
│  │  • API Communication                               │            │
│  │  • Intelligent Caching                             │            │
│  │  • Scheme Search                                   │            │
│  │  • NAV Fetching                                    │            │
│  └────────┬───────────────────────────────────────────┘            │
│           │                                                         │
└───────────┼─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐                                               │
│  │   MFAPI.in       │                                               │
│  │ (External API)   │                                               │
│  │                  │                                               │
│  │ GET /mf          │  - All schemes                                │
│  │ GET /mf/{code}   │  - Scheme details + NAV history               │
│  └──────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │  portfolio.json  │         │    .mfcache/     │                 │
│  │                  │         │                  │                 │
│  │ • Transactions   │         │ • Cached NAVs    │                 │
│  │ • Persistent     │         │ • Scheme data    │                 │
│  │ • User data      │         │ • Temporary      │                 │
│  └──────────────────┘         └──────────────────┘                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Add Transaction Flow

```
User Input
    │
    ▼
┌─────────────────────┐
│ Search for Scheme   │──────► mfapi_fetcher.search_schemes()
└──────┬──────────────┘              │
       │                             ▼
       │                    ┌──────────────────┐
       │                    │ Check Cache      │
       │                    └────┬─────────────┘
       │                         │
       │                    ┌────▼────┐
       │                    │Valid?   │
       │                    └────┬────┘
       │                         │
       │            No ◄──────────┴──────────► Yes
       │             │                          │
       │             ▼                          ▼
       │    ┌──────────────────┐      ┌──────────────┐
       │    │ Fetch from API   │      │Return cached │
       │    └────┬─────────────┘      └──────────────┘
       │         │
       │         ▼
       │    ┌──────────────────┐
       │    │ Save to Cache    │
       │    └────┬─────────────┘
       │         │
       └─────────┴────────────► Select Scheme
                                      │
                                      ▼
                            Enter Transaction Details
                                      │
                                      ▼
                      portfolio_manager.add_transaction()
                                      │
                                      ▼
                             Save to portfolio.json
                                      │
                                      ▼
                                 Transaction Added!
```

### 2. Calculate Capital Gains Flow

```
User Request
    │
    ▼
Load Transactions from portfolio.json
    │
    ▼
┌────────────────────────────┐
│ Group by Scheme            │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ For each SELL transaction: │
└──────┬─────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Match with BUY using FIFO           │
│                                     │
│  BUY Queue: [Buy1, Buy2, Buy3]     │
│                                     │
│  For SELL of 50 units:              │
│    Take from Buy1 (oldest)          │
│    Calculate holding period         │
│    Calculate gain/loss              │
│    Classify STCG/LTCG               │
└──────┬──────────────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Aggregate Results:          │
│  • Total STCG               │
│  • Total LTCG               │
│  • Transaction details      │
└──────┬─────────────────────┘
       │
       ▼
Display Capital Gains Report
```

### 3. View Portfolio Flow

```
User Request
    │
    ▼
Load Transactions from portfolio.json
    │
    ▼
┌──────────────────────────────┐
│ Get Unique Scheme Codes      │
└──────┬───────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│ For each scheme:                      │
│   ├─► mfapi_fetcher.get_latest_nav() │
│   │            │                      │
│   │            ▼                      │
│   │   ┌──────────────┐              │
│   │   │ Check Cache  │              │
│   │   └──────┬───────┘              │
│   │          │                       │
│   │     ┌────▼────┐                 │
│   │     │ Valid?  │                 │
│   │     └────┬────┘                 │
│   │          │                       │
│   │    Yes ──┴── No                 │
│   │     │        │                   │
│   │     │        ▼                   │
│   │     │   Fetch from API           │
│   │     │        │                   │
│   │     │        ▼                   │
│   │     │   Save to Cache            │
│   │     │        │                   │
│   │     └────────┘                   │
│   │          │                       │
│   └──────────┘                       │
│              │                        │
└──────────────┼────────────────────────┘
               │
               ▼
┌────────────────────────────┐
│ Calculate for each holding:│
│  • Total units             │
│  • Average NAV             │
│  • Invested amount         │
│  • Current value           │
│  • Gain/Loss               │
│  • Gain %                  │
└──────┬─────────────────────┘
       │
       ▼
Display Portfolio Summary
```

## Component Interactions

### Portfolio Manager ↔ MFAPI Fetcher

```
PortfolioManager                    MFAPIFetcher
       │                                  │
       │  get_holdings(current_navs)     │
       │─────────────────────────────────►│
       │                                  │
       │  For each scheme_code:          │
       │  get_latest_nav(code)           │
       │─────────────────────────────────►│
       │                                  │
       │                                  │  Check cache
       │                                  │─────────►
       │                                  │
       │                                  │  Fetch if needed
       │                                  │─────────►
       │                                  │
       │  ◄──────────────────────────────│
       │  Return NAV data                │
       │                                  │
       │  Calculate holdings              │
       │────────►                         │
       │                                  │
```

### Web App Request Handling

```
Browser                 Flask App              Portfolio Manager
   │                        │                         │
   │  GET /api/portfolio    │                         │
   │───────────────────────►│                         │
   │                        │                         │
   │                        │  Load transactions      │
   │                        │────────────────────────►│
   │                        │                         │
   │                        │  Fetch current NAVs     │
   │                        │────────────────────────►│
   │                        │                         │
   │                        │  Calculate holdings     │
   │                        │────────────────────────►│
   │                        │                         │
   │                        │  ◄──────────────────────│
   │                        │  Return holdings data   │
   │                        │                         │
   │  ◄─────────────────────│                         │
   │  JSON Response         │                         │
   │                        │                         │
```

## Key Algorithms

### FIFO Capital Gains

```python
Algorithm: FIFO_Capital_Gains(transactions, is_equity)
    Input: List of transactions, fund type
    Output: List of capital gains

    1. Initialize:
        - buy_queue = empty queue
        - gains = empty list

    2. For each transaction in transactions:
        If transaction.type == 'BUY':
            Add to buy_queue

        If transaction.type == 'SELL':
            units_remaining = transaction.units

            While units_remaining > 0 AND buy_queue not empty:
                oldest_buy = buy_queue.first()

                units_to_match = min(units_remaining, oldest_buy.units)

                Calculate:
                    holding_days = sell_date - buy_date
                    purchase_amt = units_to_match * buy_nav
                    sale_amt = units_to_match * sell_nav
                    gain = sale_amt - purchase_amt

                Classify:
                    If is_equity:
                        type = LTCG if holding_days >= 365 else STCG
                    Else:
                        type = LTCG if holding_days >= 1095 else STCG

                Add to gains list

                Update:
                    units_remaining -= units_to_match
                    oldest_buy.units -= units_to_match

                If oldest_buy.units == 0:
                    Remove from buy_queue

    3. Return gains
```

### Cache Validation

```python
Algorithm: Get_With_Cache(endpoint, ttl)
    Input: API endpoint, time-to-live
    Output: Data from cache or API

    1. Generate cache_key from endpoint

    2. Check if cache file exists:
        If exists:
            file_age = current_time - file_modified_time

            If file_age < ttl:
                Read and return cached data
            Else:
                Cache expired, continue to step 3

    3. Fetch from API:
        response = HTTP_GET(endpoint)

    4. Save to cache:
        Write response to cache file
        Set file modified time

    5. Return response
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
├─────────────────────────────────────────┤
│ • HTML5 (dashboard.html)                │
│ • CSS3 (embedded styles)                │
│ • JavaScript (ES6+)                     │
│ • Chart.js 4.4.0 (visualizations)       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Application Layer               │
├─────────────────────────────────────────┤
│ • Python 3.8+                           │
│ • Flask 3.0+ (web framework)            │
│ • Custom CLI (portfolio_app.py)         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│          Business Logic                 │
├─────────────────────────────────────────┤
│ • PortfolioManager class                │
│ • Transaction, Holding, CapitalGain     │
│ • FIFO algorithm                        │
│ • Portfolio calculations                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│          Data Access Layer              │
├─────────────────────────────────────────┤
│ • MFAPIFetcher class                    │
│ • Requests library 2.31+                │
│ • File-based caching                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│            Data Storage                 │
├─────────────────────────────────────────┤
│ • JSON files (portfolio.json)           │
│ • File system cache (.mfcache/)         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         External Services               │
├─────────────────────────────────────────┤
│ • MFAPI.in REST API                     │
│ • HTTPS communication                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Integration Options               │
├─────────────────────────────────────────┤
│ • Google Apps Script                    │
│ • Google Sheets                         │
└─────────────────────────────────────────┘
```

## Security Considerations

```
┌─────────────────────────────────────────┐
│           Data Security                 │
├─────────────────────────────────────────┤
│ ✓ Local storage only                   │
│ ✓ No external database                 │
│ ✓ No user authentication needed        │
│ ✓ Portfolio data in JSON (readable)    │
│ ⚠ Run on localhost only (default)      │
│ ⚠ Backup portfolio.json regularly      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           API Security                  │
├─────────────────────────────────────────┤
│ ✓ HTTPS to MFAPI.in                    │
│ ✓ Read-only API access                 │
│ ✓ No API keys required                 │
│ ✓ Rate limiting via delays             │
│ ⚠ Dependent on external service        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Web Dashboard Security          │
├─────────────────────────────────────────┤
│ ⚠ Flask debug mode (dev only)          │
│ ⚠ No authentication (single user)      │
│ ⚠ Bind to localhost only               │
│ ! Not for production deployment         │
└─────────────────────────────────────────┘
```

## Scalability

### Current Limitations
- Single user design
- Local file storage
- Synchronous API calls
- In-memory processing

### Scaling Options
```
For Multiple Users:
    • Add database (SQLite/PostgreSQL)
    • Implement user authentication
    • Deploy on cloud server

For Better Performance:
    • Use async API calls
    • Implement Redis cache
    • Add database indexes
    • Optimize queries

For High Availability:
    • Deploy multiple instances
    • Load balancer
    • Database replication
    • CDN for static files
```

## Deployment Options

### Local (Current)
```
Users: 1
Storage: Local files
Network: Localhost
Pros: Simple, fast, no costs
Cons: Single machine only
```

### Cloud Deployment
```
Options:
    • Heroku (easy)
    • AWS EC2 (flexible)
    • Google Cloud Run (serverless)
    • DigitalOcean (VPS)

Requirements:
    • Add production WSGI server (gunicorn)
    • Environment variables for config
    • Database instead of JSON
    • HTTPS certificate
    • User authentication
```

## Performance Metrics

### Without Cache
```
Operation          | Time    | API Calls
-------------------|---------|----------
Search schemes     | 2-3s    | 1
Get scheme details | 0.3-0.5s| 1
Load portfolio (10)| 3-5s    | 11
Calculate gains    | <0.1s   | 0
```

### With Cache
```
Operation          | Time    | API Calls
-------------------|---------|----------
Search schemes     | 0.1s    | 0
Get scheme details | 0.01s   | 0
Load portfolio (10)| 0.1s    | 0
Calculate gains    | <0.1s   | 0

Speedup: 30-50x
```

---

**Architecture Version:** 1.0
**Last Updated:** January 2026
