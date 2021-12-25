"""
Handles Fitbit OAuth credentials & requests.
"""
import base64
import requests
import json
from datetime import datetime, timedelta
from functools import reduce

with open('/run/secrets/FITBIT_ACCESS_TOKEN', 'r') as secretFile:
    FITBIT_ACCESS_TOKEN = secretFile.read().strip()

with open('/run/secrets/FITBIT_USER_ID', 'r') as secretFile:
    FITBIT_USER_ID = secretFile.read().strip()

FITBIT_DOMAIN = 'https://api.fitbit.com'
FITBIT_DATA_PATHS = {
        'sleep': f'/1.2/user/{FITBIT_USER_ID}/sleep/date/%s.json',
        'activity': f'/1/user/{FITBIT_USER_ID}/activities/date/%s.json'
        }
HEADERS = { 'Authorization': f'Bearer {FITBIT_ACCESS_TOKEN}' }

DB_TABLES_CORRECT_ORDER = ['sleep_summaries', 'sleep_records', 'activity_summaries']
DB_COLUMNS = {
        'sleep_records': ['start_time', 'end_time', 'wake_time', 'rem_time', 'light_time', 'deep_time', 'minutes_asleep', 'efficiency_score', 'is_main_sleep', 'sleep_summary_id'],
        'sleep_summaries': ['date', 'total_sleep_records', 'total_minutes_asleep', 'main_sleep_total_minutes_asleep'],
        'activity_summaries': ['date', 'sedentary_minutes', 'lightly_active_minutes', 'fairly_active_minutes', 'very_active_minutes']
        }

def request_log_date_range(startdate, date, sourceType='all'):
    """
    Returns: an array of dictionaries containing a date & response object for each log type in FITBIT_DATA_PATHS starting from JOIN_DATE until the date parameter (excluding)
    Example:
    [
      {'date': '2021-11-24', 'sleep': <response object>, 'activity': <response object>},
      {'date': '2021-11-25', 'sleep': <response object>, 'activity': <response object>},
      {'date': '2021-11-26', 'sleep': <response object>, 'activity': <response object>},
    ]
    """
    return (request_log(d, sourceType) for d in date_range(startdate, date))

def request_log(date, sourceType='all'):
    if sourceType == 'all':
        return {sourceType: request_log_of_type(date, sourceType) for sourceType in FITBIT_DATA_PATHS} | {'date': date}
    else: 
        return {sourceType: request_log_of_type(date, sourceType)} | {'date': date}

def request_log_of_type(date, sourceType):
    print(f'Requesting FitBit log of {sourceType} for date: {date}')
    url = FITBIT_DOMAIN + FITBIT_DATA_PATHS[sourceType] % date
    return requests.get(url, headers=HEADERS)

def transform_date_range(startdate, date, sourceType='all'):
    """
    Returns: a dictionary with keys as postgre db table names and values as lists of tuples, ready to be inserted into the db.
    Example:
    {
        'sleep_records': [(foo1, bar1, baz1, ...), (foo2, bar2, baz2, ...) ...],
        'sleep_summaries': [(foo3, bar3, baz3, ...), ...]
    }
    """
    tuplesDict = {}
    listOfDicts = (transform(d, sourceType) for d in date_range(startdate, date))
    for d in listOfDicts:
        for k, v in d.items():
            if k in tuplesDict:
                tuplesDict[k] += v
            else:
                tuplesDict[k] = v
    return tuplesDict
    

def transform(date, sourceType='all'):
    if sourceType == 'all':
        sourceTypes = list(FITBIT_DATA_PATHS)
    else:
        sourceTypes = [sourceType]
    return {tableName: listOfTuples for sourceType in sourceTypes for tableName, listOfTuples in transform_by_type(date, sourceType).items()}

def transform_by_type(date, sourceType):
    print(f'Transforming json file of {sourceType} for date: {date}')
    fname = f'data-lake/{date}-{sourceType}.json'
    returnDict = {}
    with open(fname, 'r') as fobj:
        jsonDict = json.load(fobj)
        if sourceType == 'sleep':
            sleepRecords = [(
                s['startTime'],
                s['endTime'],
                (s['levels']['summary'].get('wake') or
                    s['levels']['summary']['awake'])['minutes'],
                (s['levels']['summary'].get('rem') or {'minutes': 0})['minutes'],
                (s['levels']['summary'].get('light') or
                    s['levels']['summary']['asleep'])['minutes'],
                (s['levels']['summary'].get('deep') or {'minutes': 0})['minutes'],
                s['minutesAsleep'],
                s['efficiency'],
                s['isMainSleep'],
                date 
                ) for s in jsonDict['sleep']]

            # indexes
            minutesAsleep = 6
            isMainSleep = 8

            totalSleepRecords = len(sleepRecords)
            if totalSleepRecords == 0:
                sleepSummary = [(
                    date,
                    totalSleepRecords,
                    None,
                    None
                    )]
            else:
                sleepSummary = [(
                    date,
                    totalSleepRecords,
                    sum([s[minutesAsleep] for s in sleepRecords]),
                    sum([s[minutesAsleep] for s in sleepRecords if s[isMainSleep]])
                    )]
            returnDict = {
                'sleep_records': sleepRecords,
                'sleep_summaries': sleepSummary
                }
        elif sourceType == 'activity':
            activitySummaries = [(
                date,
                jsonDict['summary']['sedentaryMinutes'],
                jsonDict['summary']['lightlyActiveMinutes'],
                jsonDict['summary']['fairlyActiveMinutes'],
                jsonDict['summary']['veryActiveMinutes'],
                )]
            returnDict = {
                'activity_summaries': activitySummaries
                }
    return returnDict

def load(tuplesDict, connection, cur):
    for dbName in DB_TABLES_CORRECT_ORDER:
        if dbName in tuplesDict and len(tuplesDict[dbName]):
            tuples = tuplesDict[dbName]
            columnsStr = '(' + ','.join(DB_COLUMNS[dbName]) + ')'
            percentSes = '(' + ', '.join(['%s'] * len(DB_COLUMNS[dbName])) + ')' # returns '(%s, %s, %s, ...)'
            tuplesStr = ', '.join([cur.mogrify(percentSes, t).decode('utf-8') for t in tuples])
            queryStr = f'INSERT INTO {dbName}{columnsStr} VALUES {tuplesStr} ON CONFLICT DO NOTHING'
            print(f'Attempting to insert {len(tuples)} record(s) into table {dbName}')
            cur.execute(queryStr)
            connection.commit()


def date_range(start, end, step=1):
    currDate = datetime.strptime(start, '%Y-%m-%d')
    endDate = datetime.strptime(end, '%Y-%m-%d')
    while currDate <= endDate:
        yield datetime.strftime(currDate, '%Y-%m-%d')
        currDate += timedelta(step)
