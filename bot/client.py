"""Binance Futures Testnet client wrapper."""

import logging
import os

from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import requests

from bot.validators import ValidationError


class BinanceAPIError(Exception):
    """Raised when Binance API returns an error."""

    def __init__(self, message: str, status_code: int = None, error_code: int = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class BinanceNetworkError(Exception):
    """Raised when network communication fails."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class BinanceClient:
    """Wrapper for Binance Futures Testnet API."""

    TESTNET_BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self):
        """Initialize client with credentials from environment variables."""
        load_dotenv()

        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValidationError(
                "API credentials not found. "
                "Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET "
                "in your .env file or environment variables."
            )

        self.logger = logging.getLogger(__name__)

        try:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=True,
            )
            self.logger.info("Binance Futures Testnet client initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Binance client: {e}")
            raise BinanceNetworkError(
                f"Failed to initialize Binance client: {e}",
                original_error=e,
            )

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        stop_price: float = None,
    ) -> dict:
        """Place an order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g., BTCUSDT).
            side: BUY or SELL.
            order_type: MARKET, LIMIT, or STOP.
            quantity: Order quantity.
            price: Limit price (required for LIMIT/STOP orders).
            stop_price: Stop price (required for STOP orders).

        Returns:
            API response dictionary.

        Raises:
            BinanceAPIError: If API returns an error.
            BinanceNetworkError: If network request fails.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = price
        elif order_type == "STOP":
            params["price"] = price
            params["stopPrice"] = stop_price

        self.logger.debug(f"Order request params: {params}")

        try:
            self.logger.info(
                f"Placing {order_type} order: {side} {quantity} {symbol}"
                + (f" @ {price}" if price else "")
                + (f" (stop: {stop_price})" if stop_price else "")
            )

            response = self.client.futures_create_order(**params)

            self.logger.debug(f"Order response: {response}")
            self.logger.info(
                f"Order placed successfully - ID: {response.get('orderId')}, "
                f"Status: {response.get('status')}"
            )

            return response

        except BinanceAPIException as e:
            self.logger.error(
                f"Binance API error: Status={e.status_code}, "
                f"Code={e.code}, Message={e.message}"
            )
            raise BinanceAPIError(
                message=e.message,
                status_code=e.status_code,
                error_code=e.code,
            )

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise BinanceNetworkError(
                "Failed to connect to Binance API. Check your network connection.",
                original_error=e,
            )

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise BinanceNetworkError(
                "Request to Binance API timed out.",
                original_error=e,
            )

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise BinanceNetworkError(
                f"Network request failed: {e}",
                original_error=e,
            )

        except Exception as e:
            self.logger.error(f"Unexpected error placing order: {e}")
            raise BinanceNetworkError(
                f"Unexpected error: {e}",
                original_error=e,
            )
