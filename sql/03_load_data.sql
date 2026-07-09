-- Load data script
-- ==========================================
-- 03_load_data.sql
-- Load CSV files into RAW tables
-- ==========================================

USE DATABASE ELT_WAREHOUSE;
USE SCHEMA RAW;

--------------------------------------------------
-- Create CSV File Format
--------------------------------------------------

CREATE OR REPLACE FILE FORMAT csv_format
TYPE = CSV
FIELD_DELIMITER = ','
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
PARSE_HEADER = TRUE;

--------------------------------------------------
-- Create Internal Stage
--------------------------------------------------

CREATE OR REPLACE STAGE raw_stage
FILE_FORMAT = csv_format;

--------------------------------------------------
-- Verify Stage
--------------------------------------------------

SHOW STAGES;