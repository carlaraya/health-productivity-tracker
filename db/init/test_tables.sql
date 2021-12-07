CREATE TABLE test_departments (
    id      INT PRIMARY KEY     NOT NULL,
    name        VARCHAR(50)     NOT NULL
);

CREATE TABLE test_people (
    id      INT PRIMARY KEY     NOT NULL,
    name        VARCHAR(50)     NOT NULL,
    age         INT             NOT NULL,
    salary      REAL            NOT NULL,
    department_id INT           NOT NULL,
    FOREIGN KEY (department_id)
        REFERENCES test_departments (id)
);

INSERT INTO test_departments (id, name) VALUES
(1, 'Engineering'),
(2, 'HR'),
(3, 'Sales');

INSERT INTO test_people (id, name, age, salary, department_id) VALUES
(1, 'Alice', 55, 800000, 1),
(2, 'Bob', 24, 400000, 1),
(3, 'Carl', 32, 200000, 2),
(4, 'Dan', 22, 910000, 1),
(5, 'Eve', 38, 1000, 2),
(6, 'Frederick', 42, 200, 3);
