import os
from dotenv import dotenv_values
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

default_args = {
    'owner'                 : 'airflow',
    'depend_on_past'        : False,
    'start_date'            : datetime(2021, 11, 25),
    'email_on_failure'      : True,
    'email_on_retry'        : True,
    'retries'               : 2,
    'retry_delay'           : timedelta(minutes=3),
    'email'                 : [os.environ['AIRFLOW_MAIL_TO']]
}

with DAG('hpt_dag', default_args=default_args, schedule_interval="26 3 * * *", catchup=True) as dag:
    extract_task = BashOperator(
        task_id='hpt_extract',
        bash_command='cd /etl; python3 extract.py {{ ds }}',
    )
    transform_load_task = BashOperator(
        task_id='hpt_transform_load',
        bash_command='cd /etl; python3 transform_load.py {{ ds }}',
    )
    extract_task >> transform_load_task
