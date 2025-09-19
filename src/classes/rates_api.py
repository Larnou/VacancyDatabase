import json
import os
from pathlib import Path
from typing import Any

import requests


class RatesAPI:
    """
    Класс RatesAPI, обеспечивает получение информации по курсу валют.

    Attributes:
        __API_URL: Базовый URL подключения к API
    """

    __API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __get_rates_by_api(self) -> Any | dict[Any, Any]:
        """
        Получает список курсов валют через подключение к ЦБРФ Api.

        Returns:
            Словарь со списком валют и информацией по ним.
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
    def get_currency_rate(curency_code: str, rate_dict: dict) -> Any | float:
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

    @staticmethod
    def load_rates_data(file_name: str) -> dict[str, str]:
        """
        Загрузка данных по курсу валют. Если файл существует, загрузка с файла.
        Если не существует: получение данных и сохранение в файл.

        Args:
            file_name: Название файла с указанием расширения (.json).
        Returns:
            Словарь со списком валют и информацией по ним.
        """

        # Коментарий на будущее:
        # Можно реализовать так, чтобы программа проверяла курс валют на текущий день.
        # Пыталась сама найти файл с датой в названии, и если его нет, то создать новый и старый удалить (если был).
        # Если файл существует, то просто загрузить его. Это позволит не указывать назавание файла.

        current_file = Path(__file__).resolve()
        BASE_DIR = current_file.parent.parent.parent
        DATA_PATH = BASE_DIR / "data" / "currencies" / file_name

        # Создание файла, если его не существует
        if not os.path.exists(DATA_PATH):
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                rates = RatesAPI().__get_rates_by_api()
                json.dump(rates, f, ensure_ascii=False, indent=4)
            return rates
        else:
            # Загрузка файла, так как он уже существует.
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
