from typing import Optional
from bot.client import BinanceClient
from bot.logging_config import get_logger

logger = get_logger("orders")


class OrderManager:

    def __init__(self, client: BinanceClient):
        self.client = client

    def place_order(
        self,
        symbol:     str,
        side:       str,
        order_type: str,
        quantity:   float,
        price:      Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:
        logger.info(
            "OrderManager — placing %s %s %s qty=%s",
            side, order_type, symbol, quantity,
        )
        return self.client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )