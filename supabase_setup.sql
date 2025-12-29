-- Discilogo Supabase Setup Script
-- Run this in Supabase SQL Editor (supabase.com -> Your Project -> SQL Editor)

-- Create habits table
CREATE TABLE IF NOT EXISTS habits (
    id BIGSERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    date TEXT NOT NULL,
    habit_id BIGINT NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    habit_question_snapshot TEXT NOT NULL,
    status BOOLEAN NOT NULL,
    excuse_note TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_logs_date ON logs(date);
CREATE INDEX IF NOT EXISTS idx_logs_habit_id ON logs(habit_id);
CREATE INDEX IF NOT EXISTS idx_habits_active ON habits(is_active);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (for simplicity - you can make this more restrictive later)
CREATE POLICY "Allow all operations on habits" ON habits FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on logs" ON logs FOR ALL USING (true) WITH CHECK (true);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS and create policy for notes
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on notes" ON notes FOR ALL USING (true) WITH CHECK (true);

