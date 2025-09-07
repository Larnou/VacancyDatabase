from typing import Any


class Employer:
    """
    Класс Employer, позволяет хранить информацию о работадателе и его доступных вакансиях.
    """

    def __init__(self, employer_id: int, name: str, url: str, vacancies: list[dict[str, Any]]):
        """
        Создаёт объект Employer.
        """
        self.employer_id = employer_id
        self.name = name
        self.url = url
        self.vacancies = vacancies

    @staticmethod
    def cast_to_object_list(dict_list: list[dict[str, Any]]) -> list:
        """
        Переводит список словарей в список объектов класса Employer.

        Args:
            dict_list: Список словарей.

        Returns:
            Список объектов Employer.
        """
        employers_list = []

        for employer in dict_list:
            new_employer = Employer(
                employer_id=employer["id"],
                name=employer["name"],
                url=employer["alternate_url"],
                vacancies=employer["employer_vacancies"],
            )
            employers_list.append(new_employer)

        return employers_list

    def to_dict(self) -> dict:
        """Преобразует объект Employer в словарь для сериализации"""
        return {"employer_id": self.employer_id, "name": self.name, "url": self.url, "vacancies": len(self.vacancies)}

    def __str__(self) -> str:
        """
        Строковое представление работадателя: Название, Ссылка, Ссылка на вакансии,

        Returns:
            Строковое представление работадателя.
        """

        return f"Employer(id={self.employer_id}, name={self.name}, url={self.url}, vacancies={len(self.vacancies)})"
