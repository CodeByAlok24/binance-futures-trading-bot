"""Input validation for trading bot CLI arguments."""

import re
from typing import Optional


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol.

    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT).

    Returns:
        Normalized uppercase symbol.

    Raises:
        ValidationError: If symbol format is invalid.
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty.")

    symbol = symbol.upper().strip()

    if not re.match(r'^[A-Z0-9]+USDT$', symbol):
        raise ValidationError(
            f"Invalid symbol format: '{symbol}'. "
            "Symbol must end with USDT (e.g., BTCUSDT, ETHUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """Validate and normalize order side.

    Args:
        side: Order side (BUY or SELL).

    Returns:
        Normalized uppercase side.

    Raises:
        ValidationError: If side is invalid.
    """
    if not side:
        raise ValidationError("Side cannot be empty.")

    side = side.upper().strip()

    if side not in ("BUY", "SELL"):
        raise ValidationError(
            f"Invalid side: '{side}'. Must be 'BUY' or 'SELL'."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """Validate and normalize order type.

    Args:
        order_type: Order type (MARKET, LIMIT, or STOP_LIMIT).

    Returns:
        Normalized uppercase order type.

    Raises:
        ValidationError: If order type is invalid.
    """
    if not order_type:
        raise ValidationError("Order type cannot be empty.")

    order_type = order_type.upper().strip()

    valid_types = ("MARKET", "LIMIT", "STOP_LIMIT")
    if order_type not in valid_types:
        raise ValidationError(
            f"Invalid order type: '{order_type}'. "
            f"Must be one of: {', '.join(valid_types)}."
        )

    return order_type


def validate_quantity(quantity: str) -> float:
    """Validate and parse order quantity.

    Args:
        quantity: Order quantity as string.

    Returns:
        Parsed quantity as float.

    Raises:
        ValidationError: If quantity is invalid.
    """
    if not quantity:
        raise ValidationError("Quantity cannot be empty.")

    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid quantity: '{quantity}'. Must be a positive number."
        )

    if qty <= 0:
        raise ValidationError(
            f"Invalid quantity: {qty}. Must be greater than 0."
        )

    return qty


def validate_price(price: Optional[str], required: bool = False) -> Optional[float]:
    """Validate and parse order price.

    Args:
        price: Order price as string.
        required: If True, raises error when price is None or empty.

    Returns:
        Parsed price as float, or None if not provided and not required.

    Raises:
        ValidationError: If price is required but missing, or invalid.
    """
    if not price or price.strip() == "":
        if required:
            raise ValidationError(
                "Price is required for LIMIT and STOP_LIMIT orders."
            )
        return None

    try:
        price_val = float(price)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid price: '{price}'. Must be a positive number."
        )

    if price_val <= 0:
        raise ValidationError(
            f"Invalid price: {price_val}. Must be greater than 0."
        )

    return price_val


def validate_stop_price(stop_price: Optional[str], required: bool = False) -> Optional[float]:
    """Validate and parse stop price for STOP_LIMIT orders.

    Args:
        stop_price: Stop price as string.
        required: If True, raises error when stop_price is None or empty.

    Returns:
        Parsed stop price as float, or None if not provided and not required.

    Raises:
        ValidationError: If stop_price is required but missing, or invalid.
    """
    if not stop_price or stop_price.strip() == "":
        if required:
            raise ValidationError(
                "Stop price is required for STOP_LIMIT orders."
            )
        return None

    try:
        stop_val = float(stop_price)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid stop price: '{stop_price}'. Must be a positive number."
        )

    if stop_val <= 0:
        raise ValidationError(
            f"Invalid stop price: {stop_val}. Must be greater than 0."
        )

    return stop_val


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """Validate all order parameters at once.

    Args:
        symbol: Trading pair symbol.
        side: Order side.
        order_type: Order type.
        quantity: Order quantity.
        price: Order price (required for LIMIT/STOP_LIMIT).
        stop_price: Stop price (required for STOP_LIMIT).

    Returns:
        Dictionary with validated and normalized parameters.

    Raises:
        ValidationError: If any parameter is invalid.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)

    needs_price = validated_type in ("LIMIT", "STOP_LIMIT")
    needs_stop = validated_type == "STOP_LIMIT"

    validated_price = validate_price(price, required=needs_price)
    validated_stop = validate_stop_price(stop_price, required=needs_stop)

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_type,
        "quantity": validated_qty,
        "price": validated_price,
        "stop_price": validated_stop,
    }
