"""
Handles Fitbit OAuth credentials & requests.
"""
import base64
import requests
from datetime import datetime, timedelta

with open('secrets/FITBIT_ACCESS_TOKEN.secret', 'r') as secretFile:
    FITBIT_ACCESS_TOKEN = secretFile.read().strip()

with open('secrets/FITBIT_USER_ID.secret', 'r') as secretFile:
    FITBIT_USER_ID = secretFile.read().strip()

JOIN_DATE = '2021-11-24'

FITBIT_DOMAIN = 'https://api.fitbit.com'
FITBIT_DATA_PATHS = {
        'sleep': f'/1.2/user/{FITBIT_USER_ID}/sleep/date/%s.json',
        'activity': f'/1/user/{FITBIT_USER_ID}/activities/date/%s.json'
        }
HEADERS = { 'Authorization': f'Bearer {FITBIT_ACCESS_TOKEN}' }

def request_log_until(date, logType='all'):
    """
    Returns: an array of dictionaries containing a date & response object for each log type in FITBIT_DATA_PATHS starting from JOIN_DATE until the date parameter (excluding)
    Example:
    [
      {'date': '2021-11-24', 'sleep': <response object>, 'activity': <response object>},
      {'date': '2021-11-25', 'sleep': <response object>, 'activity': <response object>},
      {'date': '2021-11-26', 'sleep': <response object>, 'activity': <response object>},
    ]
    """
    return [request_log(d, logType) for d in date_range(JOIN_DATE, date)]

def request_log(date, logType='all'):
    if logType == 'all':
        return {logType: request_log_of_type(date, logType) for logType in FITBIT_DATA_PATHS} | {'date': date}
    else:
        return {logType: request_log_of_type(date, logType)} | {'date': date}

def request_log_of_type(date, logType):
    print(f'Requesting FitBit log of {logType} at {date}')
    url = FITBIT_DOMAIN + FITBIT_DATA_PATHS[logType] % date
    return requests.get(url, headers=HEADERS)


def date_range(start, end, step=1):
    currDate = datetime.strptime(start, '%Y-%m-%d')
    endDate = datetime.strptime(end, '%Y-%m-%d')
    while currDate < endDate:
        yield datetime.strftime(currDate, '%Y-%m-%d')
        currDate += timedelta(step)
