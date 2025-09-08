# Тесты метода __get_rates_by_api
import json
from unittest.mock import Mock, patch

import pytest
import requests

from src.classes.rates_api import RatesAPI


@patch("src.classes.rates_api.requests.get")
def test_get_rates_by_api_success(mock_get, mock_api_response):
    """Тест успешного получения курсов валют через API"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_get.return_value = mock_response

    rates_api = RatesAPI()
    result = rates_api._RatesAPI__get_rates_by_api()

    assert result == mock_api_response["Valute"]
    mock_get.assert_called_once_with("https://www.cbr-xml-daily.ru/daily_json.js")


@patch("src.classes.rates_api.requests.get")
def test_get_rates_by_api_failure_status_code(mock_get):
    """Тест получения курсов валют с ошибкой статус-кода"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    rates_api = RatesAPI()
    result = rates_api._RatesAPI__get_rates_by_api()

    assert result == {}
    mock_get.assert_called_once()


@patch("src.classes.rates_api.requests.get")
def test_get_rates_by_api_exception(mock_get):
    """Тест получения курсов валют с исключением"""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    rates_api = RatesAPI()
    result = rates_api._RatesAPI__get_rates_by_api()

    assert result == {}
    mock_get.assert_called_once()


@patch("src.classes.rates_api.requests.get")
def test_get_rates_by_api_json_decode_error(mock_get):
    """Тест получения курсов валют с ошибкой декодирования JSON"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("JSON decode error", "", 0)
    mock_get.return_value = mock_response

    rates_api = RatesAPI()
    result = rates_api._RatesAPI__get_rates_by_api()

    assert result == {}
    mock_get.assert_called_once()


# Тесты метода get_currency_rate
def test_get_currency_rate_usd(sample_rates_data):
    """Тест получения курса USD"""
    result = RatesAPI.get_currency_rate("USD", sample_rates_data)

    # USD: Value=75.5, Nominal=1 → 75.5
    assert result == 75.5


def test_get_currency_rate_eur(sample_rates_data):
    """Тест получения курса EUR"""
    result = RatesAPI.get_currency_rate("EUR", sample_rates_data)

    # EUR: Value=85.2, Nominal=1 → 85.2
    assert result == 85.2


def test_get_currency_rate_jpy(sample_rates_data):
    """Тест получения курса JPY (номинал 100)"""
    result = RatesAPI.get_currency_rate("JPY", sample_rates_data)

    # JPY: Value=68.9, Nominal=100 → 0.689
    assert round(result, 3) == 0.689


def test_get_currency_rate_invalid_code(sample_rates_data):
    """Тест получения курса несуществующей валюты"""
    with pytest.raises(KeyError):
        RatesAPI.get_currency_rate("INVALID", sample_rates_data)
