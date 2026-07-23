"""Order placement logic for the trading bot."""

import logging
from dataclasses import dataclass, field
from typing import Optional

from bot.client import BinanceClient, BinanceAPIError, BinanceNetworkError


@dataclass
class OrderResult:
    """Structured result from an order placement."""

    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    raw_response: dict = field(default_factory=dict)
    error_message: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return (
                f"Order ID: {self.order_id}\n"
                f"Status: {self.status}\n"
                f"Executed Quantity: {self.executed_qty}\n"
                f"Average Price: {self.avg_price}"
            )
        return f"Error: {self.error_message}"


# Mapping from user-facing order types to Binance API types
ORDER_TYPE_MAP = {
    "MARKET": "MARKET",
    "LIMIT": "LIMIT",
    "STOP_LIMIT": "STOP",
}


class OrderManager:
    """Manages order placement on Binance Futures Testnet."""

    def __init__(self, client: BinanceClient):
        """Initialize with a BinanceClient instance.

        Args:
            client: Initialized BinanceClient.
        """
        self.client = client
        self.logger = logging.getLogger(__name__)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> OrderResult:
        """Place an order and return structured result.

        Args:
            symbol: Trading pair (e.g., BTCUSDT).
            side: BUY or SELL.
            order_type: MARKET, LIMIT, or STOP_LIMIT.
            quantity: Order quantity.
            price: Limit price (required for LIMIT/STOP_LIMIT).
            stop_price: Stop price (required for STOP_LIMIT).

        Returns:
            OrderResult with order details or error information.
        """
        self._print_request_summary(symbol, side, order_type, quantity, price, stop_price)

        api_order_type = ORDER_TYPE_MAP.get(order_type, order_type)

        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=api_order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
            )

            result = OrderResult(
                success=True,
                order_id=response.get("orderId"),
                status=response.get("status"),
                executed_qty=response.get("executedQty", "N/A"),
                avg_price=response.get("avgPrice", "N/A"),
                raw_response=response,
            )

            self._print_response(result)
            return result

        except BinanceAPIError as e:
            result = OrderResult(
                success=False,
                error_message=f"API Error [{e.error_code}]: {e.message}",
            )
            self._print_response(result)
            return result

        except BinanceNetworkError as e:
            result = OrderResult(
                success=False,
                error_message=f"Network Error: {e.message}",
            )
            self._print_response(result)
            return result

    def _print_request_summary(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float],
        stop_price: Optional[float],
    ) -> None:
        """Print formatted order request summary."""
        print("\n" + "=" * 50)
        print("ORDER REQUEST SUMMARY")
        print("=" * 50)
        print(f"  Symbol:     {symbol}")
        print(f"  Side:       {side}")
        print(f"  Type:       {order_type}")
        print(f"  Quantity:   {quantity}")
        if price is not None:
            print(f"  Price:      {price}")
        if stop_price is not None:
            print(f"  Stop Price: {stop_price}")
        print("=" * 50 + "\n")

    def _print_response(self, result: OrderResult) -> None:
        """Print formatted order response."""
        print("\n" + "-" * 50)
        print("ORDER RESPONSE")
        print("-" * 50)

        if result.success:
            print(f"  Order ID:           {result.order_id}")
            print(f"  Status:             {result.status}")
            print(f"  Executed Quantity:  {result.executed_qty}")
            print(f"  Average Price:      {result.avg_price}")
            print("-" * 50)
            print("  [SUCCESS] ORDER PLACED SUCCESSFULLY")
        else:
            print(f"  Error: {result.error_message}")
            print("-" * 50)
            print("  [FAILED] ORDER FAILED")

        print("-" * 50 + "\n")
