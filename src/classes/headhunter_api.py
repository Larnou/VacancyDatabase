import json
import sys
import time
from typing import Any

import Levenshtein
import requests
from tqdm import tqdm


# Исправить код ниже
class HeadHunterAPI:
    """
    Класс HeadHunterAPI, обеспечивает связь с HH Api и получение списка работадателей и их доступных вакансий.

    Attributes:
        __API_EMPLOYERS_URL: Базовый URL подключения к API по работадателям.
        __API_VACANCIES_URL: Базовый URL подключения к API по вакансиям.
    """

    __API_EMPLOYERS_URL = "https://api.hh.ru/employers"
    __API_VACANCIES_URL = "https://api.hh.ru/vacancies"

    def __init__(self) -> None:
        """
        Создаёт объект HeadHunterAPI.
        """

    @staticmethod
    def __connect_to_api(api: str, api_parameters: dict) -> list:
        """
        Получает список работадателей через подключение к HH Api.

        Args:
            api_parameters: Набор параметр для работы API.

        Returns:
            Список работадателей и информацию о них.
        """
        headers = {"User-Agent": "HH-User-Agent"}

        try:
            response = requests.get(api, headers=headers, params=api_parameters)

            # Проверка статус-кода ответа
            if response.status_code != 200:
                print(f"Ошибка HH API: статус {response.status_code}")
                return []
            else:
                items_from_answer = response.json()["items"]
                return items_from_answer

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API hh.ru: {e}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка обработки ответа API: {e}")
            return []

    def get_employer(self, employer_name: str) -> dict[str, Any] | None:
        """
        Получает работадателя с названием наиболее подходящим по указанному имени employer_name.

        Args:
            employer_name: Имя работадателя или название компании.

        Returns:
            Работадателя и информацию о нём.
        """

        api_parameters = {"text": employer_name, "area": 113, "only_with_vacancies": False, "per_page": 10, "page": 0}

        # Список вакансий по ключевому слову
        employers = self.__connect_to_api(api=self.__API_EMPLOYERS_URL, api_parameters=api_parameters)

        if len(employers) > 0:
            employer = max(employers, key=lambda x: Levenshtein.ratio(x.get("name"), employer_name))
            employer["employer_vacancies"] = self.get_vacancies_from_employer(employer["id"])
            return employer
        else:
            return None

    def get_vacancies_from_employer(self, employer_id: str) -> list[dict[str, Any]]:
        """
        Получает список вакансий от определённого работадателя.

        Args:
            employer_id: ID работадателя или компании.

        Returns:
            Список вакансий по этому работадателю.
        """

        api_parameters = {"employer_id": employer_id, "per_page": 50, "page": 0}

        # Список вакансий по ключевому слову
        vacancies_list = []

        while api_parameters["page"] != 50:
            vacancies = self.__connect_to_api(api=self.__API_VACANCIES_URL, api_parameters=api_parameters)

            if len(vacancies) > 0:
                vacancies_list.extend(vacancies)
                api_parameters["page"] += 1
                time.sleep(1)
            else:
                break

        return vacancies_list

    def get_list_of_employers(self, employers_name_list: list[str]) -> list[dict[str, Any]]:
        """
        Получает список работадателей из employers_name_list.

        Args:
            employers_name_list: Список работадателей.

        Returns:
            Список работадателей.
        """
        employers = []

        pbar = tqdm(employers_name_list, desc="Обработка", ascii=True, file=sys.stderr)
        for employer_name in employers_name_list:
            pbar.set_description(f"Загрузка вакансий от: {employer_name}")
            employer = self.get_employer(employer_name)
            if employer:
                employers.append(employer)
            pbar.update(1)

        return employers
