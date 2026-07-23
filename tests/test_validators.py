"""Unit tests for input validators."""

import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    validate_all,
    ValidationError,
)


class TestValidateSymbol:
    """Tests for symbol validation."""

    def test_valid_symbol(self):
        assert validate_symbol("BTCUSDT") == "BTCUSDT"

    def test_lowercase_converted(self):
        assert validate_symbol("btcusdt") == "BTCUSDT"

    def test_mixed_case(self):
        assert validate_symbol("EthUSDT") == "ETHUSDT"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_symbol("")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_symbol(None)

    def test_invalid_format_no_usdt(self):
        with pytest.raises(ValidationError, match="must end with USDT"):
            validate_symbol("BTCUSD")

    def test_invalid_format_special_chars(self):
        with pytest.raises(ValidationError, match="Invalid symbol format"):
            validate_symbol("BTC-USDT")

    def test_with_spaces(self):
        assert validate_symbol("  BTCUSDT  ") == "BTCUSDT"


class TestValidateSide:
    """Tests for side validation."""

    def test_valid_buy(self):
        assert validate_side("BUY") == "BUY"

    def test_valid_sell(self):
        assert validate_side("SELL") == "SELL"

    def test_lowercase_buy(self):
        assert validate_side("buy") == "BUY"

    def test_lowercase_sell(self):
        assert validate_side("sell") == "SELL"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_side("")

    def test_invalid_side(self):
        with pytest.raises(ValidationError, match="Invalid side"):
            validate_side("HOLD")

    def test_with_spaces(self):
        assert validate_side("  BUY  ") == "BUY"


class TestValidateOrderType:
    """Tests for order type validation."""

    def test_valid_market(self):
        assert validate_order_type("MARKET") == "MARKET"

    def test_valid_limit(self):
        assert validate_order_type("LIMIT") == "LIMIT"

    def test_valid_stop_limit(self):
        assert validate_order_type("STOP_LIMIT") == "STOP_LIMIT"

    def test_lowercase(self):
        assert validate_order_type("market") == "MARKET"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_order_type("")

    def test_invalid_type(self):
        with pytest.raises(ValidationError, match="Invalid order type"):
            validate_order_type("STOP")


class TestValidateQuantity:
    """Tests for quantity validation."""

    def test_valid_quantity(self):
        assert validate_quantity("0.001") == 0.001

    def test_integer_quantity(self):
        assert validate_quantity("1") == 1.0

    def test_large_quantity(self):
        assert validate_quantity("100") == 100.0

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_quantity("")

    def test_non_numeric_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be a positive number"):
            validate_quantity("abc")

    def test_zero_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be greater than 0"):
            validate_quantity("0")

    def test_negative_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be greater than 0"):
            validate_quantity("-1")


class TestValidatePrice:
    """Tests for price validation."""

    def test_valid_price(self):
        assert validate_price("50000") == 50000.0

    def test_decimal_price(self):
        assert validate_price("50000.50") == 50000.50

    def test_not_required_returns_none(self):
        assert validate_price(None, required=False) is None

    def test_empty_not_required_returns_none(self):
        assert validate_price("", required=False) is None

    def test_required_missing_raises(self):
        with pytest.raises(ValidationError, match="required"):
            validate_price(None, required=True)

    def test_non_numeric_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be a positive number"):
            validate_price("abc")

    def test_zero_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be greater than 0"):
            validate_price("0")


class TestValidateStopPrice:
    """Tests for stop price validation."""

    def test_valid_stop_price(self):
        assert validate_stop_price("59500") == 59500.0

    def test_not_required_returns_none(self):
        assert validate_stop_price(None, required=False) is None

    def test_required_missing_raises(self):
        with pytest.raises(ValidationError, match="required"):
            validate_stop_price(None, required=True)

    def test_zero_raises(self):
        with pytest.raises(ValidationError, match="[Mm]ust be greater than 0"):
            validate_stop_price("0")


class TestValidateAll:
    """Tests for validate_all function."""

    def test_valid_market_order(self):
        result = validate_all("BTCUSDT", "BUY", "MARKET", "0.001")
        assert result["symbol"] == "BTCUSDT"
        assert result["side"] == "BUY"
        assert result["order_type"] == "MARKET"
        assert result["quantity"] == 0.001
        assert result["price"] is None
        assert result["stop_price"] is None

    def test_valid_limit_order(self):
        result = validate_all("ETHUSDT", "SELL", "LIMIT", "0.1", price="3000")
        assert result["symbol"] == "ETHUSDT"
        assert result["side"] == "SELL"
        assert result["order_type"] == "LIMIT"
        assert result["quantity"] == 0.1
        assert result["price"] == 3000.0

    def test_valid_stop_limit_order(self):
        result = validate_all(
            "BTCUSDT", "BUY", "STOP_LIMIT", "0.001",
            price="60000", stop_price="59500"
        )
        assert result["order_type"] == "STOP_LIMIT"
        assert result["price"] == 60000.0
        assert result["stop_price"] == 59500.0

    def test_limit_missing_price_raises(self):
        with pytest.raises(ValidationError, match="Price is required"):
            validate_all("BTCUSDT", "BUY", "LIMIT", "0.001")

    def test_stop_limit_missing_price_raises(self):
        with pytest.raises(ValidationError, match="Price is required"):
            validate_all("BTCUSDT", "BUY", "STOP_LIMIT", "0.001")

    def test_stop_limit_missing_stop_price_raises(self):
        with pytest.raises(ValidationError, match="Stop price is required"):
            validate_all("BTCUSDT", "BUY", "STOP_LIMIT", "0.001", price="60000")
