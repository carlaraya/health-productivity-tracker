import os
from dotenv import dotenv_values
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

default_args = {
    'owner'                 : 'airflow',
    'depend_on_past'        : False,
    'start_date'            : datetime(2022, 1, 3),
    'email_on_failure'      : False,
    'email_on_retry'        : False,
    'retries'               : 2,
    'retry_delay'           : timedelta(minutes=3)
}

with DAG('hpt_dag', default_args=default_args, schedule_interval="8 0 * * *", catchup=True) as dag:
    extract_task = BashOperator(
        task_id='hpt_extract',
        bash_command='cd /etl; python3 extract.py {{ yesterday_ds }}',
    )
    transform_load_task = BashOperator(
        task_id='hpt_transform_load',
        bash_command='cd /etl; python3 transform_load.py {{ yesterday_ds }}',
    )
    extract_task >> transform_load_task