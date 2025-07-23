-- Cleanup in case of reruns
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS logins;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    middle_initials TEXT,
    middle_name TEXT,
    dob DATE,
    age_last_birthday INTEGER,
    favourite_colour TEXT,
    favourite_animal TEXT,
    favourite_food TEXT,
    gender TEXT,
    password TEXT NOT NULL,
    city TEXT,
    county TEXT,
    county_code TEXT,
    postcode TEXT,
    email TEXT UNIQUE NOT NULL,
    dial_code TEXT NOT NULL,
    phone TEXT,
    mobile TEXT,
    education TEXT,
    rqf TEXT,
    salary REAL,
    currency TEXT CHECK(currency IN ('GBP', 'EUR', 'USD')) NOT NULL,
    website_visits_last_30_days INTEGER,
    country_code TEXT CHECK(country_code IN ('UK', 'FR', 'USA', 'SC')) NOT NULL
);

CREATE TABLE IF NOT EXISTS logins (
    login_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    login_timestamp DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);