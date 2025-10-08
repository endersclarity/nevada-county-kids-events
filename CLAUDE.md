# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nevada County Kids Events Agent** - Event aggregation and delivery system that scrapes, normalizes, and delivers kid-friendly local events from multiple Nevada County sources. Built as a Python-based scraping engine with future slash command integration for Claude Code.

**Current Status:** Epic 2 Complete (Core Engine), Epic 3 In Progress (Multi-Source Integration)

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Supabase credentials
```

### Running the Orchestrator
```bash
# Single source (KNCO only)
python -m src.orchestrator --sources knco

# Multiple sources in parallel
python -m src.orchestrator --sources knco,library,county

# Force fresh scrape (bypass cache)
python -m src.orchestrator --sources knco --no-cache

# Sequential scraping (disable parallelism)
python -m src.orchestrator --sources knco,library --no-parallel

# Filter by quality score
python -m src.orchestrator --sources knco --min-quality 50

# Custom timeout per source
python -m src.orchestrator --sources knco,library --timeout 60
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_knco_scraper.py

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=src

# Run single test
python -m pytest tests/test_knco_scraper.py::test_parse_events
```

### Development Scripts
```bash
# Test library scraper (live)
python test_library_live.py

# Test library scraper (JSON fixture)
python test_library_json.py

# Evaluate KNCO data quality
python scripts/evaluate_knco.py
```

## Architecture

### High-Level Structure

```
EventOrchestrator (orchestrator.py)
├── Manages parallel/sequential scraping execution
├── Integrates CacheManager for TTL-based caching
└── Coordinates scrapers, normalization, and storage

Scrapers (src/scrapers/)
├── BaseScraper (base.py) - Abstract interface
├── KNCOScraper (knco.py) - Trumba RSS feed
├── LibraryScraper (library.py) - LibCal JSON API
└── CountyScraper (county.py) - iCal format

Processors (src/processors/)
├── Normalizer (normalizer.py) - Standardizes event data
│   ├── Validates required fields (title, date, source)
│   ├── Generates content_hash for deduplication
│   └── Calculates quality_score (0-100)
└── Deduplicator (deduplicator.py) - Cross-source duplicate detection

Storage (src/storage/)
├── SupabaseClient (supabase.py) - PostgreSQL operations
│   ├── upsert_events() - ON CONFLICT handling
│   └── get_cached_events() - TTL-based queries
└── CacheManager (cache.py) - TTL-based caching layer
```

### Data Flow

1. **Orchestrator** receives source list and configuration
2. **CacheManager** checks database for fresh events (TTL-based)
3. If cache miss → **Scraper** fetches raw data from source
4. **Normalizer** validates and standardizes events
5. **SupabaseClient** upserts to database (handles duplicates via unique index)
6. Events returned as list of dictionaries

### Key Design Patterns

**Scraper Pattern:** All scrapers inherit from `BaseScraper` and implement:
- `fetch()` - Returns list of raw event dictionaries
- `parse()` - Source-specific parsing logic

**Unique Event Identity:** Events are uniquely identified by `(source_name, source_event_id)` tuple. Database uses unique index `idx_source_event_unique` to prevent duplicates from same source.

**Quality Scoring:** Events receive 0-100 quality score based on field completeness:
- Required fields (title, date): 40 points
- Description: 20-30 points (bonus for >50 chars)
- Optional metadata (venue, age_range, price): 10 points each
- Used to filter low-quality events via `--min-quality` flag

**Parallel Execution:** `ThreadPoolExecutor` scrapes multiple sources concurrently with per-source timeout. Graceful degradation if sources fail.

## Database Schema

Events table (Supabase PostgreSQL):

```sql
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  event_date TIMESTAMP WITH TIME ZONE,
  venue TEXT,
  city_area TEXT,
  source_name TEXT NOT NULL,
  source_url TEXT,
  source_event_id TEXT,
  content_hash TEXT,
  age_range TEXT,
  price TEXT,
  is_free BOOLEAN,
  quality_score INTEGER,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Critical indexes for performance
