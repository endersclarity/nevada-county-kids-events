"""Setup database tables for Nevada County Kids Events"""
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

# SQL to create the events table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,

  -- Core fields
  title TEXT NOT NULL,
  description TEXT,
  event_date TIMESTAMP WITH TIME ZONE,

  -- Location
  venue TEXT,
  city_area TEXT,

  -- Source tracking
  source_name TEXT NOT NULL,
  source_url TEXT,
  source_event_id TEXT,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Deduplication
  content_hash TEXT,

  -- Metadata
  event_types TEXT[],
  age_range TEXT,
  price TEXT,
  is_free BOOLEAN,

  -- Quality/enrichment
  kid_friendly_score INTEGER,
  quality_score INTEGER,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Critical indexes for performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_source_event_unique ON events(source_name, source_event_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_name);
CREATE INDEX IF NOT EXISTS idx_events_content_hash ON events(content_hash);
CREATE INDEX IF NOT EXISTS idx_events_scraped_at ON events(scraped_at);
"""

def main():
    """Execute SQL via Supabase REST API"""

    # Use Supabase REST API to execute SQL
    # Note: This requires the service_role key, not anon key
    # We'll use PostgREST instead

    print(f"Setting up database at {SUPABASE_URL}...")
    print()
    print("=" * 60)
    print("IMPORTANT: You need to run this SQL in your Supabase dashboard:")
    print("=" * 60)
    print()
    print("1. Go to: " + SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/'))
    print("2. Click 'SQL Editor' in the left sidebar")
    print("3. Click 'New query'")
    print("4. Copy and paste the following SQL:")
    print()
    print("-" * 60)
    print(CREATE_TABLE_SQL)
    print("-" * 60)
    print()
    print("5. Click 'Run' or press Ctrl+Enter")
    print()
    print("=" * 60)

    # Also save to file
    with open('setup_supabase_table.sql', 'w') as f:
        f.write(CREATE_TABLE_SQL)

    print()
    print("SQL also saved to: setup_supabase_table.sql")
    print()

if __name__ == '__main__':
    main()
