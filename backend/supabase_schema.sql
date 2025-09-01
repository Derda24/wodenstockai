-- Supabase Database Schema for Woden AI Stock Management
-- Run this in your Supabase SQL Editor

-- Note: JWT secret is managed by Supabase automatically
-- No need to set app.jwt_secret manually

-- Create stock_items table
CREATE TABLE IF NOT EXISTS stock_items (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(255) UNIQUE NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    current_stock DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    min_stock DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create stock_transactions table for audit trail
CREATE TABLE IF NOT EXISTS stock_transactions (
    id SERIAL PRIMARY KEY,
    stock_item_id INTEGER NOT NULL REFERENCES stock_items(id) ON DELETE CASCADE,
    transaction_type VARCHAR(100) NOT NULL, -- 'daily_consumption', 'manual_update', 'sales_upload'
    old_stock DECIMAL(10,2) NOT NULL,
    new_stock DECIMAL(10,2) NOT NULL,
    change_amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create manual_updates table for protection against daily consumption
CREATE TABLE IF NOT EXISTS manual_updates (
    id SERIAL PRIMARY KEY,
    stock_item_id INTEGER NOT NULL REFERENCES stock_items(id) ON DELETE CASCADE,
    old_stock DECIMAL(10,2) NOT NULL,
    new_stock DECIMAL(10,2) NOT NULL,
    reason VARCHAR(255),
    manual_update_flag BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create daily_usage_config table
CREATE TABLE IF NOT EXISTS daily_usage_config (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(255) UNIQUE NOT NULL,
    daily_amount DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    recipe_name VARCHAR(255) NOT NULL,
    ingredients TEXT NOT NULL, -- JSON string
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sales_history table
CREATE TABLE IF NOT EXISTS sales_history (
    id SERIAL PRIMARY KEY,
    date VARCHAR(50) NOT NULL,
    total_sales DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    items_sold TEXT NOT NULL, -- JSON string
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_items_material_id ON stock_items(material_id);
CREATE INDEX IF NOT EXISTS idx_stock_items_category ON stock_items(category_name);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_stock_item_id ON stock_transactions(stock_item_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_timestamp ON stock_transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_manual_updates_stock_item_id ON manual_updates(stock_item_id);
CREATE INDEX IF NOT EXISTS idx_manual_updates_timestamp ON manual_updates(timestamp);
CREATE INDEX IF NOT EXISTS idx_daily_usage_config_material_id ON daily_usage_config(material_id);
CREATE INDEX IF NOT EXISTS idx_recipes_recipe_name ON recipes(recipe_name);
CREATE INDEX IF NOT EXISTS idx_sales_history_date ON sales_history(date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_stock_items_updated_at BEFORE UPDATE ON stock_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_usage_config_updated_at BEFORE UPDATE ON daily_usage_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Optional for now
-- ALTER TABLE stock_items ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE stock_transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE manual_updates ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE daily_usage_config ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sales_history ENABLE ROW LEVEL SECURITY;

-- Create a view for stock summary
CREATE OR REPLACE VIEW stock_summary AS
SELECT 
    si.category_name,
    si.item_name,
    si.current_stock,
    si.min_stock,
    si.unit,
    si.material_id,
    CASE 
        WHEN si.current_stock <= si.min_stock THEN 'LOW_STOCK'
        WHEN si.current_stock <= si.min_stock * 1.5 THEN 'MEDIUM_STOCK'
        ELSE 'GOOD_STOCK'
    END as stock_status,
    si.updated_at as last_updated
FROM stock_items si
ORDER BY si.category_name, si.item_name;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
