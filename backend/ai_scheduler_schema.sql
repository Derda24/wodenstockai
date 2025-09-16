-- AI Scheduler Database Schema for Woden AI Stock Management
-- Run this in your Supabase SQL Editor to add only the AI Scheduler tables

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

-- Create updated_at trigger function if it doesn't exist
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

-- Insert sample baristas for testing
INSERT INTO baristas (name, email, phone, type, max_hours, preferred_shifts, skills, is_active) VALUES
('Ahmet Yılmaz', 'ahmet@woden.com', '+90 555 123 4567', 'full-time', 45, ARRAY['morning', 'evening'], ARRAY['coffee', 'cashier', 'cleaning'], true),
('Mehmet Kaya', 'mehmet@woden.com', '+90 555 234 5678', 'full-time', 45, ARRAY['evening'], ARRAY['coffee', 'management'], true),
('Ayşe Demir', 'ayse@woden.com', '+90 555 345 6789', 'part-time', 25, ARRAY['morning'], ARRAY['coffee', 'cashier'], true),
('Fatma Özkan', 'fatma@woden.com', '+90 555 456 7890', 'full-time', 45, ARRAY['morning', 'evening'], ARRAY['coffee', 'cashier', 'cleaning'], true),
('Ali Çelik', 'ali@woden.com', '+90 555 567 8901', 'part-time', 30, ARRAY['evening'], ARRAY['coffee', 'cleaning'], true),
('Zeynep Arslan', 'zeynep@woden.com', '+90 555 678 9012', 'full-time', 45, ARRAY['morning'], ARRAY['coffee', 'cashier', 'management'], true)
ON CONFLICT (id) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
