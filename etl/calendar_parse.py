import os
import re
import ics
from datetime import datetime, timedelta

EVOLUTION_ICS_FILE = '/evolution/.local/share/evolution/calendar/%s/calendar.ics'
EVOLUTION_CONFIG_DIR = '/evolution/.config/evolution/sources/'

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

def date_range(start, end, step=1):
    currDate = datetime.strptime(start, '%Y-%m-%d')
    endDate = datetime.strptime(end, '%Y-%m-%d')
    while currDate <= endDate:
        yield datetime.strftime(currDate, '%Y-%m-%d')
        currDate += timedelta(step)
