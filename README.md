# Personal Health and Productivity Tracker

An ETL pipeline & data visualization for my sleep & todo list data.
- Extracts todo list data from my Evolution calendar & sleep data from the Fitbit API & stores it all as json files
- Transforms the json data into sql-friendly tuples
- Loads the data into a PostgreSQL DB.
- Uses Metabase to visualize the data. Shows correlations between daily sleep time and productivity.
  - Productivity is quantified with the formula `finished_tasks * (finished_tasks / planned_tasks)`
- Airflow server runs ETL pipeline daily
  - Makes sure tasks are run sequentially and enforces task dependencies (e.g. transform and load scripts cannot be run if extraction step errors)
  - Logs failures to help with bugfixing

## Installation
1. Install Docker and Docker Compose.
1. Install Evolution. Make sure Evolution has two calendars named `Todo` and `Done`. Evolution data files should be in `~/.local/share/evolution/` and `~/.config/evolution/`. Or if installing on a cloud server, use a program to sync with the data from the local device.
1. Get Fitbit credentials from https://dev.fitbit.com/apps/oauthinteractivetutorial. Select "Implicit Grant Flow".
1. For the Airflow Gmail credentials follow this tutorial to generate an app password https://support.google.com/mail/answer/185833?hl=en
1. `secrets/` should contain all the sensitive data. Add these files in `secrets/`. env file format: (replace the keywords in < > with the appropriate text. Do not include the symbols themselves, of course.)
    - `fitbit.env`
        ```
        FITBIT_ACCESS_TOKEN=<fitbit token>
        FITBIT_USER_ID=<fitbit id>
        ```
    - `metabase.env`
        ```
        MB_DB_PASS=<postgres password>
        MB_DB_USER=<postgres user>
        ```
    - `postgres.env`
        ```
        POSTGRES_PASS=<postgres password>
        POSTGRES_USER=<postgres user>
        ```
    - `airflow.env`
        ```
        AIRFLOW__SMTP__SMTP_USER=<gmail email address>
        AIRFLOW__SMTP__SMTP_PASSWORD=<gmail app password>
        AIRFLOW__SMTP__SMTP_MAIL_FROM=<gmail email address>
        AIRFLOW_MAIL_TO=<alerts receiver email address>
        ```
1. Make an empty directory `db/data`.
1. Run `docker-compose up`.

## Complete Setup
1. Keep the docker compose setup running.
1. To generate the json files, in another terminal do `docker-compose run etl python3 extract.py -s earliest yesterday`.
1. To dump all data into postgresql database do `docker-compose run etl python3 transform_load.py -s earliest yesterday`.
1. Open `<ip address>:3000` in the browser.
