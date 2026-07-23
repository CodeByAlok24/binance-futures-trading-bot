# Binance Futures Testnet Trading Bot

A modular, production-style Python CLI application for placing **MARKET**, **LIMIT**, and **STOP_LIMIT** orders on **Binance Futures Testnet (USDT-M)** with input validation, structured logging, comprehensive error handling, and clean separation of concerns.

Built as a technical assessment submission — demonstrating clean architecture, defensive programming, and real-world API integration.

---

## Features

- MARKET, LIMIT, and STOP_LIMIT order placement
- BUY and SELL support
- CLI-based input with argparse
- Input validation before any network call
- Structured logging with file rotation and secret redaction
- Custom exception hierarchy (ValidationError, BinanceAPIError, BinanceNetworkError)
- 45 unit tests covering all validation logic
- Secrets managed via `.env` — never hardcoded

---

## Screenshots
<img width="880" height="407" alt="Screenshot 2026-07-23 163521" src="https://github.com/user-attachments/assets/49fa70e1-40f0-4015-a5ce-ebd4828bba25" />

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Signed REST client for Binance Futures Testnet
│   ├── orders.py            # Order param building, placement, and result formatting
│   ├── validators.py        # Input validation with custom exceptions
│   └── logging_config.py    # Logging setup with rotation and secret redaction
├── tests/
│   ├── __init__.py
│   └── test_validators.py   # 45 unit tests (offline, no API keys needed)
├── logs/                    # Log files auto-created here
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Template for credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     CLI Layer                       │
│                  cli.py (argparse)                  │
│        parses args → calls validate → places order │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                 Validation Layer                     │
│              validators.py                           │
│    validate_all() → symbol, side, type, qty, price  │
│    Raises ValidationError if anything is invalid    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Business Logic                      │
│               orders.py (OrderManager)               │
│    place_order() → builds params, calls client,     │
│    returns OrderResult dataclass                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                 API Client Layer                     │
│               client.py (BinanceClient)               │
│    Handles HMAC signing, HTTP communication,         │
│    error mapping (API errors vs network errors)      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         Binance Futures Testnet API                  │
│         https://testnet.binancefuture.com            │
│         Endpoint: POST /fapi/v1/order               │
└─────────────────────────────────────────────────────┘
```

**Key design principle:** Each layer has a single responsibility and can be tested independently. The CLI never talks directly to the API; the validator never makes network calls.

---

## Setup

### 1. Register on Binance Futures Testnet

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your Binance account
3. Go to **API Management** → **Create API** → choose **System generated**
4. Copy your **API Key** and **Secret Key**

### 2. Clone and Install

```bash
git clone https://github.com/CodeByAlok24/binance-futures-trading-bot.git
cd binance-futures-trading-bot

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Add Credentials

```bash
cp .env.example .env
```

Edit `.env` and add your testnet credentials:

```
BINANCE_TESTNET_API_KEY=your_key_here
BINANCE_TESTNET_API_SECRET=your_secret_here
```

> **Security:** The `.env` file is excluded from version control via `.gitignore`. Your keys are never logged — a `SecretRedactor` filter automatically redacts them from all log output.

---

## CLI Reference

```
usage: cli.py [-h] --symbol SYMBOL --side {BUY,SELL} --type
              {MARKET,LIMIT,STOP_LIMIT} --quantity QUANTITY
              [--price PRICE] [--stop-price STOP_PRICE]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--symbol` | Yes | Trading pair (e.g., `BTCUSDT`, `ETHUSDT`) |
| `--side` | Yes | `BUY` or `SELL` |
| `--type` | Yes | `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `--quantity` | Yes | Order quantity (must be > 0) |
| `--price` | For LIMIT/STOP_LIMIT | Limit price |
| `--stop-price` | For STOP_LIMIT | Stop trigger price |

### Quick Help

```bash
python cli.py --help
```

---

## Usage Examples

### Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Actual output from test run:**

```
==================================================
ORDER REQUEST SUMMARY
==================================================
  Symbol:     BTCUSDT
  Side:       BUY
  Type:       MARKET
  Quantity:   0.001
==================================================

--------------------------------------------------
ORDER RESPONSE
--------------------------------------------------
  Order ID:           23511918268
  Status:             NEW
  Executed Quantity:  0.0000
  Average Price:      N/A
--------------------------------------------------
  [SUCCESS] ORDER PLACED SUCCESSFULLY
--------------------------------------------------
```

### Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

**Actual output from test run:**

```
==================================================
ORDER REQUEST SUMMARY
==================================================
  Symbol:     BTCUSDT
  Side:       SELL
  Type:       LIMIT
  Quantity:   0.001
  Price:      70000.0
==================================================

--------------------------------------------------
ORDER RESPONSE
--------------------------------------------------
  Order ID:           23511938081
  Status:             NEW
  Executed Quantity:  0.0000
  Average Price:      N/A
--------------------------------------------------
  [SUCCESS] ORDER PLACED SUCCESSFULLY
