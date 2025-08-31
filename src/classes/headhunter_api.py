import json
from typing import Any

import requests


# Исправить код ниже
class HeadHunterAPI:
    """
    Класс HeadHunterAPI, обеспечивает связь с HH Api и получение списка вакансий с указанием ключевого слова.

    Attributes:
        __API_URL: Базовый URL подключения к API
    """

    __API_URL = "https://api.hh.ru/vacancies"
    __slots__ = ("__headers", "__params", "__vacancies")

    def __init__(self) -> None:
        """
        Создаёт объект HeadHunterAPI.
        """
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.__params = {"text": "", "page": 0, "per_page": 10}
        self.__vacancies = []

    def connect_to_api(self) -> requests.Response:
        """
        Подключение к HH Api.

        Returns:
            Response подключения API.
        """
        return requests.get(self.__API_URL, headers=self.__headers, params=self.__params)

    def __get_vacancies_by_api(self) -> list[dict[Any, Any]]:
        """
        Получает список вакансий через подключение к HH Api.

        Returns:
            Список вакансий
        """
        try:
            response = self.connect_to_api()

            # Проверка статус-кода ответа
            if response.status_code != 200:
                print(f"Ошибка API: статус {response.status_code}")
                return []
            else:
                vacancies = response.json()["items"]
                return vacancies

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API hh.ru: {e}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка обработки ответа API: {e}")
            return []

    def get_vacancies(self, keyword: str) -> list[dict]:
        """
        Получение вакансий по заданному ключевому слову keyword.

        Args:
            keyword: Ключевое слово, по которому будет проводиться поиск вакансий.
        Returns:
            Список вакансий, содержащих ключевое слово.
        """
        self.__params["text"] = keyword
        while self.__params.get("page") != 1:
            vacancies = self.__get_vacancies_by_api()
            self.__vacancies.extend(vacancies)
            self.__params["page"] += 1

        return self.__vacancies
