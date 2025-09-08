# Тесты метода __connect_to_api
import sys
from unittest.mock import Mock, patch

import pytest
import requests

from src.classes.headhunter_api import HeadHunterAPI


@patch("src.classes.headhunter_api.requests.get")
def test_connect_to_api_success(mock_get, hh_api, mock_employer_response):
    """Тест успешного подключения к API"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_employer_response
    mock_get.return_value = mock_response

    result = hh_api._HeadHunterAPI__connect_to_api(api="https://api.hh.ru/employers", api_parameters={"text": "test"})

    assert result == mock_employer_response["items"]
    mock_get.assert_called_once()


@patch("src.classes.headhunter_api.requests.get")
def test_connect_to_api_failure_status_code(mock_get, hh_api):
    """Тест подключения к API с ошибкой статус-кода"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = hh_api._HeadHunterAPI__connect_to_api(api="https://api.hh.ru/employers", api_parameters={"text": "test"})

    assert result == []
    mock_get.assert_called_once()


@patch("src.classes.headhunter_api.requests.get")
def test_connect_to_api_exception(mock_get, hh_api):
    """Тест подключения к API с исключением"""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    result = hh_api._HeadHunterAPI__connect_to_api(api="https://api.hh.ru/employers", api_parameters={"text": "test"})

    assert result == []
    mock_get.assert_called_once()


# Тесты метода get_employer
@patch.object(HeadHunterAPI, "_HeadHunterAPI__connect_to_api")
def test_get_employer_success(mock_connect, hh_api, mock_employer_response):
    """Тест успешного получения работодателя"""
    mock_connect.return_value = mock_employer_response["items"]

    # Мокируем вызов get_vacancies_from_employer
    with patch.object(hh_api, "get_vacancies_from_employer") as mock_get_vacancies:
        mock_get_vacancies.return_value = [{"id": "111", "name": "Test Vacancy"}]

        result = hh_api.get_employer("Test Employer")

        assert result is not None
        assert result["id"] == "123"
        assert result["name"] == "Test Employer"
        assert "employer_vacancies" in result
        mock_get_vacancies.assert_called_once_with("123")


@patch.object(HeadHunterAPI, "_HeadHunterAPI__connect_to_api")
def test_get_employer_not_found(mock_connect, hh_api, mock_empty_response):
    """Тест случая, когда работодатель не найден"""
    mock_connect.return_value = mock_empty_response["items"]

    result = hh_api.get_employer("Non Existent Employer")

    assert result is None


@patch.object(HeadHunterAPI, "_HeadHunterAPI__connect_to_api")
def test_get_vacancies_from_employer_empty(mock_connect, hh_api, mock_empty_response):
    """Тест получения пустого списка вакансий"""
    mock_connect.return_value = mock_empty_response["items"]

    result = hh_api.get_vacancies_from_employer("123")

    assert result == []


# Тесты метода get_list_of_employers
@patch("src.classes.headhunter_api.tqdm")
@patch.object(HeadHunterAPI, "get_employer")
def test_get_list_of_employers_success(mock_get_employer, mock_tqdm, hh_api):
    """Тест успешного получения списка работодателей"""
    # Настраиваем моки
    mock_employer = {"id": "123", "name": "Test Employer", "employer_vacancies": []}
    mock_get_employer.return_value = mock_employer

    mock_progress_bar = Mock()
    mock_tqdm.return_value = mock_progress_bar
    mock_progress_bar.__enter__ = Mock(return_value=mock_progress_bar)
    mock_progress_bar.__exit__ = Mock(return_value=None)

    # Вызываем тестируемый метод
    employers_list = ["Test Employer", "Another Employer"]
    result = hh_api.get_list_of_employers(employers_list)

    # Проверяем результаты
    assert len(result) == 2
    assert result[0] == mock_employer
    assert result[1] == mock_employer
    assert mock_get_employer.call_count == 2
    mock_tqdm.assert_called_once_with(employers_list, desc="Обработка", ascii=True, file=sys.stderr)


@patch("src.classes.headhunter_api.tqdm")
@patch.object(HeadHunterAPI, "get_employer")
def test_get_list_of_employers_partial_success(mock_get_employer, mock_tqdm, hh_api):
    """Тест получения списка работодателей с частичным успехом"""
    # Настраиваем моки
    mock_employer = {"id": "123", "name": "Test Employer", "employer_vacancies": []}
    mock_get_employer.side_effect = [mock_employer, None]  # Первый успех, второй - нет

    mock_progress_bar = Mock()
    mock_tqdm.return_value = mock_progress_bar
    mock_progress_bar.__enter__ = Mock(return_value=mock_progress_bar)
    mock_progress_bar.__exit__ = Mock(return_value=None)

    # Вызываем тестируемый метод
    employers_list = ["Test Employer", "Non Existent Employer"]
    result = hh_api.get_list_of_employers(employers_list)

    # Проверяем результаты
    assert len(result) == 1
    assert result[0] == mock_employer
    assert mock_get_employer.call_count == 2


# Тесты обработки ошибок
@patch.object(HeadHunterAPI, "_HeadHunterAPI__connect_to_api")
def test_get_vacancies_from_employer_api_error(mock_connect, hh_api):
    """Тест обработки ошибки API при получении вакансий"""
    mock_connect.return_value = []  # Пустой ответ

    result = hh_api.get_vacancies_from_employer("123")

    assert result == []


# Параметризованные тесты для различных сценариев
@pytest.mark.parametrize(
    "status_code, expected_result",
    [
        (200, [{"id": "123", "name": "Test Employer"}]),
        (404, []),
        (500, []),
        (403, []),
    ],
)
@patch("src.classes.headhunter_api.requests.get")
def test_connect_to_api_different_status_codes(mock_get, hh_api, status_code, expected_result):
    """Параметризованный тест для различных статус-кодов API"""
    mock_response = Mock()
    mock_response.status_code = status_code

    if status_code == 200:
        mock_response.json.return_value = {"items": [{"id": "123", "name": "Test Employer"}]}
    else:
        mock_response.json.return_value = {"items": []}

    mock_get.return_value = mock_response

    result = hh_api._HeadHunterAPI__connect_to_api(api="https://api.hh.ru/employers", api_parameters={"text": "test"})

    assert result == expected_result
