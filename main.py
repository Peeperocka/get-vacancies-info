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
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2

    elif payment_from:
        return payment_from*1.2

    elif payment_to:
        return payment_to*0.8

    else:
        return


def avoid_dividing_by_zero(summ, count):
    '''avoids dividing by zero, if count == 0 returns N/D'''

    if count != 0:
        return int(summ / count)

    else:
        return 'N/D'


def print_tables(data, site):
    '''gets collected data and prints table with it'''

    table_config = [[
        'Language',
        'Average Salary',
        'Vacancies Found',
        'Vacancies Processed']
    ]

    for category, data in data.items():
        table_config.append([
            category,
            data['average_salary'],
            data['vacancies_found'],
            data['vacancies_processed']]
        )

    table = AsciiTable(table_config)
    table.title = site
    return table.table


def get_all_hh_vacancies(language):
    '''downloads all available vacancies'''

    page = 0
    pages = 1
    period = 30
    area_id = 1
    vacancies = []

    url = 'https://api.hh.ru/vacancies/'

    params = {
            'text': f'Программист {language}',
            'period': period,
            'area': area_id,
        }

    while page < pages:
        params = {
            'text': f'Программист {language}',
            'period': period,
            'area': area_id,
            'page': page
        }

        response = requests.get(url, params)
        response.raise_for_status()
        response_data = response.json()

        vacancies += response_data['items']
        pages = response_data['pages']
        page += 1

    return vacancies, response_data['found']


def predict_rub_salary_hh():
    '''main function to work with HH api'''
    jobs_data = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0

        try:
            vacancies, vacancies_found = get_all_hh_vacancies(language)

        except requests.exceptions.HTTPError:
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

        jobs_data[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': avoid_dividing_by_zero(
                salaries_summ,
                vacancies_processed
            )
            }

    print(print_tables(jobs_data, 'HeadHunter'))


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
            'page': page
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        response.raise_for_status()
        response_data = response.json()

        more_vacancies = response_data['more']

        vacancies += response_data['objects']
        page += 1

    return vacancies


def predict_rub_salary_sj(secretkey):
    '''main function to work with SuperJob API'''

    jobs_data = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0

        try:
            vacancies = get_all_sj_vacancies(language, secretkey)

        except requests.exceptions.HTTPError:
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

        jobs_data[language] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': vacancies_processed,
            'average_salary': avoid_dividing_by_zero(
                salaries_summ,
                vacancies_processed
            )
        }

    print(print_tables(jobs_data, 'SuperJob'))


if __name__ == '__main__':
    load_dotenv()

    sj_secretkey = os.environ['SUPERJOB_SECRETKEY']

    predict_rub_salary_hh()
    predict_rub_salary_sj(sj_secretkey)
