# Мокирование окружения и зависимостей
from unittest.mock import patch, Mock

import pandas as pd

from src.classes.db_manager import DBManager


@patch('src.classes.db_manager.psycopg2.connect')
@patch('src.classes.db_manager.os.getenv')
def test_get_connection_data(mock_getenv, mock_connect, db_manager, mock_connection):
    """Тест получения данных для подключения к БД"""
    mock_conn, _ = mock_connection
    mock_connect.return_value = mock_conn

    # Настраиваем моки для переменных окружения
    mock_getenv.side_effect = lambda x: {
        "DATABASE_HOST": "localhost",
        "DATABASE_USER": "test_user",
        "DATABASE_PASSWORD": "test_password",
        "DATABASE_NAME": "test_db"
    }.get(x)

    # Вызываем тестируемый метод
    result = db_manager._DBManager__get_connection_data()

    # Проверяем результаты
    mock_connect.assert_called_once_with(
        host="localhost",
        database="test_db",
        user="test_user",
        password="test_password"
    )
    assert result == mock_conn


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_create_employers_database(mock_get_connection, db_manager, mock_connection):
    """Тест создания таблицы employers"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Вызываем тестируемый метод
    db_manager.create_employers_database()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "CREATE TABLE IF NOT EXISTS employers" in args[0]
    assert "employer_id int PRIMARY KEY" in args[0]
    assert "name varchar(100) NOT NULL" in args[0]
    assert "url varchar(100) NOT NULL" in args[0]

    # Проверяем, что было выполнено подтверждение транзакции
    mock_conn.commit.assert_called_once()


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_create_vacancies_database(mock_get_connection, db_manager, mock_connection):
    """Тест создания таблицы vacancies"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Вызываем тестируемый метод
    db_manager.create_vacancies_database()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "CREATE TABLE IF NOT EXISTS vacancies" in args[0]
    assert "name varchar(100) NOT NULL" in args[0]
    assert "has_test boolean NOT NULL" in args[0]
    assert "experience varchar(20) NOT NULL" in args[0]
    assert "requirements varchar(300) NOT NULL" in args[0]
    assert "employer_id int REFERENCES employers(employer_id)" in args[0]
    assert "url varchar(100) NOT NULL" in args[0]
    assert "avg_salary float NOT NULL" in args[0]

    # Проверяем, что было выполнено подтверждение транзакции
    mock_conn.commit.assert_called_once()


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_insert_employers(mock_get_connection, db_manager, mock_connection, mock_employer):
    """Тест вставки данных работодателей и вакансий"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Вызываем тестируемый метод
    db_manager.insert_employers([mock_employer])

    # Проверяем, что были выполнены правильные SQL-запросы
    assert mock_cursor.execute.call_count == 3  # 1 работодатель + 2 вакансии

    # Проверяем запрос на вставку работодателя
    calls = mock_cursor.execute.call_args_list
    employer_call = calls[0]
    assert employer_call[0][0] == "INSERT INTO employers (employer_id, name, url) VALUES (%s, %s, %s)"
    assert employer_call[0][1] == (123, "Test Employer", "https://hh.ru/employer/123")

    # Проверяем запросы на вставку вакансий
    vacancy_call_1 = calls[1]
    assert "INSERT INTO vacancies" in vacancy_call_1[0][0]
    assert vacancy_call_1[0][1] == (
        "Python Developer", True, "1-3 years", "Python, Django",
        123, "https://hh.ru/vacancy/456", 100000.0
    )

    vacancy_call_2 = calls[2]
    assert "INSERT INTO vacancies" in vacancy_call_2[0][0]
    assert vacancy_call_2[0][1] == (
        "Data Scientist", False, "3-5 years", "Python, ML",
        123, "https://hh.ru/vacancy/789", 150000.0
    )

    # Проверяем, что было выполнено подтверждение транзакции
    mock_conn.commit.assert_called_once()


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_companies_and_vacancies_count(mock_get_connection, db_manager, mock_connection):
    """Тест получения списка компаний и количества вакансий"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Настраиваем мок для возвращаемых данных
    mock_data = [("Company A", 10), ("Company B", 5)]
    mock_cursor.fetchall.return_value = mock_data

    # Вызываем тестируемый метод
    result = db_manager.get_companies_and_vacancies_count()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "SELECT DISTINCT(e.name), COUNT(v.name)" in args[0]
    assert "FROM employers e" in args[0]
    assert "JOIN vacancies v ON e.employer_id = v.employer_id" in args[0]
    assert "GROUP BY e.name" in args[0]

    # Проверяем, что результат - это DataFrame с правильными данными
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["company_name", "vacancies"]
    assert len(result) == 2
    assert result.iloc[0]["company_name"] == "Company A"
    assert result.iloc[0]["vacancies"] == 10


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_all_vacancies(mock_get_connection, db_manager, mock_connection):
    """Тест получения всех вакансий"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Настраиваем мок для возвращаемых данных
    mock_data = [
        ("Company A", "Python Developer", 100000.0, "https://hh.ru/vacancy/123"),
        ("Company B", "Data Scientist", 150000.0, "https://hh.ru/vacancy/456")
    ]
    mock_cursor.fetchall.return_value = mock_data

    # Вызываем тестируемый метод
    result = db_manager.get_all_vacancies()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "SELECT e.name AS employer_name, v.name AS vacancy_name, v.avg_salary, v.alternate_url" in args[0]
    assert "FROM employers e" in args[0]
    assert "JOIN vacancies v ON e.employer_id = v.employer_id" in args[0]

    # Проверяем, что результат - это DataFrame с правильными данными
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["employer_name", "vacancy_name", "avg_salary", "url"]
    assert len(result) == 2
    assert result.iloc[0]["employer_name"] == "Company A"
    assert result.iloc[0]["vacancy_name"] == "Python Developer"
    assert result.iloc[0]["avg_salary"] == 100000.0


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_avg_salary(mock_get_connection, db_manager, mock_connection):
    """Тест получения средней зарплаты"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Настраиваем мок для возвращаемых данных
    mock_data = (125000.0,)
    mock_cursor.fetchone.return_value = mock_data

    # Вызываем тестируемый метод
    result = db_manager.get_avg_salary()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "SELECT AVG(avg_salary)" in args[0]
    assert "FROM vacancies" in args[0]
    assert "WHERE avg_salary > 0" in args[0]

    # Проверяем, что результат - это DataFrame с правильными данными
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["average_salary"]
    assert result.iloc[0]["average_salary"] == 125000.0


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_vacancies_with_higher_salary(mock_get_connection, db_manager, mock_connection):
    """Тест получения вакансий с зарплатой выше средней"""
    mock_conn, mock_cursor = mock_connection
    mock_get_connection.return_value = mock_conn

    # Настраиваем мок для возвращаемых данных
    mock_data = [
        ("Company A", "Python Developer", 150000.0, True, "1-3 years", "Python", "https://hh.ru/vacancy/123"),
        ("Company B", "Data Scientist", 200000.0, False, "3-5 years", "ML", "https://hh.ru/vacancy/456")
    ]
    mock_cursor.fetchall.return_value = mock_data

    # Вызываем тестируемый метод
    result = db_manager.get_vacancies_with_higher_salary()

    # Проверяем, что был выполнен правильный SQL-запрос
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert "SELECT e.name, v.name, v.avg_salary, v.has_test, v.experience, v.requirements, v.url" in args[0]
    assert "FROM vacancies v" in args[0]
    assert "JOIN employers e on e.employer_id = v.employer_id" in args[0]
    assert "WHERE avg_salary > (SELECT AVG(avg_salary)" in args[0]
    assert "ORDER BY v.avg_salary DESC" in args[0]

    # Проверяем, что результат - это DataFrame с правильными данными
    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "employer_name", "vacancy_name", "avg_salary", "has_test",
        "experience", "requirements", "url"
    ]
    assert list(result.columns) == expected_columns
    assert len(result) == 2
    assert result.iloc[0]["employer_name"] == "Company A"
    assert result.iloc[0]["vacancy_name"] == "Python Developer"
    assert result.iloc[0]["avg_salary"] == 150000.0


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_vacancies_with_keyword_safe_query(mock_get_connection):
    """Тест безопасного параметризованного запроса с ключевым словом"""
    # Создаем мок-объекты для соединения и курсора
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_conn

    # Настраиваем моки для работы с контекстными менеджерами
    mock_conn.__enter__ = Mock(return_value=mock_conn)
    mock_conn.__exit__ = Mock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

    # Настраиваем мок для возвращаемых данных
    mock_data = [
        ("Company A", "Python Developer", 100000.0, True, "1-3 years", "Python", "https://hh.ru/vacancy/123")
    ]
    mock_cursor.fetchall.return_value = mock_data

    # Создаем экземпляр DBManager и вызываем тестируемый метод
    db_manager = DBManager()
    keyword = "Python"
    result = db_manager.get_vacancies_with_keyword(keyword)

    # Проверяем, что был выполнен параметризованный SQL-запрос
    mock_cursor.execute.assert_called_once()

    # Получаем аргументы вызова execute
    args, kwargs = mock_cursor.execute.call_args

    # Проверяем, что первый аргумент - это SQL-запрос с плейсхолдером %s
    sql_query = args[0]
    assert "LIKE %s" in sql_query
    assert f"LIKE '%{keyword}%'" not in sql_query  # Убеждаемся, что нет форматирования строк

    # Проверяем, что второй аргумент - это кортеж с параметром
    assert len(args) == 2
    assert isinstance(args[1], tuple)
    assert args[1] == (f"%{keyword}%",)

    # Проверяем, что результат - это DataFrame с правильными данными
    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "employer_name", "vacancy_name", "avg_salary", "has_test",
        "experience", "requirements", "url"
    ]
    assert list(result.columns) == expected_columns
    assert len(result) == 1
    assert result.iloc[0]["vacancy_name"] == "Python Developer"


