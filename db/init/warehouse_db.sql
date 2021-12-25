CREATE TABLE IF NOT EXISTS activity_summaries
(
    date date NOT NULL,
    sedentary_minutes smallint NOT NULL DEFAULT 0,
    lightly_active_minutes smallint NOT NULL DEFAULT 0,
    fairly_active_minutes smallint NOT NULL DEFAULT 0,
    very_active_minutes smallint NOT NULL DEFAULT 0,
    PRIMARY KEY (date)
);

CREATE TABLE IF NOT EXISTS sleep_summaries
(
    date date NOT NULL,
    total_sleep_records smallint NOT NULL DEFAULT 0,
    total_minutes_asleep smallint,
    main_sleep_total_minutes_asleep smallint,
    PRIMARY KEY (date)
);

CREATE TABLE IF NOT EXISTS sleep_records
(
    start_time timestamp (0) without time zone NOT NULL,
    end_time timestamp (0) without time zone NOT NULL,
    wake_time smallint NOT NULL DEFAULT 0,
    rem_time smallint NOT NULL DEFAULT 0,
    light_time smallint NOT NULL DEFAULT 0,
    deep_time smallint NOT NULL DEFAULT 0,
    minutes_asleep smallint NOT NULL DEFAULT 0,
    efficiency_score smallint NOT NULL DEFAULT 0,
    is_main_sleep boolean NOT NULL DEFAULT FALSE,
    sleep_summary_id date NOT NULL,
    PRIMARY KEY (start_time),
  	CONSTRAINT sleep_summary_id
  	    FOREIGN KEY (sleep_summary_id)
        REFERENCES sleep_summaries (date)
);

CREATE TABLE IF NOT EXISTS todo_summaries
(
    date date NOT NULL,
    done_tasks smallint NOT NULL DEFAULT 0,
    total_tasks smallint NOT NULL DEFAULT 0,
    PRIMARY KEY (date)
);

CREATE TABLE IF NOT EXISTS todo_tasks
(
    name varchar(500),
    is_done boolean NOT NULL DEFAULT FALSE,
    todo_summary_id date NOT NULL,
    PRIMARY KEY (name, todo_summary_id),
    CONSTRAINT todo_summary_id
  		FOREIGN KEY (todo_summary_id)
    	REFERENCES todo_summaries (date)
);
