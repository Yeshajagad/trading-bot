# ⚡ Binance Futures Trading Bot

A production-grade Python CLI trading bot for Binance Futures.
Supports **paper trading mode** (no API keys needed) and **live Binance Testnet mode**.

## Features
- Market, Limit, and Stop-Market orders
- BUY and SELL on any supported symbol
- Auto paper trading mode when no API keys configured
- Rich colored CLI with confirmation prompt
- Full input validation before any API call
- Structured rotating log file
- Clean layered architecture (client / orders / validators / CLI)

## Trading Modes

| Mode | When | Behaviour |
|------|------|-----------|
| **PAPER** | No API keys in `.env` | Built-in mock exchange, identical Binance response schema |
| **LIVE** | API keys in `.env` | Real Binance Futures Testnet |

> Binance Testnet API keys were unavailable during development.
> A paper trading layer was implemented with identical Binance API response
> schema, including order IDs, fill simulation, and status values.
> The system auto-switches to live mode when credentials are provided.

## Setup
```bash
git clone https://github.com/Yeshajagad/trading_bot.git
cd trading_bot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Add a `.env` file:
```
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_BASE_URL=https://testnet.binancefuture.com
```
Leave blank for paper trading. Add keys for live testnet.

## Run Examples

### Market Order
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit Order
```bash
python cli.py place --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3600
```

### Stop-Market Order
```bash
python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 65000
```

### Help
```bash
python cli.py --help
python cli.py place --help
```

## Project Structure
```
trading_bot/
├── bot/
│   ├── __init__.py        # Auto-initialises logging
│   ├── client.py          # Auto paper/live client
│   ├── exchange.py        # Paper trading mock engine
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Structured rotating logger
├── logs/
│   └── trading_bot.log    # All logs written here
├── cli.py                 # CLI entry point
├── .env                   # API credentials (never committed)
├── requirements.txt
└── README.md
```

## Supported Symbols (Paper Mode)
BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, DOGEUSDT, ADAUSDT
