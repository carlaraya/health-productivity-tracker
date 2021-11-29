import json
import sys
import fitbit
from datetime import datetime, timedelta

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

    # Get dictionary of response objects
    if isUntil:
        responses = fitbit.request_log_until(date)
    else:
        responses = [fitbit.request_log(date)]

    for responsesDict in responses:
        for logType in fitbit.FITBIT_DATA_PATHS:
            with open(f'data-lake/{responsesDict["date"]}-{logType}.json', 'w') as jsonFile:
                jsonString = json.dumps(responsesDict[logType].json(), indent=2)
                jsonFile.write(jsonString) 

if __name__ == '__main__':
    main()
