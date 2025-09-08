# Тесты инициализации
from unittest.mock import Mock, patch

from src.classes.vacancy import Vacancy


@patch('src.classes.vacancy.RatesAPI')
def test_vacancy_initialization(mock_rates_api, sample_full_vacancy_data, sample_short_rates_data):
    """Тест инициализации объекта Vacancy"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 1.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy(
        name=sample_full_vacancy_data["name"],
        salary=sample_full_vacancy_data["salary"],
        employer=sample_full_vacancy_data["employer"]["name"],
        requirements=sample_full_vacancy_data["snippet"]["requirement"],
        experience=sample_full_vacancy_data["experience"]["name"],
        has_test=sample_full_vacancy_data["has_test"],
        alternate_url=sample_full_vacancy_data["alternate_url"],
        rates_data=sample_short_rates_data
    )

    assert vacancy.name == "Python Developer"
    assert vacancy.employer == "Test Company"
    assert vacancy.experience == "1-3 years"
    assert vacancy.has_test is True
    assert vacancy.alternate_url == "https://hh.ru/vacancy/123"
    assert "Django" in vacancy.requirements
    assert "<highlighttext>" not in vacancy.requirements


@patch('src.classes.vacancy.RatesAPI')
def test_vacancy_initialization_no_salary(mock_rates_api, sample_vacancy_no_salary, sample_short_rates_data):
    """Тест инициализации Vacancy без зарплаты"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 1.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy(
        name=sample_vacancy_no_salary["name"],
        salary=sample_vacancy_no_salary["salary"],
        employer=sample_vacancy_no_salary["employer"]["name"],
        requirements=sample_vacancy_no_salary["snippet"]["requirement"],
        experience=sample_vacancy_no_salary["experience"]["name"],
        has_test=sample_vacancy_no_salary["has_test"],
        alternate_url=sample_vacancy_no_salary["alternate_url"],
        rates_data=sample_short_rates_data
    )

    assert vacancy.name == "Python Developer"
    assert vacancy.salary_info["from"] == "Не указано"
    assert vacancy.salary_info["to"] == "Не указано"
    assert vacancy.salary_info["average"] == 0.0


# Тесты методов обработки зарплаты
def test_get_salary_currency():
    """Тест преобразования кодов валют"""
    assert Vacancy.get_salary_currency("RUR") == "RUB"
    assert Vacancy.get_salary_currency("BYR") == "BYN"
    assert Vacancy.get_salary_currency("USD") == "USD"
    assert Vacancy.get_salary_currency("EUR") == "EUR"


@patch('src.classes.vacancy.RatesAPI')
def test_update_currency_value(mock_rates_api):
    """Тест конвертации валюты в рубли"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 75.0
    mock_rates_api.return_value = mock_rates_instance

    result = Vacancy.update_currency_value(1000, "USD", {})
    assert result == 75000.0

    result = Vacancy.update_currency_value(1000, "RUB", {})
    assert result == 1000.0


def test_calculate_avg_salary():
    """Тест расчета средней зарплаты"""
    # Обе границы указаны
    assert Vacancy.calculate_avg_salary(100000, 150000) == 125000.0

    # Указана только нижняя граница
    assert Vacancy.calculate_avg_salary(100000, "Не указано") == 100000

    # Указана только верхняя граница
    assert Vacancy.calculate_avg_salary("Не указано", 150000) == 150000

    # Ничего не указано
    assert Vacancy.calculate_avg_salary("Не указано", "Не указано") == 0.0


@patch('src.classes.vacancy.RatesAPI')
def test_update_salary_info(mock_rates_api, sample_short_rates_data):
    """Тест обновления информации о зарплате"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 75.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy.__new__(Vacancy)  # Создаем экземпляр без вызова __init__

    # Тест с полной информацией о зарплате
    salary_data = {"from": 1000, "to": 2000, "currency": "USD"}
    result = vacancy.update_salary_info(salary_data, sample_short_rates_data)

    assert result["from"] == 75000.0  # 1000 * 75
    assert result["to"] == 150000.0  # 2000 * 75
    assert result["currency"] == "RUB"
    assert result["average"] == 112500.0  # (75000 + 150000) / 2

    # Тест с отсутствующей зарплатой
    result = vacancy.update_salary_info(None, sample_short_rates_data)
    assert result["from"] == "Не указано"
    assert result["to"] == "Не указано"
    assert result["currency"] == "RUB"
    assert result["average"] == 0.0


