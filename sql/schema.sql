CREATE DATABASE IF NOT EXISTS usda_etl_pipeline;
USE usda_etl_pipeline;

CREATE TABLE IF NOT EXISTS usda_observations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    state_name VARCHAR(100) NOT NULL,
    commodity_desc VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
