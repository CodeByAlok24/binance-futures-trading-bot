# Binance Futures Testnet Trading Bot

A structured Python CLI application for placing orders on **Binance Futures Testnet (USDT-M)**, with input validation, structured logging, and clean error handling.

## Features

- Place **MARKET**, **LIMIT**, and **STOP_LIMIT** orders (bonus third order type)
- Support for both **BUY** and **SELL** sides
- Command-line interface with clear help messages
- Input validation before any network call
- Structured logging to file with rotation
- Clean separation between API layer and CLI layer
- Proper error handling with user-friendly messages

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures Testnet client wrapper
│   ├── orders.py          # Order param building + placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging configuration
├── tests/
│   ├── __init__.py
│   └── test_validators.py # Offline unit tests
├── logs/                  # Auto-created, contains trading_bot.log
├── cli.py                 # CLI entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Register on Binance Futures Testnet

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your Binance account (or create one)
3. Navigate to API Management
4. Generate new API Key and Secret
5. Copy and save both credentials securely

### 2. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd trading_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your testnet API credentials
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

**Important:** Never commit your `.env` file to version control.

## Usage

### Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Expected Output:**

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
  Order ID:           123456
  Status:             FILLED
  Executed Quantity:  0.001
  Average Price:      62000.00
--------------------------------------------------
  ✓ ORDER PLACED SUCCESSFULLY
--------------------------------------------------
```

### Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

### Stop-Limit Order (Bonus Feature)

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 60000 --stop-price 59500
```

### CLI Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--symbol` | Yes | Trading pair (e.g., BTCUSDT) |
| `--side` | Yes | Order side: BUY or SELL |
| `--type` | Yes | Order type: MARKET, LIMIT, or STOP_LIMIT |
| `--quantity` | Yes | Order quantity (must be > 0) |
| `--price` | For LIMIT/STOP_LIMIT | Limit price |
| `--stop-price` | For STOP_LIMIT | Stop trigger price |

## Running Tests

```bash
pytest tests/ -v
```

Tests validate input handling offline without network access or API keys.

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`:

- **Console output:** INFO level (concise)
- **File output:** DEBUG level (detailed, with API secret redaction)
- **Log rotation:** 2MB max size, 3 backup files

**Sample log entries:**

```
2026-07-23 12:30:15 | INFO     | bot.client:85 | Placing MARKET order: BUY 0.001 BTCUSDT
2026-07-23 12:30:16 | INFO     | bot.client:90 | Order placed successfully - ID: 123456, Status: FILLED
```

## Error Handling

The application handles three types of errors:

1. **Validation Errors** - Invalid input (bad symbol, missing price, negative quantity)
2. **Binance API Errors** - API rejections (insufficient balance, invalid symbol)
3. **Network Errors** - Connectivity issues (timeout, DNS failure)

All errors are printed to console and logged to file.

## Architecture

```
CLI (cli.py)
    ↓
Validators (validators.py)  →  Validate BEFORE any network call
    ↓
OrderManager (orders.py)    →  Build order params, format output
    ↓
BinanceClient (client.py)   →  API communication, error handling
    ↓
Binance Futures Testnet API
```

## Design Decisions

- **`python-binance` library:** Used for its built-in `testnet=True` support and automatic HMAC signing
- **Input validation first:** All validation happens before any network call to avoid unnecessary API requests
- **Structured results:** `OrderResult` dataclass provides consistent output regardless of success/failure
- **Secret redaction:** API keys and secrets are automatically redacted in log files
- **No auto-retry:** Order placement failures are reported immediately (retrying could cause duplicate orders)

## Assumptions

- Only USDT-M Futures Testnet is targeted (`/fapi/v1/*` endpoints)
- Orders use default account settings (no leverage/margin-type changes)
- `recvWindow` is 5000ms; system clock is reasonably synced
- Sufficient test balance is available in the testnet account
- Testnet resets approximately once per month

## Requirements

- Python 3.7+
- `python-binance>=1.0.20`
- `python-dotenv>=1.0.0`
- `pytest>=7.0.0` (for running tests)
