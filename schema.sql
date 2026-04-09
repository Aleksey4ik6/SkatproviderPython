-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS isp_database;
USE isp_database;

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    plan_id INT,
    registration_date DATETIME,
    INDEX (plan_id)
);

-- Plans table
CREATE TABLE IF NOT EXISTS plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    speed VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    data_limit VARCHAR(50),
    description TEXT
);

-- Complaints table
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    description TEXT NOT NULL,
    date DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    resolution TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Billing table
CREATE TABLE IF NOT EXISTS billing (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    paid TINYINT(1) DEFAULT 0,
    payment_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
