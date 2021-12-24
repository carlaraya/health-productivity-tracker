import os
import re
import ics
import json
from datetime import datetime, timedelta

EVOLUTION_ICS_FILE = '/evolution/.local/share/evolution/calendar/%s/calendar.ics'
EVOLUTION_CONFIG_DIR = '/evolution/.config/evolution/sources/'

DB_TABLES_CORRECT_ORDER = ['todo_summaries', 'todo_tasks']
DB_COLUMNS = {
        'todo_summaries': ['date', 'done_tasks', 'total_tasks'],
        'todo_tasks': ['name', 'is_done', 'todo_summary_id']
        }

def get_calendar_names_to_ids_dict():
    # generate dict with displayname mapped to id
    sourceFnames = os.listdir(EVOLUTION_CONFIG_DIR)
    files = ((open(EVOLUTION_CONFIG_DIR + fname, 'r').read(), fname) for fname in sourceFnames if fname.endswith('.source'))
    calendarFiles = ((f, fn) for f, fn in files if '[Calendar]' in f)

    calendarsDict = {
            re.search('DisplayName=(.*)', f).group(1): fn.replace('.source', '')
            for f, fn in calendarFiles
            }
    return calendarsDict

def get_events_date_range(startdate, date):
    return (get_events(d) for d in date_range(startdate, date))

def get_events(date):
    print('Mining data from calendar for date: ' + date)
    calendarsDict = get_calendar_names_to_ids_dict()
    # assign todo and done calendar ids to variable
    calendars = ['Todo', 'Done']
    calendarFnames = (EVOLUTION_ICS_FILE % calendarsDict[c] for c in calendars)
    calendarObjs = (ics.Calendar(open(fn, 'r').read()) for fn in calendarFnames)
    calendarEventsToday = (
            [ev for ev in obj.events if date == ev.begin.format('YYYY-MM-DD')]
            for obj in calendarObjs)
    eventsDict = {
            calendars[i]: [ev.name for ev in evs]
            for i, evs in enumerate(calendarEventsToday)}

    return eventsDict | {
            'date': date,
            'doneTasks': len(eventsDict['Done']),
            'totalTasks': len(eventsDict['Todo']) + len(eventsDict['Done'])
            }

def transform_date_range(startdate, date):
    """
    Returns: a dictionary with keys as postgre db table names and values as lists of tuples, ready to be inserted into the db.
    Example:
    {
        'sleep_records': [(foo1, bar1, baz1, ...), (foo2, bar2, baz2, ...) ...],
        'sleep_summaries': [(foo3, bar3, baz3, ...), ...]
    }
    """
    tuplesDict = {}
    listOfDicts = (transform(d) for d in date_range(startdate, date))
    for d in listOfDicts:
        for k, v in d.items():
            if k in tuplesDict:
                tuplesDict[k] += v
            else:
                tuplesDict[k] = v
    return tuplesDict

def transform(date):
    print('Transforming calendar json data for date: ' + date)
    fname = f'data-lake/{date}-calendar.json'
    with open(fname, 'r') as fobj:
        jsonDict = json.load(fobj)
        todoTasks = [(t, 'f', date) for t in jsonDict['Todo']] + \
                    [(t, 't', date) for t in jsonDict['Done']]
        todoSummaries = [(date, jsonDict['doneTasks'], jsonDict['totalTasks'])]
    return {'todo_tasks': todoTasks, 'todo_summaries': todoSummaries}

def load(tuplesDict, connection, cur):
    for dbName in DB_TABLES_CORRECT_ORDER:
        if dbName in tuplesDict:
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
