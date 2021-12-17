import json
import sys
from datetime import datetime, timedelta
import fitbit
import calendar_parse
import argparse

EARLIEST_DATE = '2021-11-25'
DATA_SOURCES = ['fitbit', 'calendar']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('date', type=str,
                        help='Format: YYYY-MM-DD|yesterday|today. Specify the end date parameter of the query, or the only date to query if start-date is not specified. Can also be set to "yesterday" or "today".')
    parser.add_argument('-s', '--startdate', type=str,
                        help='Format: YYYY-MM-DD|earliest. Specify the start date parameter of the query. Can be set to "earliest", in order to query starting from the very first record.')
    parser.add_argument('-d', '--datasource', type=str,
                        help='Format: ' + '|'.join(DATA_SOURCES) + '. Data source to query, whether it is "fitbit", or "calendar". Will query all sources if unspecified.')
    args = parser.parse_args()

    # Clean up args. Turn date args into real dates, instead of words like 'today' or 'yesterday'.
    if args.date == 'today':
        today = datetime.now()
        args.date = datetime.strftime(today, '%Y-%m-%d')
    elif args.date == 'yesterday':
        yesterday = datetime.now() - timedelta(1)
        args.date = datetime.strftime(yesterday, '%Y-%m-%d')

    if args.startdate == 'earliest':
        args.startdate = EARLIEST_DATE
    elif not args.startdate:
        args.startdate = args.date

    # dictionary with data sources as keys and booleans as values (whether user wants to query such data source).
    # Example: {'fitbit': True, 'calendar': False}
    willQuery = {source: source == args.datasource or not args.datasource for source in DATA_SOURCES}


    if willQuery['fitbit']:
        # Get dictionary of response objects
        responses = fitbit.request_log_date_range(args.startdate, args.date)

        # extract json from response object and dump to json file
        for responsesDict in responses:
            for logType in fitbit.FITBIT_DATA_PATHS:
                fname = f'data-lake/{responsesDict["date"]}-{logType}.json'
                print('Saving to file: ' + fname)
                with open(fname, 'w') as jsonFile:
                    jsonString = json.dumps(responsesDict[logType].json(), indent=2)
                    jsonFile.write(jsonString) 

    if willQuery['calendar']:
        # Get dictionary of calendar summary per day
        eventsPerDay = calendar_parse.get_events_date_range(args.startdate, args.date)

        for eventsDict in eventsPerDay:
            fname = f'data-lake/{eventsDict["date"]}-calendar.json'
            print('Saving to file: ' + fname)
            with open(fname, 'w') as jsonFile:
                jsonString = json.dumps(eventsDict, indent=2)
                jsonFile.write(jsonString) 


if __name__ == '__main__':
    main()
