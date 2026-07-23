"""CLI entry point for the trading bot."""

import argparse
import sys

from bot.logging_config import setup_logging
from bot.validators import validate_all, ValidationError
from bot.client import BinanceClient, BinanceAPIError, BinanceNetworkError
from bot.orders import OrderManager


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Market Order:  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  Limit Order:   python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
  Stop-Limit:    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 60000 --stop-price 59500
        """,
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type: MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (must be > 0)",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Limit price (required for LIMIT and STOP_LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        default=None,
        help="Stop price (required for STOP_LIMIT orders)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the trading bot.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    setup_logging()

    args = parse_args()

    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as e:
        print(f"\n  [ERROR] Validation Error: {e}\n")
        return 1

    try:
        client = BinanceClient()
    except (ValidationError, BinanceNetworkError) as e:
        print(f"\n  [ERROR] Client Error: {e}\n")
        return 1

    manager = OrderManager(client)

    result = manager.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["order_type"],
        quantity=validated["quantity"],
        price=validated["price"],
        stop_price=validated["stop_price"],
    )

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
