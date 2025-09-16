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
    total_quantity INTEGER NOT NULL DEFAULT 0,
    items_sold TEXT NOT NULL, -- JSON string
    learning_data TEXT, -- JSON string for AI learning
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create baristas table for AI Scheduler
CREATE TABLE IF NOT EXISTS baristas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    type VARCHAR(20) DEFAULT 'full-time', -- 'full-time', 'part-time'
    max_hours INTEGER DEFAULT 45, -- per week
    preferred_shifts TEXT[], -- ['morning', 'evening']
    skills TEXT[], -- ['coffee', 'cashier', 'cleaning', 'management']
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create weekly_schedules table
CREATE TABLE IF NOT EXISTS weekly_schedules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
    created_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create shifts table
CREATE TABLE IF NOT EXISTS shifts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    schedule_id UUID NOT NULL REFERENCES weekly_schedules(id) ON DELETE CASCADE,
    barista_id UUID NOT NULL REFERENCES baristas(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL, -- 0=Monday, 6=Sunday
    shift_type VARCHAR(20) NOT NULL, -- 'morning', 'evening', 'off', 'part-time'
    start_time TIME,
    end_time TIME,
    hours DECIMAL(3,1) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create time_off_requests table
CREATE TABLE IF NOT EXISTS time_off_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    barista_id UUID NOT NULL REFERENCES baristas(id) ON DELETE CASCADE,
    request_date DATE NOT NULL,
    reason VARCHAR(100), -- 'vacation', 'sick', 'personal', 'other'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    notes TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP WITH TIME ZONE
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

-- Indexes for AI Scheduler tables
CREATE INDEX IF NOT EXISTS idx_baristas_type ON baristas(type);
CREATE INDEX IF NOT EXISTS idx_baristas_is_active ON baristas(is_active);
CREATE INDEX IF NOT EXISTS idx_weekly_schedules_week_start ON weekly_schedules(week_start);
CREATE INDEX IF NOT EXISTS idx_weekly_schedules_status ON weekly_schedules(status);
CREATE INDEX IF NOT EXISTS idx_shifts_schedule_id ON shifts(schedule_id);
CREATE INDEX IF NOT EXISTS idx_shifts_barista_id ON shifts(barista_id);
CREATE INDEX IF NOT EXISTS idx_shifts_day_of_week ON shifts(day_of_week);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_barista_id ON time_off_requests(barista_id);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_request_date ON time_off_requests(request_date);
CREATE INDEX IF NOT EXISTS idx_time_off_requests_status ON time_off_requests(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at (with IF NOT EXISTS check)
DO $$
BEGIN
    -- Existing triggers
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_stock_items_updated_at') THEN
        CREATE TRIGGER update_stock_items_updated_at BEFORE UPDATE ON stock_items
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_daily_usage_config_updated_at') THEN
        CREATE TRIGGER update_daily_usage_config_updated_at BEFORE UPDATE ON daily_usage_config
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_recipes_updated_at') THEN
        CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    -- AI Scheduler triggers
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_baristas_updated_at') THEN
        CREATE TRIGGER update_baristas_updated_at BEFORE UPDATE ON baristas
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_weekly_schedules_updated_at') THEN
        CREATE TRIGGER update_weekly_schedules_updated_at BEFORE UPDATE ON weekly_schedules
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

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
