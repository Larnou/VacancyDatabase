from typing import Any

from src.classes.rates_api import RatesAPI

# Создать класс для работы с вакансиями. В этом классе самостоятельно определить атрибуты,
# такие как название вакансии, ссылка на вакансию, зарплата, краткое описание или требования и т. п.
# (всего не менее четырех атрибутов). Класс должен поддерживать методы сравнения вакансий между собой
# по зарплате и валидировать данные, которыми инициализируются его атрибуты.


class Vacancy:
    """
    Класс Vacancy, позволяет хранить информацию о вакансии в удобном виде.
    """

    __slots__ = (
        "name",
        "salary_info",
        "has_test",
        "experience",
        "requirements",
        "employer",
        "alternate_url",
        "rates_data",
    )

    def __init__(
        self,
        name: str,
        salary: None | dict,
        employer: str,
        requirements: str,
        experience: str,
        has_test: bool,
        alternate_url: str,
        rates_data: dict,
    ) -> None:
        """
        Создаёт объект Vacancy.
        """
        self.name = name
        self.salary_info = self.update_salary_info(salary, rates_data)
        self.requirements = self.remove_from_requirements(requirements)
        self.has_test = has_test
        self.experience = experience
        self.employer = employer
        self.alternate_url = alternate_url

    @staticmethod
    def get_salary_currency(currency: str) -> str:
        """
        Обновляет кодовое значение валюты в соотвествии с общепринятым форматом.

        Args:
            currency: Кодовое значение валюты из HeadHunter.

        Returns:
            Правильное кодовое значение валюты.
        """

        currency_exeptions = {"RUR": "RUB", "BYR": "BYN"}
        currency_value = currency if currency not in currency_exeptions else currency_exeptions[currency]
        return currency_value

    @staticmethod
    def update_currency_value(value: int | float, currency: str, rates_data: dict) -> float:
        """
        Обновляет значение зароботной платы в соотвествии с курсом валюты.

        Args:
            value: Значение валюты.
            currency: Кодовое значение валюты.
            rates_data: Словарь с информацией по курсу валют.

        Returns:
            Значение заработной валюты с учётом курса валют.
        """

        if currency != "RUB":
            rates = RatesAPI().get_currency_rate(currency, rates_data)
            return value * rates
        else:
            return value

    @staticmethod
    def calculate_avg_salary(salary_from: str | float | int, salary_to: str | float | int) -> float | int:
        """
        Обновляет значение зароботной платы в соотвествии с курсом валюты.

        Args:
            salary_from: Нижняя граница заработной платы.
            salary_to: Верхняя граница заработной платы.

        Returns:
            Значение средней заработной платы исходя из двух крайних значений.
        """

        if salary_from != "Не указано" and salary_to != "Не указано":
            return (salary_from + salary_to) / 2

        elif salary_from == "Не указано" and salary_to != "Не указано":
            return salary_to

        elif salary_to == "Не указано" and salary_from != "Не указано":
            return salary_from
        else:
            return 0.0

    def update_salary_info(self, salary: None | dict, rates_data: dict) -> dict[str, Any]:
        """
        Обновление информации по заработной плате: границы зарплаты, валюта и средний уровень зарплаты.

        Args:
            salary: Исходный словарь с информацией по заработной плате.
            rates_data: Набор данных по текущему курсу валют в пересчёте на российские рубли.
        Returns:
            Словарь с информацией по заработной плате.
        """

        salary_info = {"from": 0, "to": 0, "currency": "RUB", "average": 0.0}

        if isinstance(salary, dict):
            # Получаем правильное кодовое значение валюты
            salary_info["currency"] = self.get_salary_currency(salary["currency"])

            # Получаем скорректированное на валюту уровень зарплаты "с .. "
            if isinstance(salary.get("from"), int):
                salary_info["from"] = self.update_currency_value(
                    salary.get("from"), salary_info["currency"], rates_data
                )
            else:
                salary_info["from"] = "Не указано"

            # Получаем скорректированное на валюту уровень зарплаты ".. до"
            if isinstance(salary.get("to"), int):
                salary_info["to"] = self.update_currency_value(salary.get("to"), salary_info["currency"], rates_data)
            else:
                salary_info["to"] = "Не указано"

            salary_info["currency"] = 'RUB'
            # Получаем среднюю зарлпату
            salary_info["average"] = self.calculate_avg_salary(salary_info["from"], salary_info["to"])

            return salary_info
        else:
            return {"from": "Не указано", "to": "Не указано", "currency": "RUB", "average": 0.0}

    @staticmethod
    def remove_from_requirements(requirements: str) -> str:
        """
        Очистка строки требований от HTML тегов после обращения к API.

        Args:
            requirements: Ключевое слово, по которому будет проводиться поиск вакансий.
        Returns:
            Отформатированная строка требований без HTML-тегов.
        """
        requirements = "" if not requirements else requirements
        new_requirement = requirements.replace("<highlighttext>", "")
        new_requirement = new_requirement.replace("</highlighttext>", "")
        return new_requirement

    def get_salary_info(self) -> str:
        """
        Возвращает форматированную информацию о зарплате.

        Returns:
            Форматированная информация о зарплате.
        """
        return f"{self.salary_info['from']} - {self.salary_info['to']} {self.salary_info['currency']}"

    def __str__(self) -> str:
        """
        Строковое представление вакансии: Вакансия, Зарплата, Компания,
        Требования, Опыт работы, Тестовое задание, Ссылка

        Returns:
            Строковое представление вакансии.
        """
        salary_info = self.get_salary_info()
        has_test_info = "Есть" if self.has_test else "Нет"

        return (
            f"Вакансия: {self.name}\n"
            f"Зарплата: {salary_info}\n"
            f"Компания: {self.employer}\n"
            f"Требования: {self.requirements[:140]}\n"
            f"Опыт работы: {self.experience}\n"
            f"Тестовое задание: {has_test_info}\n"
            f"Ссылка: {self.alternate_url}\n"
        )

    def to_dict(self) -> dict:
        """
        Преобразует объект Vacancy в словарь для сериализации

        Returns:
            Представление данных по вакансии в виде словаря.
        """
        return {
            "name": self.name,
            "salary": self.salary_info,
            "has_test": self.has_test,
            "experience": {"name": self.experience},
            "snippet": {"requirement": self.requirements},
            "employer": {"name": self.employer},
            "alternate_url": self.alternate_url,
        }

    @staticmethod
    def cast_to_object_list(vacancy_list_input: list[dict], rates_dict: dict) -> list:
        """
        Переводит JSON данные в список объектов Vacancy.

        Args:
            vacancy_list_input: Список вакансий в формате JSON строки.
            rates_dict: Словарь с информацией по курсу валют для правильного перевода в рубли.
        Returns:
            Список объектов Vacancy.
        """

        vacancy_list_output = []
        for vacany_info in vacancy_list_input:
            vacancy = Vacancy(
                vacany_info["name"],
                vacany_info["salary"],
                vacany_info["employer"]["name"],
                vacany_info["snippet"]["requirement"],
                vacany_info["experience"]["name"],
                vacany_info["has_test"],
                vacany_info["alternate_url"],
                rates_dict,
            )
            vacancy_list_output.append(vacancy)

        return vacancy_list_output
