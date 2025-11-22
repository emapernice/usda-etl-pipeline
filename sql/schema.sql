-- Database initialization
CREATE DATABASE IF NOT EXISTS usda_etl_pipeline;
USE usda_etl_pipeline;


-- Table: usda_observations
DROP TABLE IF EXISTS usda_observations;

CREATE TABLE usda_observations (
    id INT NOT NULL AUTO_INCREMENT,
    year INT DEFAULT NULL,
    state_name VARCHAR(100) DEFAULT NULL,
    commodity_desc VARCHAR(100) DEFAULT NULL,
    statisticcat_desc VARCHAR(100) DEFAULT NULL,
    unit_desc VARCHAR(100) DEFAULT NULL,
    value FLOAT DEFAULT NULL,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Notes:
-- - This schema reflects the actual structure currently used
--   by the ETL pipeline and the MySQL database.