--------------------------------------------------
```

### Stop-Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 117000 --stop-price 118000
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

45 tests covering all validation logic — runs offline, no API keys needed.

```
tests/test_validators.py::TestValidateSymbol::test_valid_symbol PASSED
tests/test_validators.py::TestValidateSymbol::test_lowercase_converted PASSED
...
tests/test_validators.py::TestValidateAll::test_valid_market_order PASSED
tests/test_validators.py::TestValidateAll::test_valid_limit_order PASSED
tests/test_validators.py::TestValidateAll::test_valid_stop_limit_order PASSED

============================= 45 passed in 0.10s ==============================
```

---

## Logging

Logs are written to `logs/trading_bot.log` with automatic rotation (2MB, 3 backups).

| Channel | Level | Detail |
|---------|-------|--------|
| Console | INFO | Key lifecycle events (order placed, error summary) |
| File | DEBUG | Full request params, raw API responses, stack traces |

### Sample log file

```
2026-07-23 14:15:28 | INFO     | bot.client:60  | Binance Futures Testnet client initialized successfully.
2026-07-23 14:15:28 | DEBUG    | bot.client:108 | Order request params: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.001}
2026-07-23 14:15:28 | INFO     | bot.client:111 | Placing MARKET order: BUY 0.001 BTCUSDT
2026-07-23 14:15:29 | DEBUG    | bot.client:119 | Order response: {'orderId': 23511918268, 'status': 'NEW', 'executedQty': '0.0000', ...}
2026-07-23 14:15:29 | INFO     | bot.client:120 | Order placed successfully - ID: 23511918268, Status: NEW
2026-07-23 14:15:40 | INFO     | bot.client:60  | Binance Futures Testnet client initialized successfully.
2026-07-23 14:15:40 | INFO     | bot.client:111 | Placing LIMIT order: SELL 0.001 BTCUSDT @ 70000.0
2026-07-23 14:15:41 | INFO     | bot.client:120 | Order placed successfully - ID: 23511938081, Status: NEW
2026-07-23 14:15:55 | INFO     | bot.client:111 | Placing STOP order: BUY 0.001 BTCUSDT @ 60000.0 (stop: 59500.0)
2026-07-23 14:15:56 | ERROR    | bot.client:128 | Binance API error: Status=400, Code=-2021, Message=Order would immediately trigger.
```

> API keys and secrets are automatically redacted from log output by the `SecretRedactor` filter.

---

## Error Handling

The application distinguishes between three failure modes:

| Error Type | Example | When It Happens |
|-----------|---------|----------------|
| `ValidationError` | Invalid symbol, missing price, negative quantity | Before any API call |
| `BinanceAPIError` | Insufficient balance, invalid symbol, bad price | API rejects the order |
| `BinanceNetworkError` | Timeout, DNS failure, connection refused | Network issues |

**Sample error output:**

```
# Validation error:
  [ERROR] Validation Error: Invalid symbol format: 'BTC'. Symbol must end with USDT (e.g., BTCUSDT, ETHUSDT).

# Missing argument:
  [ERROR] Validation Error: Price is required for LIMIT and STOP_LIMIT orders.

# API error:
  [ERROR] Error: API Error [-2021]: Order would immediately trigger.
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **python-binance** over raw HTTP | Built-in `testnet=True` param, automatic HMAC signing, mature library |
| **argparse** over Click/Typer | Zero external dependencies for the CLI; sufficient for the requirements |
| **`STOP` order type** for Stop-Limit | Binance Futures API uses `STOP` type with `stopPrice` field; `STOP_LIMIT` doesn't exist on Futures |
| **Validation-first pattern** | All input validated before any network call — never send a bad request to the API |
| **No auto-retry on failure** | Retrying order placement risks duplicate orders; report once and let the user decide |
| **dataclass for results** | `OrderResult` provides a consistent contract between `orders.py` and `cli.py` |
| **Secret redaction in logs** | `SecretRedactor` filter on both handlers prevents credential leakage in log files |

---

## Assumptions

- Targets **USDT-M Futures Testnet** only (`/fapi/v1/*` endpoints)
- Default account leverage/margin settings are acceptable
- `recvWindow` default of 5000ms; system clock is reasonably synced
- Sufficient test balance is available in the testnet account
- Testnet data is periodically reset (roughly once per month)

---

## Requirements

- Python 3.7+
- `python-binance>=1.0.20`
- `python-dotenv>=1.0.0`
- `pytest>=7.0.0` (development / testing only)

---

## Deliverables Checklist

| Required Item | Status |
|---------------|--------|
| MARKET order log | ✅ Included (`logs/trading_bot.log`) |
| LIMIT order log | ✅ Included (`logs/trading_bot.log`) |
| Source code (structured) | ✅ 4-layer architecture |
| README with setup | ✅ This file |
| requirements.txt | ✅ Included |
| Bonus: STOP_LIMIT order | ✅ Implemented |
| Bonus: Comprehensive tests | ✅ 45 unit tests |

---

*Built for the Primetrade.ai Python Developer Application Task.*
