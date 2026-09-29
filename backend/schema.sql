-- ==========================================
-- SUPABASE DATABASE SCHEMA FOR PROFILES TABLE
-- ==========================================
-- Run this SQL in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/_/sql

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create index on firebase_uid for quick lookups
CREATE INDEX IF NOT EXISTS idx_profiles_firebase_uid ON public.profiles(firebase_uid);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Allow full access for backend service role key and public operations where appropriate
CREATE POLICY "Allow public read access to profiles" 
    ON public.profiles 
    FOR SELECT 
    USING (true);

CREATE POLICY "Allow service role full access" 
    ON public.profiles 
    FOR ALL 
    USING (true)
    WITH CHECK (true);
