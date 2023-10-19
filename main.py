import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable

POPULAR_LANGUAGES = [
    'JavaScript',
    'Java',
    'Ruby',
    'C++',
    'C#',
    'C',
    'Python',
    'Go',
    '1c'
]


def predict_rub_salary(payment_from, payment_to):
    '''predicting salary'''
    if payment_from != 0 and payment_to != 0:
        return (payment_from + payment_to) / 2
    elif payment_from != 0 and payment_from:
        return payment_from*1.2
    elif payment_to != 0 and payment_to:
        return payment_to*0.8
    else:
        print('Error')
        return


def print_tables(data, site):
    '''gets collected data and prints table with it'''

    table_data = [[
        'Language',
        'Average Salary',
        'Vacancies Found',
        'Vacancies Processed']
    ]

    for key, value in data.items():
        table_data.append([
            key,
            value['average_salary'],
            value['vacancies_found'],
            value['vacancies_processed']]
        )

    table = AsciiTable(table_data)
    table.title = site
    print(table.table)


def get_all_hh_vacancies(language):
    '''downloads all available vacancies'''

    period = 30
    area_id = 1
    vacancies = []
    url = 'https://api.hh.ru/vacancies/'

    params = {
            'text': f'Программист {language}',
            'period': period,
            'area': area_id,
        }

    response = requests.get(url, params)
    response.raise_for_status()

    pages = response.json()['pages']
    for page in range(pages):
        params = {
            'text': f'Программист {language}',
            'period': period,
            'area': area_id,
            'page': page
        }

        response = requests.get(url, params)
        response.raise_for_status()
        vacancies += response.json()['items']
    return vacancies


def get_hh_vacancies_info():
    '''main function to work with HH api'''
    vacancies_info = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0
        try:
            vacancies = get_all_hh_vacancies(language)
        except requests.exceptions.HTTPError:
            print('Error while getting all vacancies, continue.')
            continue

        for vacancy in vacancies:

            if (vacancy['salary'] and
                    vacancy['salary']['currency'] == 'RUR' and
                    vacancy['salary']['from'] and
                    vacancy['salary']['to']):

                vacancies_processed += 1
                salaries_summ += predict_rub_salary(
                    vacancy['salary']['from'],
                    vacancy['salary']['to']
                )

        vacancies_info[language] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': vacancies_processed,
            'average_salary': int(salaries_summ/vacancies_processed)
            }

    print_tables(vacancies_info, 'HeadHunter')


def get_all_sj_vacancies(language, secretkey):
    '''downloads all available vacancies'''
    vacancies = []
    more_vacancies = True
    page = 0

    url = 'https://api.superjob.ru/3.0/vacancies'

    headers = {
        'X-Api-App-Id': secretkey
    }

    while more_vacancies:

        params = {
            'keyword': f'Программист {language}',
            'town': 'Москва',
            'catalogues': 48,
            'page': page
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )
        response.raise_for_status()

        more_vacancies = response.json()['more']

        vacancies += response.json()['objects']
        page += 1

    return vacancies


def get_sj_vacancies_info(secretkey):
    '''main function to work with SuperJob API'''

    vacancies_info = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0

        try:
            vacancies = get_all_sj_vacancies(language, secretkey)

        except requests.exceptions.HTTPError:
            print('Error while getting all vacancies, continue.')
            continue

        for vacancy in vacancies:
            if ((vacancy['currency'] == 'rub') and
                    (vacancy['payment_from'] != 0 or
                     vacancy['payment_to'] != 0)):

                vacancies_processed += 1
                salaries_summ += predict_rub_salary(
                    vacancy['payment_from'],
                    vacancy['payment_to']
                )
        vacancies_info[language] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': vacancies_processed,
        }

        if vacancies_processed != 0:
            average_salary = int(salaries_summ/vacancies_processed)

            vacancies_info[language]['average_salary'] = average_salary

        else:
            vacancies_info[language]['average_salary'] = 'N/D'

    print_tables(vacancies_info, 'SuperJob')


if __name__ == '__main__':
    load_dotenv()

    sj_secretkey = os.environ['superjob_secretkey']

    get_hh_vacancies_info()
    get_sj_vacancies_info(sj_secretkey)
