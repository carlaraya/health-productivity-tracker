import argparse
import fitbit
from datetime import datetime, timedelta

EARLIEST_DATE = '2021-11-25'
DATA_SOURCES = ['fitbit', 'calendar']
DATA_LAKE_PATH = 'data-lake/'

def new_arg_parser():
    parser = argparse.ArgumentParser()
    return parser

def insert_date_arguments(parser):
    parser.add_argument('date', type=str,
                        help='Format: YYYY-MM-DD|yesterday|today. Specify the end date parameter of the query, or the only date to query if start-date is not specified. Can also be set to "yesterday" or "today".')
    parser.add_argument('-s', '--startdate', type=str,
                        help='Format: YYYY-MM-DD|earliest. Specify the start date parameter of the query. Can be set to "earliest", in order to query starting from the very first record.')
    parser.add_argument('-d', '--datasource', type=str,
                        help='Format: ' + '|'.join(DATA_SOURCES) + '. Data source to query, whether it is "fitbit", or "calendar". Will query all sources if unspecified.')
    parser.add_argument('-t', '--sourcetype', type=str,
                        help='Format: ' + '|'.join(fitbit.FITBIT_DATA_PATHS) + '. Fitbit source type to query, e.g. "sleep" or "activity". Will query all source types if unspecified.')

def parse_args(parser):
    args = parser.parse_args()
    return args

def clean_args(args):
    # Clean up args. Turn date args into real dates, instead of words like 'today' or 'yesterday'.
    if args.date == 'today':
        today = datetime.now()
        args.date = datetime.strftime(today, '%Y-%m-%d')
    elif args.date == 'yesterday':
        yesterday = datetime.now() - timedelta(1)
        args.date = datetime.strftime(yesterday, '%Y-%m-%d')

    # dictionary with data sources as keys and booleans as values (whether user wants to query such data source).
    # Example: {'fitbit': True, 'calendar': False}
    willQuery = {source: source == args.datasource or not args.datasource for source in DATA_SOURCES}

    if args.startdate == 'earliest':
        args.startdate = EARLIEST_DATE
    elif not args.startdate:
        args.startdate = args.date

    return willQuery

def handle_args():
    parser = new_arg_parser()
    insert_date_arguments(parser)
    args = parse_args(parser)
    willQuery = clean_args(args)
    return (args, willQuery)
