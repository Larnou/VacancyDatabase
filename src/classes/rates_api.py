import json
from typing import Any

import requests


class RatesAPI:
    """
    Класс RatesAPI, обеспечивает получение информации по курсу валют.

    Attributes:
        __API_URL: Базовый URL подключения к API
    """

    __API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self) -> None:
        pass

    def get_rates_by_api(self) -> Any | dict[Any, Any]:
        """
        Получает список курсов валют через подключение к ЦБРФ Api.

        Returns:
            Список курсов валют
        """
        try:
            response = requests.get(self.__API_URL)

            # Проверка статус-кода ответа
            if response.status_code != 200:
                print(f"Ошибка API: статус {response.status_code}")
                return {}
            else:
                rates = response.json()
                rates = rates.get("Valute")
                return rates

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API ЦБРФ: {e}")
            return {}
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка обработки ответа API ЦБРФ: {e}")
            return {}

    @staticmethod
    def get_currency_rate(curency_code: str, rate_dict: dict[str, str]) -> Any | float:
        """
        Получение текущего курса валюты, указанной в curency_code в пересчёте 1 единица валюты == N рублей

        Args:
            curency_code: Буквенный код валюты: USD, EUR и так далее.
            rate_dict: Служебный словарь с информацией по валютам
        Returns:
            Текущий курс валюты, указанный в curency_code в пересчёте N рублей на 1 единицу валюты
        """
        currency = rate_dict[curency_code]
        currency_value = float(currency.get("Value"))
        currency_nominal = float(currency.get("Nominal"))
        return currency_value / currency_nominal
