# Personal Health and Productivity Tracker

An ETL pipeline & data visualization for my sleep & todo list data.
- Extracts todo list data from my Evolution calendar & sleep data from the Fitbit API & stores it all as json files
- Transforms the json data into sql-friendly tuples
- Loads the data into a PostgreSQL DB.
- Uses Metabase to visualize the data. Shows correlations between daily sleep time and productivity.
  - Productivity is quantified with the formula `finished_tasks * (finished_tasks / planned_tasks)`

## Installation
1. Install Docker and Docker Compose.
1. Install Evolution. Make sure Evolution has two calendars named `Todo` and `Done`. Evolution data files should be in `~/.local/share/evolution/` and `~/.config/evolution/`.
1. Get Fitbit credentials from https://dev.fitbit.com/apps/oauthinteractivetutorial. Select "Implicit Grant Flow".
1. `secrets/` should contain all the sensitive data. Add these files in `secrets/`. All `.secret` files should contain only the secret text and nothing else.
    - `FITBIT_ACCESS_TOKEN.secret`
    - `FITBIT_USER_ID.secret`
    - `POSTGRES_PASSWORD.secret`
    - `POSTGRES_USER.secret`
    - `metabase.env`
        - env file format: (replace the keywords in < > with the appropriate text. Do not include the symbols themselves, of course.)
        ```
        MB_DB_PASS=<postgres password>
        MB_DB_USER=<postgres user>
        ```
1. Make an empty directory `db/data`.
1. Run `docker-compose up`.

## Complete Setup
1. Keep the docker compose setup running.
1. To generate the json files, in another terminal do `docker-compose run etl python3 extract.py -s earliest yesterday`.
1. To dump all data into postgresql database do `docker-compose run etl python3 transform_load.py -s earliest yesterday`.
1. Open `<ip address>:3000` in the browser.
