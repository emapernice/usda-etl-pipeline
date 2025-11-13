-- Migration: Add price_usd_per_ton and timestamp columns
-- Description: Add columns required by ETL: price_usd_per_ton, updated_at

USE usda_etl_pipeline;

ALTER TABLE usda_observations
  ADD COLUMN price_usd_per_ton DECIMAL(12,2) NULL AFTER price,
  ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP;