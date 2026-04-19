# Copilot Instructions — Finance SMS Logger API

## Architecture Overview

Flask REST API that parses bank SMS messages and logs transactions to Google Sheets. A companion Android app ([Finance-App-Android](https://github.com/Satyajit-2003/Finance-App-Android/)) sends SMS text to this API.

**Data flow**: Android app → `POST /api/v1/log-sms` → `sms_parser.get_transaction_info()` → `SheetManager` → Google Sheets (monthly tab in a shared workbook)

**Key components**:

- `app.py` — Flask app, `@app.before_request` auth middleware, all route handlers
- `config.py` — All configuration classes: `AppConfig`, `SheetConfig`, `TransactionTypes`, `Paths`, `ValidationRules`
- `sheet_manager.py` — Google Sheets API wrapper; creates/manages monthly sheets within one shared workbook
- `sms_parser/` — Standalone SMS parsing library; `engine.py` is the entry point, `utils.py` handles text normalization

## Developer Workflows

**Local development**:

```bash
python run.py          # Flask dev server (loads .env automatically)
python setup_dev.py    # Validate environment variables and credentials
```

**Production**:

```bash
python production.py   # Waitress WSGI server (not Flask dev server)
```

**Tests** (no pytest — uses a custom suite in `run_tests.py`):

```bash
python run_tests.py                 # All tests
python run_tests.py --quick         # Parser + auth only (no network)
python run_tests.py --local         # Against local server
python run_tests.py --api-only      # API endpoint tests only
python run_tests.py --extended      # Includes edge cases
```

## Configuration & Credentials

Environment variables are loaded from `.env` in dev; system env vars in production (Render).

**Required env vars**:

- `API_KEY`, `SECRET_KEY`, `GSHEET_SHARED_WORKBOOK_ID`
- `GOOGLE_PROJECT_ID`, `GOOGLE_PRIVATE_KEY_ID`, `GOOGLE_PRIVATE_KEY`, `GOOGLE_CLIENT_EMAIL`, `GOOGLE_CLIENT_ID`

Google credentials are **never stored as a file in production** — `config.get_google_credentials_info()` builds the credentials dict from individual env vars. See `credentials/google-credentials.json.example` for the expected shape.

## API Conventions

- All `/api/v1/*` routes require `X-API-KEY` header (enforced in `app.before_request`)
- `/health` is unauthenticated
- Every response follows `{"success": bool, "data": ..., "message": str}` or `{"success": false, "error": str, "message": str}`
- API prefix is `AppConfig.API_PREFIX` (`/api/v1`)

## Google Sheets Structure

Each month gets a dedicated tab named `{Month}-{Year}` (e.g., `April-2026`) inside one shared workbook. Tabs are created on-demand by `SheetManager._create_new_sheet()`.

Fixed column order (A–H) defined in `SheetConfig.HEADER_ROW`:
`Date | Description | Amount | Type (dropdown) | Account | Friend Split | Amount Borne (formula) | Notes`

- `Type` uses dropdown options from `TransactionTypes.get_dropdown_options()` with color-coded conditional formatting
- `Amount Borne` uses `SheetConfig.AMOUNT_BORNE_FORMULA` (calculates my share after friend split)

## SMS Parsing Pipeline

`sms_parser/utils.process_message(text)` normalizes raw SMS (lowercases, strips punctuation, normalizes "rs"/"INR" → "rs.", handles multi-word tokens via `COMBINED_WORDS` regex list in `constants.py`), then tokenizes into a word list. Each extractor (`get_transaction_type`, `get_transaction_amount`, `get_account`, `get_balance`, `extract_merchant_info`) operates on this token list.

When adding support for new bank/wallet SMS formats, check `constants.py` (`COMBINED_WORDS`, `WALLETS`, `UPI_KEYWORDS`) and `sms_parser/account.py` first.

## Memory & Caching

`SheetManager` holds two in-memory caches keyed by sheet name:

- `monthly_spends_cache`: aggregate spend stats per month
- `transactions_cache`: transaction rows per sheet

`_clean_up()` is called on every authenticated request (via `before_request`). It checks process RSS against `AppConfig.MEMORY_LIMIT_MB` and clears both caches + reinitializes the Google API client if exceeded. This is the intended leak-prevention mechanism for the free-tier Render deployment.
