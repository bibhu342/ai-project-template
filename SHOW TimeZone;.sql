SHOW TimeZone;
SELECT now(), current_database(), current_user;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO customers (name, email)
VALUES 
 ('Bibhu', 'bibhu@example.com'),
 ('Test User', 'test@example.com');

SELECT * FROM customers;


DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);


INSERT INTO customers (name, email)
VALUES
('Bibhu', 'bibhu@example.com'),
('Aisha Khan', 'aisha.k@example.com'),
('Test User', 'test@example.com');

INSERT INTO customers (name, email)
VALUES
('Bibhu', 'bibhu@example.com'),
('Aisha Khan', 'aisha.k@example.com'),
('Test User', 'test@example.com');

SELECT id, name, email, created_at
FROM customers;


-- 1) Clean slate
DROP TABLE IF EXISTS customers;

-- 2) Create
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3) Insert 3 rows
INSERT INTO customers (name, email) VALUES
 ('Bibhu', 'bibhu@example.com'),
 ('Aisha Khan', 'aisha.k@example.com'),
 ('Test User', 'test@example.com');

-- 4) Verify
SELECT id, name, email, created_at
FROM customers
ORDER BY id;
