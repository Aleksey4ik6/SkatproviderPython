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

-- Messages table (client/support chat)
CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    sender_type ENUM('client', 'support') NOT NULL,
    sender_name VARCHAR(255),
    text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read TINYINT(1) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX (customer_id, created_at)
);

-- Manual operator events for client 360 timeline
CREATE TABLE IF NOT EXISTS customer_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    details TEXT NOT NULL,
    actor VARCHAR(255),
    event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX (customer_id, event_time)
);

-- Customer self-service requests from mobile app
CREATE TABLE IF NOT EXISTS customer_self_service_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    request_type ENUM('promised_payment', 'plan_change', 'addon', 'autopay') NOT NULL,
    payload TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Новая',
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX (customer_id, created_at),
    INDEX (status)
);

-- Customer mobile settings
CREATE TABLE IF NOT EXISTS customer_autopay_settings (
    customer_id INT PRIMARY KEY,
    enabled TINYINT(1) NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Addon services activated for customers
CREATE TABLE IF NOT EXISTS customer_addons (
    addon_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Активна',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activated_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX (customer_id, created_at)
);

-- Promised payment approvals history
CREATE TABLE IF NOT EXISTS customer_promised_payments (
    promised_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    delay_days INT NOT NULL DEFAULT 0,
    approved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX (customer_id, approved_at)
);

-- Network nodes map
CREATE TABLE IF NOT EXISTS network_nodes (
    node_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    node_type VARCHAR(50) NOT NULL DEFAULT 'Роутер',
    location VARCHAR(255),
    x_pos INT DEFAULT 0,
    y_pos INT DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'OK',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Customer to node mapping (one active node per customer)
CREATE TABLE IF NOT EXISTS customer_node_links (
    customer_id INT PRIMARY KEY,
    node_id INT NOT NULL,
    linked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (node_id) REFERENCES network_nodes(node_id),
    INDEX (node_id)
);

-- Network incidents and outages
CREATE TABLE IF NOT EXISTS network_incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'Средняя',
    status VARCHAR(20) NOT NULL DEFAULT 'Активна',
    description TEXT,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (node_id) REFERENCES network_nodes(node_id),
    INDEX (node_id, status),
    INDEX (started_at)
);
