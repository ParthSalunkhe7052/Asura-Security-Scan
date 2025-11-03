-- Migration: Add scan_name column to scans table
-- Date: 2025-11-03

-- Add the scan_name column
ALTER TABLE scans ADD COLUMN scan_name TEXT;

-- Update existing scans with generated names
-- This will be done by the Python migration script
