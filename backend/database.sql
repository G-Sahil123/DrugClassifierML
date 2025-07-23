CREATE DATABASE IF NOT EXISTS drug_classifier;
USE drug_classifier;

-- USERS TABLE
Drop table if exists users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    occupation VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50)
);

CREATE TABLE predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_email VARCHAR(100),
    Age INT,
    Sex VARCHAR(10),
    BP VARCHAR(10),
    Cholesterol VARCHAR(10),
    Na FLOAT,
    K FLOAT,
    predicted_drug VARCHAR(20),
    predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);