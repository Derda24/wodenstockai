-- Initialize Woden AI Stock Database
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist (handled by environment variables)
-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The actual tables will be created by SQLAlchemy models
-- This file can be used for additional initialization if needed

-- Sample data can be inserted here if desired
-- INSERT INTO stocks (symbol, name, current_price, sector, industry) VALUES 
-- ('AAPL', 'Apple Inc.', 150.00, 'Technology', 'Consumer Electronics'),
-- ('GOOGL', 'Alphabet Inc.', 2800.00, 'Technology', 'Internet Services'),
-- ('MSFT', 'Microsoft Corporation', 300.00, 'Technology', 'Software');
