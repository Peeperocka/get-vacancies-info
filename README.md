# get vacancies info

This project was made to help people who are searching for job or just the curious one

## Installation

### Installing dependecies

Python3 should already be installed.
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:

```
pip install -r requirements.txt
```

### Enviroment

Create `.env` file with this variable:

- `superjob_secretkey=your secret key`. You can get it [there](https://api.superjob.ru/)

## Run

### Running scripts with console

To run program you must head to files' direcory and type:

```
python main.py
```

### Some info about prints

If script runs into the error, it will print:

- `'Error while predicting salary'` if it runs into error while it analyzes salaries

- `'Error while getting all HH vacancies, continue.'` if it runs into an error while getting vacancies info from `HeadHunter`

- `'Error while getting all sj vacancies, continue.'` if it runs into an error while getting vacancies info from `Superjob`

## Notes

You can change programming languages to search by changing global variable `POPULAR_LANGUAGES`