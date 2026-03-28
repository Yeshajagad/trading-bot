"""
Client layer — auto-detects paper vs live mode.
Paper mode: uses MockExchange (no API keys needed).
Live mode:  uses real Binance Futures Testnet HTTP API.
"""

import os
from dotenv import load_dotenv
from typing import Optional
from bot.logging_config import get_logger
from bot.exchange import MockExchange, MockExchangeError

load_dotenv()
logger = get_logger("client")


class BinanceClientError(Exception):
    pass


class BinanceClient:

    BINANCE_ERRORS = {
        -1121: "Invalid trading symbol. Check symbol name (e.g. BTCUSDT).",
        -2019: "Insufficient margin balance.",
        -1100: "Malformed request — check your parameters.",
        -1102: "A required parameter is missing.",
        -1111: "Precision too high for quantity.",
    }

    def __init__(self):
        self.api_key    = os.getenv("BINANCE_API_KEY", "").strip()
        self.api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

        if self.api_key and self.api_secret:
            self._mode = "live"
            self._base_url = os.getenv(
                "BINANCE_BASE_URL", "https://testnet.binancefuture.com"
            )
            self._setup_live_session()
            logger.info("Client mode: LIVE — Binance Futures Testnet")
        else:
            self._mode     = "paper"
            self._exchange = MockExchange()
            logger.info("Client mode: PAPER — mock exchange active")

    def _setup_live_session(self):
        import requests
        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": self.api_key})

    def place_order(
        self,
        symbol:     str,
        side:       str,
        order_type: str,
        quantity:   float,
        price:      Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:
        try:
            if self._mode == "paper":
                return self._exchange.place_order(
                    symbol, side, order_type, quantity, price, stop_price
                )
            else:
                return self._place_live_order(
                    symbol, side, order_type, quantity, price, stop_price
                )
        except MockExchangeError as e:
            raise BinanceClientError(str(e))

    def _place_live_order(
        self, symbol, side, order_type, quantity, price, stop_price
    ) -> dict:
        import hashlib, hmac, time, requests
        from urllib.parse import urlencode

        params = {
            "symbol":    symbol,
            "side":      side,
            "type":      order_type,
            "quantity":  quantity,
            "timestamp": int(time.time() * 1000),
        }
        if order_type == "LIMIT":
            params.update({"price": price, "timeInForce": "GTC"})
        if order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price

        query     = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature

        logger.info("POST /fapi/v1/order — %s %s %s qty=%s",
                    side, order_type, symbol, quantity)
        try:
            resp = self._session.post(
                f"{self._base_url}/fapi/v1/order",
                data=params,
                timeout=10,
            )
        except requests.exceptions.Timeout:
            raise BinanceClientError("Request timed out.")
        except requests.exceptions.ConnectionError:
            raise BinanceClientError("Cannot connect to Binance.")

        data = resp.json()
        if resp.status_code != 200:
            code     = data.get("code", "unknown")
            friendly = self.BINANCE_ERRORS.get(code, data.get("msg", "Unknown error"))
            logger.error("API error %s: %s", code, friendly)
            raise BinanceClientError(f"[{code}] {friendly}")

        logger.info("Live order placed — id=%s status=%s",
                    data.get("orderId"), data.get("status"))
        return data