import json
from datetime import datetime, timedelta

from helpers import handle_args, DATA_LAKE_PATH
import fitbit
import calendar_parse

def main():
    args, willQuery = handle_args()

    if willQuery['fitbit']:
        # Get dictionary of response objects
        responses = fitbit.request_log_date_range(args.startdate, args.date, args.sourcetype or 'all')

        # extract json from response object and dump to json file
        for responsesDict in responses:
            for logType in ([args.sourcetype] if args.sourcetype else fitbit.FITBIT_DATA_PATHS):
                fname = f'{DATA_LAKE_PATH}{responsesDict["date"]}-{logType}.json'
                print('Saving to file: ' + fname)
                with open(fname, 'w') as jsonFile:
                    jsonString = json.dumps(responsesDict[logType].json(), indent=2)
                    jsonFile.write(jsonString) 

    if willQuery['calendar']:
        # Get dictionary of calendar summary per day
        eventsPerDay = calendar_parse.get_events_date_range(args.startdate, args.date)

        for eventsDict in eventsPerDay:
            fname = f'{DATA_LAKE_PATH}{eventsDict["date"]}-calendar.json'
            print('Saving to file: ' + fname)
            with open(fname, 'w') as jsonFile:
                jsonString = json.dumps(eventsDict, indent=2)
                jsonFile.write(jsonString) 


if __name__ == '__main__':
    main()
