"""
Paper Trading Exchange — simulates Binance Futures API responses.
Produces identical JSON schema to the real Binance API.
Used when no API keys are configured.
"""

import random
import time
import uuid
from typing import Optional
from bot.logging_config import get_logger

logger = get_logger("exchange")

MOCK_PRICES = {
    "BTCUSDT":  67450.00,
    "ETHUSDT":   3521.00,
    "BNBUSDT":    412.00,
    "SOLUSDT":    175.00,
    "XRPUSDT":      0.61,
    "DOGEUSDT":     0.18,
    "ADAUSDT":      0.45,
}


class MockExchangeError(Exception):
    pass


class MockExchange:
    """
    Simulates a Binance Futures exchange locally.
    All responses match real Binance API structure exactly.
    """

    def __init__(self):
        self.orders = {}
        logger.info(
            "Paper trading mode active — no real funds, no API calls"
        )
        logger.info(
            "Supported symbols: %s", list(MOCK_PRICES.keys())
        )

    def _get_market_price(self, symbol: str) -> float:
        if symbol not in MOCK_PRICES:
            raise MockExchangeError(
                f"Symbol '{symbol}' not found in mock exchange. "
                f"Supported: {list(MOCK_PRICES.keys())}"
            )
        base     = MOCK_PRICES[symbol]
        slippage = base * random.uniform(-0.001, 0.001)
        return round(base + slippage, 4)

    def place_order(
        self,
        symbol:     str,
        side:       str,
        order_type: str,
        quantity:   float,
        price:      Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:

        order_id     = random.randint(100_000_000, 999_999_999)
        client_id    = str(uuid.uuid4())[:8].upper()
        timestamp    = int(time.time() * 1000)
        market_price = self._get_market_price(symbol)

        logger.info(
            "Simulating %s %s %s | qty=%s | market_price=%s",
            side, order_type, symbol, quantity, market_price,
        )

        # Determine fill status based on order type + price logic
        if order_type == "MARKET":
            status       = "FILLED"
            avg_price    = market_price
            executed_qty = quantity

        elif order_type == "LIMIT":
            fills = (side == "BUY" and price >= market_price) or \
                    (side == "SELL" and price <= market_price)
            if fills:
                status, avg_price, executed_qty = "FILLED", price, quantity
            else:
                status, avg_price, executed_qty = "NEW", 0.0, 0.0

        elif order_type == "STOP_MARKET":
            status, avg_price, executed_qty = "NEW", 0.0, 0.0

        else:
            raise MockExchangeError(f"Unknown order type: {order_type}")

        response = {
            "orderId":       order_id,
            "clientOrderId": client_id,
            "symbol":        symbol,
            "side":          side,
            "type":          order_type,
            "origQty":       str(quantity),
            "executedQty":   str(executed_qty),
            "avgPrice":      str(avg_price),
            "price":         str(price or 0),
            "stopPrice":     str(stop_price or 0),
            "status":        status,
            "timeInForce":   "GTC" if order_type != "MARKET" else "IOC",
            "updateTime":    timestamp,
            "reduceOnly":    False,
            "positionSide":  "BOTH",
        }

        self.orders[order_id] = response
        logger.info(
            "Order simulated — id=%s status=%s avgPrice=%s executedQty=%s",
            order_id, status, avg_price, executed_qty,
        )
        return response