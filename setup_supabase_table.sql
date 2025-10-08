
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