# Тесты обработки требований
def test_remove_from_requirements():
    """Тест очистки требований от HTML-тегов"""
    requirements = "Python <highlighttext>Django</highlighttext> experience"
    result = Vacancy.remove_from_requirements(requirements)
    assert result == "Python Django experience"

    # Пустые требования
    result = Vacancy.remove_from_requirements("")
    assert result == ""

    # Требования без тегов
    result = Vacancy.remove_from_requirements("Python experience")
    assert result == "Python experience"


# Тесты строкового представления
@patch('src.classes.vacancy.RatesAPI')
def test_get_salary_info(mock_rates_api, sample_full_vacancy_data, sample_short_rates_data):
    """Тест форматирования информации о зарплате"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 1.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy(
        name=sample_full_vacancy_data["name"],
        salary=sample_full_vacancy_data["salary"],
        employer=sample_full_vacancy_data["employer"]["name"],
        requirements=sample_full_vacancy_data["snippet"]["requirement"],
        experience=sample_full_vacancy_data["experience"]["name"],
        has_test=sample_full_vacancy_data["has_test"],
        alternate_url=sample_full_vacancy_data["alternate_url"],
        rates_data=sample_short_rates_data
    )

    result = vacancy.get_salary_info()
    assert "100000 - 150000 RUB" in result


@patch('src.classes.vacancy.RatesAPI')
def test_str_representation(mock_rates_api, sample_full_vacancy_data, sample_short_rates_data):
    """Тест строкового представления вакансии"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 1.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy(
        name=sample_full_vacancy_data["name"],
        salary=sample_full_vacancy_data["salary"],
        employer=sample_full_vacancy_data["employer"]["name"],
        requirements=sample_full_vacancy_data["snippet"]["requirement"],
        experience=sample_full_vacancy_data["experience"]["name"],
        has_test=sample_full_vacancy_data["has_test"],
        alternate_url=sample_full_vacancy_data["alternate_url"],
        rates_data=sample_short_rates_data
    )

    result = str(vacancy)

    assert "Python Developer" in result
    assert "Test Company" in result
    assert "1-3 years" in result
    assert "Есть" in result  # has_test = True
    assert "https://hh.ru/vacancy/123" in result


# Тесты преобразования в словарь
@patch('src.classes.vacancy.RatesAPI')
def test_to_dict(mock_rates_api, sample_full_vacancy_data, sample_short_rates_data):
    """Тест преобразования Vacancy в словарь"""
    mock_rates_instance = Mock()
    mock_rates_instance.get_currency_rate.return_value = 1.0
    mock_rates_api.return_value = mock_rates_instance

    vacancy = Vacancy(
        name=sample_full_vacancy_data["name"],
        salary=sample_full_vacancy_data["salary"],
        employer=sample_full_vacancy_data["employer"]["name"],
        requirements=sample_full_vacancy_data["snippet"]["requirement"],
        experience=sample_full_vacancy_data["experience"]["name"],
        has_test=sample_full_vacancy_data["has_test"],
        alternate_url=sample_full_vacancy_data["alternate_url"],
        rates_data=sample_short_rates_data
    )

    result = vacancy.to_dict()

    assert result["name"] == "Python Developer"
    assert result["employer"]["name"] == "Test Company"
    assert result["experience"]["name"] == "1-3 years"
    assert result["has_test"] is True
    assert result["alternate_url"] == "https://hh.ru/vacancy/123"
    assert "salary" in result