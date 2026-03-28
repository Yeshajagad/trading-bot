from __future__ import annotations
from typing import Optional
from bot.logging_config import get_logger

logger = get_logger("validators")

VALID_SIDES       = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned or not cleaned.isalnum():
        raise ValidationError(
            f"Invalid symbol '{cleaned}'. Use format like BTCUSDT."
        )
    return cleaned


def validate_side(side: str) -> str:
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValidationError(f"Side must be BUY or SELL, got '{cleaned}'.")
    return cleaned


def validate_order_type(order_type: str) -> str:
    cleaned = order_type.strip().upper()
    if cleaned not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type must be MARKET, LIMIT, or STOP_MARKET. Got '{cleaned}'."
        )
    return cleaned


def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValidationError(f"Quantity must be positive, got {quantity}.")
    if quantity < 0.001:
        raise ValidationError(f"Quantity {quantity} is below minimum (0.001).")
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    if order_type == "MARKET":
        return None
    if price is None or price <= 0:
        raise ValidationError(
            f"A valid --price is required for {order_type} orders."
        )
    return price


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    cleaned_type = order_type.strip().upper()
    result = {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity":   validate_quantity(quantity),
        "price":      validate_price(price, cleaned_type),
    }
    if cleaned_type == "STOP_MARKET":
        if not stop_price or stop_price <= 0:
            raise ValidationError(
                "--stop-price is required for STOP_MARKET orders."
            )
        result["stop_price"] = stop_price

    logger.info(
        "Validation passed — %s %s %s qty=%s",
        result["side"], result["order_type"], result["symbol"], result["quantity"],
    )
    return result