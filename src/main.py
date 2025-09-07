# Точка входа пользователя
import json

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


# employers = HeadHunterAPI().get_list_of_employers(['Банк ВТБ', 'VK', 'DNS', 'IBS', 'Adict', 'HeadHunter'])
employers = HeadHunterAPI().get_list_of_employers(["IBS"])
employers_list = Employer.cast_to_object_list(employers, rates_data)

print(employers_list[0].vacancies[0])
# for i in employers_list:
#     print(i)
#     # print(i.vacancies)
#     for j in i.vacancies:
#         print(j['name'])
#
#     print(' \n\n')
