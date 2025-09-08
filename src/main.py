# Точка входа пользователя

from src.classes.db_manager import DBManager
from src.classes.employer import Employer
from src.classes.headhunter_api import HeadHunterAPI
from src.classes.rates_api import RatesAPI

# 0. Начало работы, запуск апи цбрф о валютах и проверка если файл есть, то загрузить иначе получить по апи - готово
# 1. Ввод работадателей (компаний), которые интересны пользователю
# 2. Предложение об последюущих опциях

# 3.1 Вывести список компаний и кол-во активных вакансий
# 3.2 Вывести среднюю зп по ВСЕМ вакансиям

# 4. Список всех вакансий: название, компания, зп, ссылка
# 5. Список вакансий у которых зп выше чем средняя из всего списка
# 6. Список вакансий у которых в названии есть ключевые слова пользователя

# 7. После выполнения пунктов 4-6 предлагать вывести в консоль или сохранить в файл
# 8. После выполенния пунктов 3.1 - 3.2 выводить результат в консоль

# =========== Реализация работы программы =========== #
# ===========   Заполнение данных в БД    =========== #


# Получение данных о курсе валют, для корректного перевода и сравнение вакансий в компаниях.
rates_data = RatesAPI.load_rates_data("current_rates.json")


# employers = HeadHunterAPI().get_list_of_employers(['Банк ВТБ', 'VK', 'DNS', 'IBS', 'Adict', 'HeadHunter', 'Первый Бит','АРС', '2GIS', 'Далее', 'T1 Иннотех', 'Контур', 'ИНК', 'Слата'])
# employers = HeadHunterAPI().get_list_of_employers(["VK", "DNS"])
# employers_list = Employer.cast_to_object_list(employers, rates_data)



# Добавить данные
# DBManager().create_employers_database()
# DBManager().create_vacancies_database()
# DBManager().insert_employers(employers_list)

# DBManager().get_companies_and_vacancies_count()
# DBManager().get_all_vacancies()
# DBManager().get_avg_salary()
# DBManager().get_vacancies_with_higher_salary()
DBManager().get_vacancies_with_keyword("python")
