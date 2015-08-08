"""Module to allow financial dates calculations."""

import csv
import datetime
import os
import time

__all__ = ['brazilian_bank_days']

# The holidays data
holidays = []


def load_brazilian_holidays():
    """Loads the Brazilian holidays dates.

    We are using a CSV file with bare dates in it. The format is m/d/y.
    To update this list with newer information, check the Anbima website.
    The following URL may help: http://www.anbima.com.br/feriados/feriados.asp
    """
    path = os.path.join(os.path.dirname(__file__), 'holidays.csv')
    with open(path, 'r') as f:
        reader = csv.reader(f)
        reader.next()  # skip header
        for line in reader:
            assert len(line) == 2
            date = time.strptime(''.join(line), '%m/%d/%Y')
            date = datetime.date(date.tm_year, date.tm_mon, date.tm_mday)
            holidays.append(date)


def brazilian_bank_days(low, high):
    """Calculates the number if bank days between two dates.

    The interval includes the lower date, and excludes the high date.
    For instance, supposing all days between 3/1/2015 and 5/1/2015 are not
    weekends and holidays, this function should return 2.

    This is based on Brazilian national holiday calendar. We are discounting
    the weekends regardless of its holiday status.
    """
    if not holidays:
        load_brazilian_holidays()

    cnt = 0
    date = low
    delta = datetime.timedelta(days=1)
    while date < high:
        if date.weekday() not in [5, 6] and date not in holidays:
            cnt = cnt + 1
        date = date + delta
    return cnt
