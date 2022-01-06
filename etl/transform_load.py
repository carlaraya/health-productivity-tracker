import json
import os
from datetime import datetime, timedelta
import argparse
import psycopg2

from helpers import handle_args, DATA_LAKE_PATH
import fitbit
import calendar_parse

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')

def main():
    args, willQuery = handle_args()

    connection, cur = connect_to_db()

    if willQuery['fitbit']:
        tuplesDict = fitbit.transform_date_range(args.startdate, args.date, args.sourcetype or 'all')
        fitbit.load(tuplesDict, connection, cur)

    if willQuery['calendar']:
        tuplesDict = calendar_parse.transform_date_range(args.startdate, args.date)
        calendar_parse.load(tuplesDict, connection, cur)

    if connection:
        cur.close()
        connection.close()

def connect_to_db():
    print('Connecting to DB')
    connection = psycopg2.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD, host='db', port='5432', database='warehouse')
    cur = connection.cursor()
    cur.execute('SELECT version()');

    print('Connected to: ')
    db_version = cur.fetchone()
    print(db_version)

    return (connection, cur)

if __name__ == '__main__':
    main()