CREATE UNIQUE INDEX idx_source_event_unique ON events(source_name, source_event_id);
CREATE INDEX idx_events_scraped_at ON events(scraped_at);
CREATE INDEX idx_events_date ON events(event_date);
```

## Configuration

Environment variables (`.env`):

```bash
# Required
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional - with defaults
CACHE_TTL_HOURS=6              # Cache freshness duration
REQUEST_TIMEOUT=30             # HTTP request timeout
SCRAPER_TIMEOUT=30             # Per-source timeout for parallel execution
MIN_QUALITY_SCORE=0            # Minimum quality score to include events (0-100)
```

## Source-Specific Notes

### KNCO Scraper (Trumba RSS)
- **Challenge:** HTML entities in description (`&amp;nbsp;` vs `&nbsp;`)
- **Parsing:** Extracts metadata from HTML-formatted description using regex
- **Fields:** City/Area, Age, Venue, Price all embedded in description HTML
- **Event ID:** Extracted from GUID (e.g., `http://uid.trumba.com/event/177609910` → `177609910`)

### Library Scraper (LibCal JSON API)
- **URL:** `https://nevadacounty.libcal.com/mobile_app_json.php`
- **Format:** Clean JSON with structured fields
- **Best practices:** Highest data quality, explicit age ranges
- **Event ID:** Uses LibCal's `event_id` field

### County Scraper (iCal)
- **Format:** iCalendar (.ics) format
- **Parsing:** Uses `icalendar` library
- **Challenge:** Less kid-specific metadata than other sources
- **Status:** In progress (Epic 3)

## Testing Approach

### Unit Tests
- Test scrapers with fixture data (sample RSS/JSON in `data/samples/`)
- Test normalizer validation logic with edge cases
- Test quality scoring algorithm
- Mock HTTP requests with `responses` library

### Integration Tests
- Test full orchestrator flow with real Supabase connection
- Test cache hit/miss behavior
- Test parallel scraping with timeouts
- Verify database upsert logic (ON CONFLICT handling)

### Test Data Location
- Sample data: `data/samples/`
- Debug output: `data/debug/`
- Evaluation results: `data/knco_evaluation_results.json`

## Common Development Workflows

### Adding a New Source

1. Create scraper in `src/scrapers/new_source.py`:
```python
from .base import BaseScraper

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__('new_source')

    def fetch(self) -> List[Dict]:
        # Fetch and parse logic
        pass

    def parse(self, raw_data) -> List[Dict]:
        # Return list of dicts with required fields:
        # - title, event_date, description
        # - source_url, source_event_id
        # - venue, city_area, age_range, price (optional)
        pass
```

2. Register in `orchestrator.py`:
```python
AVAILABLE_SOURCES = {
    'knco': KNCOScraper,
    'library': LibraryScraper,
    'new_source': NewSourceScraper,
}
```

3. Create test in `tests/test_new_source_scraper.py`
4. Add sample data to `data/samples/new_source_sample.html`

### Troubleshooting Cache Issues

Cache is based on `scraped_at` timestamp. Events are "fresh" if `scraped_at > NOW() - CACHE_TTL_HOURS`.

To force bypass cache:
```bash
python -m src.orchestrator --sources knco --no-cache
```

To manually clear cache for source, delete events from database:
```sql
DELETE FROM events WHERE source_name = 'knco';
```

### Debugging Scraper Failures

All scrapers log to console with `[INFO]`, `[WARNING]`, `[ERROR]` levels.

Common issues:
- **Connection timeout:** Increase `--timeout` or `REQUEST_TIMEOUT` env var
- **Parse errors:** Check if source HTML/JSON structure changed
- **Missing fields:** Normalizer will log validation errors but continue with other events

## Project Planning

Epic structure documented in `stories/` directory:
- **Epic 1:** Source Research & Evaluation (✅ Complete)
- **Epic 2:** Core Scraping Engine (✅ Complete)
- **Epic 3:** Multi-Source Integration (🟡 In Progress)
- **Epic 4:** Delivery Layer (email, Telegram, Google Calendar)
- **Epic 5:** Slash Command Interface
- **Epic 6:** Polish & Optimization

See `PRD.md` for complete product requirements and `SCRUM-BACKLOG.md` for sprint planning.

## Important Context

**Deduplication Strategy:** Currently uses unique index on `(source_name, source_event_id)` to prevent duplicates from same source. Cross-source deduplication (Epic 3.3) will use fuzzy matching on `content_hash` and title similarity.

**Date Handling:** All dates stored as `TIMESTAMP WITH TIME ZONE` in database. Normalizer parses multiple formats (ISO 8601, US format, etc.).

**Error Philosophy:** Graceful degradation - if one source fails, continue with others and show partial results. Log errors for debugging but don't halt entire pipeline.

**Performance Target:** All sources should complete scraping in <2 minutes total (parallel execution).

**Caching Strategy:** 6-hour TTL by default. Cache is source-specific, not global. Second run within TTL returns cached data instantly.
