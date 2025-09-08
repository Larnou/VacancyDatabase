# Точка входа пользователя
import pandas as pd

from src.classes.db_manager import DBManager
from src.classes.employer import Employer
from src.classes.file_manager import FileManager
from src.classes.headhunter_api import HeadHunterAPI
from src.classes.rates_api import RatesAPI


def download_data_to_database() -> None:
    """
    Подключение по API HeadHunter и загрузка данных по выбранным работадателям и их вакансиям в базу данных PostgreSQL.
    """

    # Получение данных о курсе валют, для корректного перевода и сравнение вакансий в компаниях.
    rates_data = RatesAPI.load_rates_data("current_rates.json")

    employers_names = input("\nВведите интересные вам вакансии через запятую: ").split(',')
    # employers_names = ['Банк ВТБ', 'VK', 'DNS', 'IBS', 'Adict', 'HeadHunter', 'Первый Бит', 'АРС',
    #                    '2GIS', 'Далее', 'T1 Иннотех', 'Контур', 'ИНК', 'Слата']
    employers_names = [x.strip() for x in employers_names]

    employers = HeadHunterAPI().get_list_of_employers(employers_names)
    employers_list = Employer.cast_to_object_list(employers, rates_data)

    print('\nИнформация по работадателям и вакансиям готова. Начинается загрузка в Базу Данных')
    # Заполнение данных в БД
    DBManager().create_employers_database()
    print('Таблица для работадателей создана!')

    DBManager().create_vacancies_database()
    print('Таблица для вакансий создана!')

    DBManager().insert_employers(employers_list)
    print('\nДанные успешно загружены. Для работы выберите вариант: "2. Загрузить данные из базы данных"')


def save_data_to_file(data: pd.DataFrame) -> None:
    """
    Сохранение данных в файл с расширением .json.
    """
    print("\nВыберите дальнейшие действие:")
    print("1. Сохранить результат в файл.")
    print("2. Закончить работу.")

    while True:
        choice = input("\nВыберите дальнейшее действие (1 или 2): ").strip()

        if choice == "1":
            filename = input("Введите название файла: ")
            FileManager.save_to_json(data, filename + '.json')
            break

        elif choice == "2":
            break

        else:
            print("Неверный выбор. Попробуйте ещё раз.")

    return None


def load_from_database() -> None:
    """
    Загрузка данных с базы данных PostgreSQL.
    """

    """"""
    print("\nВыберите дальнейшее действие:")
    print("1. Получить информацию о компаниях и количестве открытых вакансий в них.")
    print("2. Получить список всех вакансий.")
    print("3. Получить среднюю заработную платы, среди вакансий, в которых она была указана.")
    print("4. Получить список вакансий с заработной платой выше чем средняя по всем вакансиям.")
    print("5. Получить список вакансий в навзании которых содержится слово.")
    print("6. Закончить работу.")

    while True:
        choice = input("\nВыберите действие (1-5): ").strip()

        if choice == "1":
            request_result = DBManager().get_companies_and_vacancies_count()
            save_data_to_file(request_result)
            break

        elif choice == "2":
            request_result = DBManager().get_all_vacancies()
            save_data_to_file(request_result)
            break

        elif choice == "3":
            request_result = DBManager().get_avg_salary()
            save_data_to_file(request_result)
            break

        elif choice == "4":
            request_result = DBManager().get_vacancies_with_higher_salary()
            save_data_to_file(request_result)
            break

        elif choice == "5":
            keyword = input("\nВведите слово, которое должно содержаться в названии вакансии: ").strip()
            request_result = DBManager().get_vacancies_with_keyword(keyword)
            save_data_to_file(request_result)
            break

        elif choice == "6":
            break

        else:
            print("Неверный выбор. Попробуйте ещё раз.")

    return None


def user_interaction() -> None:
    """
    Функция для взаимодействия с пользователем.
    """

    print("\nДоброго времени суток! Выберите дальнейшее действие:")
    print("1. Загрузить в базу данных данные по новым компаниям")
    print("2. Загрузить данные из базы данных")

    while True:
        choice = input("\nВыберите действие (1 или 2): ").strip()

        if choice == "1":
            download_data_to_database()
            break

        elif choice == "2":
            load_from_database()
            break

        else:
            print("Неверный выбор. Попробуйте ещё раз.")

    return None


if __name__ == "__main__":
    user_interaction()
