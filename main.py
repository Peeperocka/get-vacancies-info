import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable
from contextlib import suppress

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

POPULAR_LANGUAGESs = [
    'Java',
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

    if count:
        return int(summ / count)

    else:
        return 'N/D'


def create_table(vacancies_info, site):
    '''gets collected data and prints table with it'''

    table_config = [[
        'Language',
        'Average Salary',
        'Vacancies Found',
        'Vacancies Processed']
    ]

    for category, data in vacancies_info.items():
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

    while page < pages:
        params = {
            'text': f'Программист {language}',
            'period': period,
            'area': area_id,
            'page': page
        }

        response = requests.get(url, params)
        response.raise_for_status()
        about_vacancies = response.json()

        vacancies += about_vacancies['items']
        pages = about_vacancies['pages']
        page += 1

    return vacancies, about_vacancies['found']


def predict_rub_salary_hh():
    '''main function to work with HH api'''
    programming_jobs_hh = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0

        vacancies, vacancies_found = get_all_hh_vacancies(language)

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

        programming_jobs_hh[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': avoid_dividing_by_zero(
                salaries_summ,
                vacancies_processed
                )
            }

    return programming_jobs_hh


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
        about_vacancies = response.json()

        more_vacancies = about_vacancies['more']

        vacancies += about_vacancies['objects']
        page += 1

    return vacancies, about_vacancies['total']


def predict_rub_salary_sj(secretkey):
    '''main function to work with SuperJob API'''

    programming_jobs_sj = {}

    for language in POPULAR_LANGUAGES:

        vacancies_processed = 0
        salaries_summ = 0

        vacancies, vacancies_found = get_all_sj_vacancies(language, secretkey)

        for vacancy in vacancies:
            if ((vacancy['currency'] == 'rub') and
                    (vacancy['payment_from'] or
                     vacancy['payment_to'])):

                vacancies_processed += 1
                salaries_summ += predict_rub_salary(
                    vacancy['payment_from'],
                    vacancy['payment_to']
                )

        programming_jobs_sj[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': avoid_dividing_by_zero(
                salaries_summ,
                vacancies_processed
            )
        }

    return programming_jobs_sj


if __name__ == '__main__':
    load_dotenv()

    sj_secretkey = os.environ['SUPERJOB_SECRETKEY']

    with suppress(requests.exceptions.HTTPError):
        rub_salary_sj = predict_rub_salary_sj(sj_secretkey)
        # rub_salary_hh = predict_rub_salary_hh()

        print(create_table(rub_salary_sj, 'Superjob'))
        # print(create_table(predict_rub_salary_hh, 'HeadHunter'))
