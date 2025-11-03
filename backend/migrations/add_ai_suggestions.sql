-- Migration: Add AI Suggestions fields to Scan table
-- Date: November 3, 2025
-- Description: Adds fields to cache AI-generated security analysis

-- Add AI suggestions columns to scans table
ALTER TABLE scans ADD COLUMN ai_suggestions TEXT NULL;
ALTER TABLE scans ADD COLUMN ai_model VARCHAR NULL;
ALTER TABLE scans ADD COLUMN ai_generated_at TIMESTAMP NULL;

-- Add index for faster queries on AI suggestions
CREATE INDEX idx_scan_ai_generated ON scans(ai_generated_at) WHERE ai_generated_at IS NOT NULL;

-- Success message
SELECT 'Migration completed: AI suggestions fields added to scans table' AS status;
