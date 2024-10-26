CREATE DATABASE currency_conversion;
USE currency_conversion;

-- Altering the 'users' table to ensure unique username and email
CREATE TABLE currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    currency_code VARCHAR(10) NOT NULL,
    currency_name VARCHAR(50) NOT NULL,
    conversion_rate_to_usd FLOAT NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    from_currency VARCHAR(10),
    to_currency VARCHAR(10),
    amount DECIMAL(10, 2),
    result DECIMAL(10, 2),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE conversion_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_currency VARCHAR(10),
    to_currency VARCHAR(10),
    amount DECIMAL(10, 2),
    result DECIMAL(10, 2),
    conversion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100),
    setting_value VARCHAR(100)
);

INSERT INTO currencies (currency_code, currency_name, conversion_rate_to_usd) 
VALUES ('USD', 'US Dollar', 1.0),
       ('EUR', 'Euro', 0.85),
       ('INR', 'Indian Rupee', 75.0),
       ('JPY', 'Japanese Yen', 110.0),
       ('GBP', 'British Pound', 0.75);

ALTER TABLE users MODIFY password VARCHAR(255);

