-- =========================================================
-- Database initialization
-- =========================================================
CREATE DATABASE IF NOT EXISTS usda_etl_pipeline;
USE usda_etl_pipeline;

-- =========================================================
-- Table: usda_observations
-- =========================================================
DROP TABLE IF EXISTS usda_observations;

CREATE TABLE usda_observations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    state_name VARCHAR(100) NOT NULL,
    commodity_desc VARCHAR(100) NOT NULL,
    statisticcat_desc VARCHAR(100) NULL,
    unit_desc VARCHAR(100) NULL,
    metric_type VARCHAR(50) NULL,
    yield FLOAT NULL,
    price FLOAT NULL,
    production FLOAT NULL,
    value FLOAT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- Indexes for performance
-- =========================================================
CREATE INDEX idx_usda_year ON usda_observations(year);
CREATE INDEX idx_usda_state ON usda_observations(state_name);
CREATE INDEX idx_usda_commodity ON usda_observations(commodity_desc);
CREATE INDEX idx_usda_metric ON usda_observations(metric_type);

-- =========================================================
-- Notes:
-- - 'metric_type' helps categorize the record: YIELD, PRICE,
--   PRODUCTION, VALUE, etc.
-- - 'value' may store generalized indicators (e.g. area planted).
-- - 'unit_desc' describes the measurement unit from the USDA API.
-- =========================================================