@patch.object(DBManager, '_DBManager__get_connection_data')
def test_get_vacancies_with_keyword_sql_injection_attempt(mock_get_connection):
    """Тест, что метод защищен от попыток SQL-инъекций"""
    # Создаем мок-объекты для соединения и курсора
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_get_connection.return_value = mock_conn

    # Настраиваем моки для работы с контекстными менеджерами
    mock_conn.__enter__ = Mock(return_value=mock_conn)
    mock_conn.__exit__ = Mock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

    # Настраиваем мок для возвращаемых данных
    mock_data = []
    mock_cursor.fetchall.return_value = mock_data

    # Создаем экземпляр DBManager и вызываем тестируемый метод
    # с потенциально опасным ключевым словом
    db_manager = DBManager()
    malicious_keyword = "'; DROP TABLE vacancies; --"
    result = db_manager.get_vacancies_with_keyword(malicious_keyword)

    # Проверяем, что был выполнен параметризованный SQL-запрос
    mock_cursor.execute.assert_called_once()

    # Получаем аргументы вызова execute
    args, kwargs = mock_cursor.execute.call_args

    # Проверяем, что запрос использует плейсхолдер
    sql_query = args[0]
    assert "LIKE %s" in sql_query

    # Проверяем, что опасный ключевое слово передается как параметр
    # и не интерполируется непосредственно в запрос
    assert len(args) == 2
    assert isinstance(args[1], tuple)
    assert args[1] == (f"%{malicious_keyword}%",)

    # Убеждаемся, что опасный SQL не попадает в текст запроса
    assert "DROP TABLE" not in sql_query

    # Проверяем, что результат - это пустой DataFrame
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
