import json
from datetime import datetime, timedelta
import argparse
import psycopg2

import fitbit
import calendar_parse

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
    parser.add_argument('-t', '--sourcetype', type=str,
                        help='Format: ' + '|'.join(fitbit.FITBIT_DATA_PATHS) + '. Fitbit source type to query, e.g. "sleep" or "activity". Will query all source types if unspecified.')
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

    args.sourcetype = args.sourcetype or 'all'

    # dictionary with data sources as keys and booleans as values (whether user wants to query such data source).
    # Example: {'fitbit': True, 'calendar': False}
    willQuery = {source: source == args.datasource or not args.datasource for source in DATA_SOURCES}

    connection, cur = connect_to_db()

    if willQuery['fitbit']:
        tuplesDict = fitbit.transform_date_range(args.startdate, args.date, args.sourcetype)
        fitbit.load(tuplesDict, connection, cur)

    if willQuery['calendar']:
        tuplesDict = calendar_parse.transform_date_range(args.startdate, args.date)
        calendar_parse.load(tuplesDict, connection, cur)

    if connection:
        cur.close()
        connection.close()

def connect_to_db():
    with open('secrets/POSTGRES_PASSWORD.secret', 'r') as secretFile:
        POSTGRES_PASSWORD = secretFile.read().strip()
    print('Connecting to DB')
    connection = psycopg2.connect(user='etl', password=POSTGRES_PASSWORD, host='db', port='5432', database='warehouse')
    cur = connection.cursor()
    cur.execute('SELECT version()');

    print('Connected to: ')
    db_version = cur.fetchone()
    print(db_version)

    return (connection, cur)

if __name__ == '__main__':
    main()
