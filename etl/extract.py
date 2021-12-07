import json
import sys
from datetime import datetime, timedelta
import fitbit
import calendar_parse

def main():
    isUntil = False
    args = sys.argv[:]
    if len(args) > 1 and args[1] == 'until':
        isUntil = True
        del args[1]

    if len(args) == 1 or args[1] == 'today':
        today = datetime.now()
        date = datetime.strftime(today, '%Y-%m-%d')
    elif args[1] == 'yesterday':
        yesterday = datetime.now() - timedelta(1)
        date = datetime.strftime(yesterday, '%Y-%m-%d')
    else:
        date = args[1]

    sources = ['fitbit', 'calendar']
    isFitbit = False
    isCalendar = False
    if 'all' in args or len(set(sources).intersection(set(args))) == 0:
        isFitbit = True
        isCalendar = True
    else:
        if 'fitbit' in args:
            isFitbit = True
        if 'calendar' in args:
            isCalendar = True

    if isFitbit:
        # Get dictionary of response objects
        if isUntil:
            responses = fitbit.request_log_until(date)
        else:
            responses = [fitbit.request_log(date)]

        # extract json from response object and dump to json file
        for responsesDict in responses:
            for logType in fitbit.FITBIT_DATA_PATHS:
                with open(f'data-lake/{responsesDict["date"]}-{logType}.json', 'w') as jsonFile:
                    jsonString = json.dumps(responsesDict[logType].json(), indent=2)
                    jsonFile.write(jsonString) 

    if isCalendar:
        if isUntil:
            eventsPerDay = calendar_parse.get_events_until(date)
        else:
            eventsPerDay = [calendar_parse.get_events(date)]
        for eventsDict in eventsPerDay:
            with open(f'data-lake/{eventsDict["date"]}-calendar.json', 'w') as jsonFile:
                jsonString = json.dumps(eventsDict, indent=2)
                jsonFile.write(jsonString) 


if __name__ == '__main__':
    main()
