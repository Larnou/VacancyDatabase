from typing import Any

from src.classes.rates_api import RatesAPI

# Создать класс для работы с вакансиями. В этом классе самостоятельно определить атрибуты,
# такие как название вакансии, ссылка на вакансию, зарплата, краткое описание или требования и т. п.
# (всего не менее четырех атрибутов). Класс должен поддерживать методы сравнения вакансий между собой
# по зарплате и валидировать данные, которыми инициализируются его атрибуты.


class Vacancy:
    """
    Класс Vacancy, позволяет хранить информацию о вакансии в удобном виде.
    Обеспечивает возможность сравнения вакансий по средней зарабной плате.
    """

    __slots__ = (
        "name",
        "salary",
        "has_test",
        "experience",
        "requirement",
        "employer",
        "alternate_url",
        "avg_salary",
        "rates_dict",
    )

    def __init__(
        self,
        name: str,
        salary: None | dict,
        employer: str,
        requirement: str,
        experience: str,
        has_test: bool,
        alternate_url: str,
        rates_dict: dict,
    ) -> None:
        """
        Создаёт объект Vacancy.
        """

        self.name = name
        self.salary = self.set_salary(salary, rates_dict)
        self.avg_salary = self.calculate_avg_salary()
        self.requirement = self.remove_from_requirement(requirement)
        self.has_test = has_test
        self.experience = experience
        self.employer = employer
        self.alternate_url = alternate_url

    @staticmethod
    def set_salary(salary: dict | None, rates_dict: dict) -> dict:
        """
        Задаёт словарь с информацией по заработной плате.

        Args:
            salary: Словарь с информацией по заработной плате.
            rates_dict: Словарь с информацией по курсу валют для правильного перевода в рубли.
        Returns:
            Обновлённый словарь с информацией по заработной плате.
        """

        if isinstance(salary, dict):
            salary_from = salary.get("from") or 0
            salary_to = salary.get("to") or 0
            currency = salary.get("currency") if salary.get("currency") != "RUR" else "RUB"

            if currency != "RUB":
                rates = RatesAPI().get_currency_rate(currency, rates_dict)
                salary_from *= rates
                salary_to *= rates

            currency_salary = {"from": round(salary_from), "to": round(salary_to), "currency": "RUB"}
            return currency_salary

        else:
            currency_salary = {"from": 0, "to": 0, "currency": "RUB"}

        return currency_salary

    @staticmethod
    def remove_from_requirement(requirement: str) -> str:
        """
        Очистка строки требований от HTML тегов после обращения к API.

        Args:
            requirement: Ключевое слово, по которому будет проводиться поиск вакансий.
        Returns:
            Строка требований.
        """
        requirement = "" if not requirement else requirement
        new_requirement = requirement.replace("<highlighttext>", "")
        new_requirement = new_requirement.replace("</highlighttext>", "")
        return new_requirement

    def calculate_avg_salary(self) -> float | None | Any:
        """Рассчитывает среднюю зарплату для сравнений"""

        salary_from = float(self.salary.get("from"))
        salary_to = float(self.salary.get("to"))

        if salary_from != 0 and salary_to != 0:
            return (salary_from + salary_to) / 2

        if salary_from == 0:
            return salary_to

        if salary_to == 0:
            return salary_from
        return None

    def get_salary_info(self) -> str:
        """
        Возвращает форматированную информацию о зарплате.

        Returns:
            Форматированная информация о зарплате.
        """

        salary_from = float(self.salary.get("from"))
        salary_to = float(self.salary.get("to"))

        if salary_from + salary_to == 0:
            return "Не указана"

        currency = self.salary.get("currency")

        # Обработка различных вариантов
        if salary_from != 0 and salary_to != 0 and salary_from != salary_to:
            return f"{salary_from} - {salary_to} {currency}"

        if salary_from == 0:
            return f"до {salary_to} {currency}"

        if salary_to == 0:
            return f"от {salary_from} {currency}"
        return "Не указана"

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
            f"Требования: {self.requirement[:140]}\n"
            f"Опыт работы: {self.experience}\n"
            f"Тестовое задание: {has_test_info}\n"
            f"Ссылка: {self.alternate_url}\n"
        )


    def to_dict(self) -> dict:
        """Преобразует объект Vacancy в словарь для сериализации"""
        return {
            "name": self.name,
            "salary": self.salary,
            "has_test": self.has_test,
            "experience": {"name": self.experience},
            "snippet": {"requirement": self.requirement},
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
