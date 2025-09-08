import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from pandas import DataFrame
from psycopg2._psycopg import connection

from src.classes.employer import Employer


class DBManager:

    @staticmethod
    def __get_connection_data() -> connection:
        """
        Получение данных для подключения к базе данных.

        Returns:
            Подключение psycopg2.connection
        """
        load_dotenv()
        host = os.getenv("DATABASE_HOST")
        user = os.getenv("DATABASE_USER")
        password = os.getenv("DATABASE_PASSWORD")
        name = os.getenv("DATABASE_NAME")
        return psycopg2.connect(host=host, database=name, user=user, password=password)

    def create_employers_database(self) -> None:
        """Создание базы данных "Работадатели"."""

        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                    CREATE TABLE IF NOT EXISTS employers
                        (
                            employer_id int PRIMARY KEY,
                            name varchar(100) NOT NULL,
                            url varchar(100) NOT NULL
                        );
                    """
                    )
                    conn.commit()
        finally:
            conn.close()

    def create_vacancies_database(self) -> None:
        """Создание базы данных "Вакансии"."""
        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                    CREATE TABLE IF NOT EXISTS vacancies
                        (
                            name varchar(100) NOT NULL,
                            has_test boolean NOT NULL,
                            experience varchar(20) NOT NULL,
                            requirements varchar(300) NOT NULL,
                            employer_id int REFERENCES employers(employer_id),
                            url varchar(100) NOT NULL,
                            avg_salary float NOT NULL
                        );
                    """
                    )
                    conn.commit()
        finally:
            conn.close()

    def insert_employers(self, employers_list: list[Employer]) -> None:
        """
        Вставка значений в таблицы баз данных "Работадатели" и "Вакансии"
        из списка данных о работадателях и их вакансиях.

        Args:
            employers_list: Список данных о работадателях и их вакансиях.
        """

        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    for employer in employers_list:
                        # Выполнение запроса
                        insert_query = "INSERT INTO employers (employer_id, name, url) VALUES (%s, %s, %s)"
                        cur.execute(insert_query, (employer.employer_id, employer.name, employer.url))

                        for vacancy in employer.vacancies:
                            insert_query = (
                                "INSERT INTO vacancies (name, has_test, experience, requirements, "
                                "employer_id, url, avg_salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                            )
                            cur.execute(
                                insert_query,
                                (
                                    vacancy.name,
                                    vacancy.has_test,
                                    vacancy.experience,
                                    vacancy.requirements,
                                    employer.employer_id,
                                    vacancy.alternate_url,
                                    vacancy.salary_info["average"],
                                ),
                            )

                    conn.commit()
        finally:
            conn.close()

    def get_companies_and_vacancies_count(self) -> DataFrame:
        """Запрос получения списка компаний и количества открытых вакансий в каждой компании."""
        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                        SELECT DISTINCT(e.name), COUNT(v.name)
                        FROM employers e
                        JOIN vacancies v ON e.employer_id = v.employer_id
                        GROUP BY e.name
                        """
                    )
                    conn.commit()

                    data = cur.fetchall()

                    dataframe = pd.DataFrame(data, columns=["company_name", "vacancies"])
                    print(dataframe)
                    return dataframe

        finally:
            conn.close()

    def get_all_vacancies(self) -> DataFrame:
        """Запрос получения списка открытых вакансий во всех компаниях."""
        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                        SELECT e.name AS employer_name, v.name AS vacancy_name, v.avg_salary, v.alternate_url
                        FROM employers e
                        JOIN vacancies v ON e.employer_id = v.employer_id
                        """
                    )
                    conn.commit()

                    data = cur.fetchall()
                    dataframe = pd.DataFrame(data, columns=["employer_name", "vacancy_name", "avg_salary", "url"])
                    print(dataframe)
                    return dataframe
        finally:
            conn.close()

    def get_avg_salary(self) -> DataFrame:
        """Запрос получения средней зарплаты по всем вакансиях во всех компаниях."""
        # Создание подключения
        conn = self.__get_connection_data()

        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                        SELECT AVG(avg_salary)
                        FROM vacancies
                        WHERE avg_salary > 0
                        """
                    )
                    conn.commit()

                    data = cur.fetchone()

                    dataframe = pd.DataFrame(data, columns=["average_salary"])
                    print(dataframe)
                    return dataframe

        finally:
            conn.close()

    def get_vacancies_with_higher_salary(self) -> DataFrame:
        """Запрос получения вакансий с уровнем зароботной платы выше
        чем средняя зарплата по всем вакансиях во всех компаниях."""
        # Создание подключения
        conn = self.__get_connection_data()
        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        """
                        SELECT e.name, v.name, v.avg_salary, v.has_test, v.experience, v.requirements, v.url
                        FROM vacancies v
                        JOIN employers e on e.employer_id = v.employer_id
                        WHERE avg_salary > (SELECT AVG(avg_salary)
                                            FROM vacancies
                                            WHERE avg_salary > 0)
                        ORDER BY v.avg_salary DESC;
                    """
                    )
                    conn.commit()

                    data = cur.fetchall()
                    dataframe = pd.DataFrame(
                        data,
                        columns=[
                            "employer_name",
                            "vacancy_name",
                            "avg_salary",
                            "has_test",
                            "experience",
                            "requirements",
                            "url",
                        ],
                    )
                    print(dataframe)
                    return dataframe
        finally:
            conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> DataFrame:
        """Запрос получения вакансий в названии которых есть указанное слово."""
        # Создание подключения
        conn = self.__get_connection_data()
        try:
            with conn:
                with conn.cursor() as cur:
                    # SQL запросы ниже:

                    cur.execute(
                        f"""
                        SELECT e.name, v.name, v.avg_salary, v.has_test, v.experience, v.requirements, v.url
                        FROM vacancies v
                        JOIN employers e on e.employer_id = v.employer_id
                        WHERE v.name LIKE '%{keyword}%'
                        ORDER BY v.avg_salary DESC;
                    """
                    )
                    conn.commit()

                    data = cur.fetchall()
                    dataframe = pd.DataFrame(
                        data,
                        columns=[
                            "employer_name",
                            "vacancy_name",
                            "avg_salary",
                            "has_test",
                            "experience",
                            "requirements",
                            "url",
                        ],
                    )
                    print(dataframe)
                    return dataframe
        finally:
            conn.close()
