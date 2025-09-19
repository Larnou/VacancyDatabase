from unittest.mock import Mock

import pandas as pd
import pytest

from src.classes.db_manager import DBManager
from src.classes.employer import Employer
from src.classes.headhunter_api import HeadHunterAPI
from src.classes.rates_api import RatesAPI
from src.classes.vacancy import Vacancy


# Фикстуры для тестовых данных
@pytest.fixture
def sample_vacancy_data():
    """Фикстура с примером данных вакансии"""
    return {
        "id": 123,
        "name": "Test Vacancy",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "alternate_url": "https://hh.ru/vacancy/123",
        "snippet": {"requirement": "Python experience", "responsibility": "Development"},
        "experience": {"name": "1-3 years"},
        "employment": {"name": "full"},
    }


@pytest.fixture
def sample_employer_data(sample_vacancy_data):
    """Фикстура с примером данных работодателя"""
    return {
        "id": 456,
        "name": "Test Employer",
        "alternate_url": "https://hh.ru/employer/456",
        "employer_vacancies": [sample_vacancy_data],
    }


@pytest.fixture
def sample_rates_dict():
    """Фикстура с примером курсов валют"""
    return {"USD": 75.0, "EUR": 85.0, "RUR": 1.0}


@pytest.fixture
def mock_vacancy_list():
    """Фикстура с мок-объектами вакансий"""
    mock_vacancy = Mock(spec=Vacancy)
    mock_vacancy.to_dict.return_value = {"title": "Test Vacancy", "salary": 100000}
    return [mock_vacancy]


# Фикстуры для тестовых данных
@pytest.fixture
def hh_api():
    """Фикстура для создания экземпляра HeadHunterAPI"""
    return HeadHunterAPI()


@pytest.fixture
def mock_employer_response():
    """Фикстура с мок-ответом API для работодателей"""
    return {
        "items": [
            {"id": "123", "name": "Test Employer", "alternate_url": "https://hh.ru/employer/123"},
            {"id": "456", "name": "Another Employer", "alternate_url": "https://hh.ru/employer/456"},
        ]
    }


@pytest.fixture
def mock_vacancies_response():
    """Фикстура с мок-ответом API для вакансий"""
    return {
        "items": [
            {
                "id": "111",
                "name": "Test Vacancy 1",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "alternate_url": "https://hh.ru/vacancy/111",
            },
            {
                "id": "222",
                "name": "Test Vacancy 2",
                "salary": {"from": 120000, "to": 180000, "currency": "USD"},
                "alternate_url": "https://hh.ru/vacancy/222",
            },
        ]
    }


@pytest.fixture
def mock_empty_response():
    """Фикстура с пустым ответом API"""
    return {"items": []}


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})


@pytest.fixture
def empty_dataframe():
    return pd.DataFrame()


@pytest.fixture
def complex_dataframe():
    return pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Product A", "Product B"],
            "price": [19.99, 25.50],
            "available": [True, False],
            "tags": [["tag1", "tag2"], ["tag3"]],
        }
    )


@pytest.fixture
def sample_rates_data():
    """Фикстура с примером данных о курсах валют"""
    return {
        "USD": {
            "ID": "R01235",
            "NumCode": "840",
            "CharCode": "USD",
            "Nominal": 1,
            "Name": "Доллар США",
            "Value": 75.5,
            "Previous": 74.8,
        },
        "EUR": {
            "ID": "R01239",
            "NumCode": "978",
            "CharCode": "EUR",
            "Nominal": 1,
            "Name": "Евро",
            "Value": 85.2,
            "Previous": 84.5,
        },
        "JPY": {
            "ID": "R01820",
            "NumCode": "392",
            "CharCode": "JPY",
            "Nominal": 100,
            "Name": "Японских иен",
            "Value": 68.9,
            "Previous": 68.2,
        },
    }


@pytest.fixture
def mock_api_response(sample_rates_data):
    """Фикстура с мок-ответом API ЦБ РФ"""
    return {
        "Valute": sample_rates_data,
        "Date": "2023-10-01T11:30:00+03:00",
        "PreviousDate": "2023-09-30T11:30:00+03:00",
        "PreviousURL": "//previous-url",
        "Timestamp": "2023-10-01T11:30:00+03:00",
    }


@pytest.fixture
def sample_short_rates_data():
    """Фикстура с примером данных о курсах валют"""
    return {
        "USD": {"Value": 75.0, "Nominal": 1},
        "EUR": {"Value": 85.0, "Nominal": 1},
        "RUB": {"Value": 1.0, "Nominal": 1}
    }

@pytest.fixture
def sample_full_vacancy_data():
    """Фикстура с примером данных вакансии"""
    return {
        "name": "Python Developer",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "employer": {"name": "Test Company"},
        "snippet": {"requirement": "Python experience <highlighttext>Django</highlighttext>"},
        "experience": {"name": "1-3 years"},
        "has_test": True,
        "alternate_url": "https://hh.ru/vacancy/123"
    }

@pytest.fixture
def sample_vacancy_no_salary():
    """Фикстура с примером вакансии без зарплаты"""
    return {
        "name": "Python Developer",
        "salary": None,
        "employer": {"name": "Test Company"},
        "snippet": {"requirement": "Python experience"},
        "experience": {"name": "1-3 years"},
        "has_test": False,
        "alternate_url": "https://hh.ru/vacancy/123"
    }


@pytest.fixture
def db_manager():
    """Фикстура для создания экземпляра DBManager"""
    return DBManager()


@pytest.fixture
def mock_employer():
    """Фикстура с мок-объектом Employer"""
    employer = Mock(spec=Employer)
    employer.employer_id = 123
    employer.name = "Test Employer"
    employer.url = "https://hh.ru/employer/123"

    # Создаем мок-вакансии
    vacancy1 = Mock(spec=Vacancy)
    vacancy1.name = "Python Developer"
    vacancy1.has_test = True
    vacancy1.experience = "1-3 years"
    vacancy1.requirements = "Python, Django"
    vacancy1.alternate_url = "https://hh.ru/vacancy/456"
    vacancy1.salary_info = {"average": 100000.0}

    vacancy2 = Mock(spec=Vacancy)
    vacancy2.name = "Data Scientist"
    vacancy2.has_test = False
    vacancy2.experience = "3-5 years"
    vacancy2.requirements = "Python, ML"
    vacancy2.alternate_url = "https://hh.ru/vacancy/789"
    vacancy2.salary_info = {"average": 150000.0}

    employer.vacancies = [vacancy1, vacancy2]
    return employer


@pytest.fixture
def mock_connection():
    """Фикстура с мок-соединением к БД"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor

    # Настраиваем контекстный менеджер для соединения
    mock_conn.__enter__ = Mock(return_value=mock_conn)
    mock_conn.__exit__ = Mock(return_value=None)

    # Настраиваем контекстный менеджер для курсора
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=None)

    return mock_conn, mock_cursor