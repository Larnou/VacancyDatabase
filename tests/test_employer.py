from unittest.mock import patch

import pytest

from src.classes.employer import Employer


# Тесты инициализации
def test_employer_initialization(sample_vacancy_data):
    """Тест инициализации объекта Employer"""
    employer = Employer(
        employer_id=456, name="Test Employer", url="https://hh.ru/employer/456", vacancies=[sample_vacancy_data]
    )

    assert employer.employer_id == 456
    assert employer.name == "Test Employer"
    assert employer.url == "https://hh.ru/employer/456"
    assert employer.vacancies == [sample_vacancy_data]


# Тесты преобразования в словарь
def test_to_dict_method(sample_vacancy_data):
    """Тест преобразования Employer в словарь"""
    employer = Employer(
        employer_id=456, name="Test Employer", url="https://hh.ru/employer/456", vacancies=[sample_vacancy_data]
    )

    result = employer.to_dict()

    assert result == {"employer_id": 456, "name": "Test Employer", "url": "https://hh.ru/employer/456", "vacancies": 1}


# Тесты строкового представления
def test_str_representation(sample_vacancy_data):
    """Тест строкового представления Employer"""
    employer = Employer(
        employer_id=456, name="Test Employer", url="https://hh.ru/employer/456", vacancies=[sample_vacancy_data]
    )

    result = str(employer)

    assert "Employer(id=456, name=Test Employer" in result
    assert "vacancies=1)" in result


# Тесты преобразования списка словарей в объекты
@patch("src.classes.employer.Vacancy.cast_to_object_list")
def test_cast_to_object_list(mock_cast, sample_employer_data, sample_rates_dict, mock_vacancy_list):
    """Тест преобразования списка словарей в список объектов Employer"""
    mock_cast.return_value = mock_vacancy_list

    result = Employer.cast_to_object_list([sample_employer_data], sample_rates_dict)

    # Проверяем, что метод Vacancy.cast_to_object_list был вызван
    mock_cast.assert_called_once_with(sample_employer_data["employer_vacancies"], sample_rates_dict)

    # Проверяем результат
    assert len(result) == 1
    assert isinstance(result[0], Employer)
    assert result[0].employer_id == 456
    assert result[0].name == "Test Employer"
    assert result[0].url == "https://hh.ru/employer/456"
    assert result[0].vacancies == mock_vacancy_list


# Параметризованные тесты для различных сценариев
@pytest.mark.parametrize(
    "employer_id, name, url, vacancies_count",
    [
        (1, "Company A", "https://company-a.com", 0),
        (2, "Company B", "https://company-b.com", 5),
        (3, "Company C", "https://company-c.com", 100),
    ],
)
def test_employer_with_different_data(employer_id, name, url, vacancies_count):
    """Параметризованный тест для Employer с разными данными"""
    vacancies = [{"id": i} for i in range(vacancies_count)]

    employer = Employer(employer_id=employer_id, name=name, url=url, vacancies=vacancies)

    assert employer.employer_id == employer_id
    assert employer.name == name
    assert employer.url == url
    assert len(employer.vacancies) == vacancies_count

    # Проверяем метод to_dict
    dict_result = employer.to_dict()
    assert dict_result["vacancies"] == vacancies_count


# Тесты краевых случаев
def test_employer_with_empty_vacancies():
    """Тест Employer с пустым списком вакансий"""
    employer = Employer(
        employer_id=789, name="Empty Vacancies Employer", url="https://empty-employer.com", vacancies=[]
    )

    assert len(employer.vacancies) == 0
    assert employer.to_dict()["vacancies"] == 0
    assert "vacancies=0" in str(employer)
