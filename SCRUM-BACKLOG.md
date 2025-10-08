# Nevada County Kids Events Agent - Scrum Backlog

**Product:** Nevada County Kids Events Agent
**Version:** 1.0 MVP
**Sprint Duration:** 1 week (flexible, no hard deadlines)
**Story Point Scale:** Fibonacci (1, 2, 3, 5, 8, 13)
**Created:** 2025-10-07
**Last Updated:** 2025-10-07

---

## Table of Contents

1. [Epic Overview](#epic-overview)
2. [Sprint Planning](#sprint-planning)
3. [Backlog (Prioritized)](#backlog-prioritized)
4. [Story Details with Acceptance Criteria](#story-details-with-acceptance-criteria)
5. [Dependency Map](#dependency-map)
6. [Velocity Tracking](#velocity-tracking)

---

## Epic Overview

### Epic Summary Table

| Epic # | Name | Stories | Total Points | Priority | Status | Dependencies |
|--------|------|---------|--------------|----------|--------|--------------|
| **E1** | Source Research & Evaluation | 4 | 13 | P0 (Critical) | 🔵 Ready | None |
| **E2** | Core Scraping Engine | 6 | 21 | P0 (Critical) | ⏸️ Blocked | E1 |
| **E3** | Multi-Source Integration | 5 | 21 | P1 (High) | ⏸️ Blocked | E2 |
| **E4** | Delivery Layer | 5 | 21 | P1 (High) | ⏸️ Blocked | E2 |
| **E5** | Slash Command Interface | 5 | 13 | P0 (Critical) | ⏸️ Blocked | E2, E4 |
| **E6** | Polish & Optimization | 3 | 13 | P2 (Low) | ⏸️ Blocked | E5 (MVP) |
| | | **28** | **102** | | | |

---

### Epic Descriptions

#### E1: Source Research & Evaluation
**Goal:** Identify the 3 best event sources for MVP based on data quality, volume, and scraping difficulty.

**Why This First:**
- Informs which scrapers to build (don't waste time on low-value sources)
- Validates feasibility of scraping approach
- Provides sample data for testing

**Exit Criteria:**
- Top 3 sources selected with documented rationale
- Sample datasets stored for testing
- Confidence in scraping strategy

---

#### E2: Core Scraping Engine (Single Source)
**Goal:** Build end-to-end working prototype with highest-priority source.

**Why This Matters:**
- Proves the architecture works
- Establishes patterns for additional sources
- Delivers tangible progress (data in database)

**Exit Criteria:**
- Command-line script scrapes + stores events
- Cache layer functional
- Unit tests passing

---

#### E3: Multi-Source Integration
**Goal:** Add 2 more sources + deduplication logic.

**Why This Matters:**
- Core value prop is aggregation (1 source = not compelling)
- Deduplication proves cross-source matching works
- Parallel scraping improves performance

**Exit Criteria:**
- 3 scrapers operational
- Combined results deduplicated
- Execution time <30 seconds

---

#### E4: Delivery Layer
**Goal:** Enable multiple output methods (email, Telegram, calendar).

**Why This Matters:**
- Makes data actionable (stored events = useless without delivery)
- User choice = better UX than single method
- Modular design allows easy expansion

**Exit Criteria:**
- At least 2 delivery methods work
- User receives events successfully
- Configuration validated

---

#### E5: Slash Command Interface
**Goal:** Claude Code command triggers full pipeline conversationally.

**Why This Matters:**
- **This IS the product** (slash command vision)
- Ties all components together
- Delivers MVP promise

**Exit Criteria:**
- `/get-events` works end-to-end
- Conversational delivery selection
- Completes in <2 minutes

---

#### E6: Polish & Optimization
**Goal:** Add intelligence and refinement (post-MVP).

**Why Later:**
- MVP proves value first
- Avoid over-engineering before usage
- Informed by real usage patterns

**Exit Criteria:**
- User validation: "This adds value"
- Measurable improvement (time saved, accuracy, etc.)

---

## Sprint Planning

### Suggested Sprint Breakdown

#### Sprint 0: Research & Planning (Pre-Development)
**Duration:** 1-2 sessions
**Goal:** Complete source evaluation, finalize architecture

**Stories:**
- E1.1: Evaluate KNCO (3 pts)
- E1.2: Evaluate Library (3 pts)
- E1.3: Evaluate County (3 pts)
- E1.4: Prioritize Sources (2 pts)

**Total:** 11 points
**Deliverable:** Source evaluation report, top 3 sources selected

---

#### Sprint 1: Foundation (Single Source)
**Duration:** 1-2 weeks
**Goal:** Working prototype with 1 source

**Stories:**
- E2.1: Python Project Setup (2 pts)
- E2.2: KNCO RSS Scraper (5 pts)
- E2.3: Data Normalizer (3 pts)
- E2.4: Supabase Integration (5 pts)
- E2.5: Cache Layer (3 pts)
- E2.6: Orchestrator (3 pts)

**Total:** 21 points
**Deliverable:** `python -m src.orchestrator --source knco` works

---

#### Sprint 2: Multi-Source Expansion
**Duration:** 1-2 weeks
**Goal:** 3 sources + deduplication

**Stories:**
- E3.1: Library Scraper (5 pts)
- E3.2: County Scraper (5 pts)
- E3.3: Deduplication Logic (5 pts)
- E3.4: Parallel Scraping (3 pts)
- E3.5: Data Quality Validation (3 pts)

**Total:** 21 points
**Deliverable:** Combined results from 3 sources, deduplicated

---

#### Sprint 3: Delivery Layer
**Duration:** 1-2 weeks
**Goal:** 2+ delivery methods working

**Stories:**
- E4.1: Delivery Interface Design (2 pts)
- E4.2: Email Delivery (5 pts)
- E4.3: Telegram Delivery (5 pts)
- E4.4: Google Calendar Integration (8 pts) *[Optional for Sprint 3]*
- E4.5: Delivery Router (3 pts)

**Total:** 15-23 points (depending on GCal inclusion)
**Deliverable:** Receive events via email + Telegram

---

#### Sprint 4: MVP Integration
**Duration:** 1 week
**Goal:** Slash command end-to-end

**Stories:**
- E5.1: Command Design (2 pts)
- E5.2: Command Orchestration (3 pts)
- E5.3: Conversational Delivery Selection (3 pts)
- E5.4: Error Handling (3 pts)
- E5.5: Documentation (2 pts)

**Total:** 13 points
**Deliverable:** `/get-events` MVP complete

---

#### Sprint 5+: Polish & Future (Post-MVP)
**Duration:** Ongoing
**Goal:** Enhancements based on usage

**Stories:**
- E6.1: Event Categorization (5 pts)
- E6.2: Kid-Friendly Scoring (5 pts)
- E6.3: Summarization (3 pts)
- (Future stories added as needed)

**Total:** 13+ points
**Deliverable:** Enhanced intelligence

---

## Backlog (Prioritized)

### Now (Sprint 0) - Source Research
**Must complete before development:**

| ID | Story | Points | Priority | Status |
|----|-------|--------|----------|--------|
| E1.1 | Evaluate KNCO RSS Feed | 3 | P0 | 🔵 Ready |
| E1.2 | Evaluate Library Calendar | 3 | P0 | 🔵 Ready |
| E1.3 | Evaluate County Calendar | 3 | P0 | 🔵 Ready |
| E1.4 | Prioritize Sources for MVP | 2 | P0 | ⏸️ Blocked by E1.1-1.3 |

**Total:** 11 points

---

### Next (Sprint 1) - Core Engine
**Build single-source prototype:**

| ID | Story | Points | Priority | Status | Depends On |
|----|-------|--------|----------|--------|------------|
| E2.1 | Python Project Setup | 2 | P0 | ⏸️ | E1.4 |
| E2.2 | KNCO RSS Scraper | 5 | P0 | ⏸️ | E2.1 |
| E2.3 | Data Normalizer | 3 | P0 | ⏸️ | E2.2 |
| E2.4 | Supabase Integration | 5 | P0 | ⏸️ | E2.3 |
| E2.5 | Cache Layer | 3 | P0 | ⏸️ | E2.4 |
| E2.6 | Orchestrator | 3 | P0 | ⏸️ | E2.2, E2.3, E2.4, E2.5 |

**Total:** 21 points

---

### Later (Sprint 2) - Multi-Source
**Add sources + deduplication:**

| ID | Story | Points | Priority | Status | Depends On |
|----|-------|--------|----------|--------|------------|
| E3.1 | Library Scraper | 5 | P1 | ⏸️ | E2.6 |
| E3.2 | County Scraper | 5 | P1 | ⏸️ | E2.6 |
| E3.3 | Cross-Source Deduplication | 5 | P1 | ⏸️ | E3.1, E3.2 |
| E3.4 | Parallel Scraping | 3 | P1 | ⏸️ | E3.1, E3.2 |
| E3.5 | Data Quality Validation | 3 | P1 | ⏸️ | E3.3 |

**Total:** 21 points

---

### Later (Sprint 3) - Delivery
**Build output methods:**

| ID | Story | Points | Priority | Status | Depends On |
|----|-------|--------|----------|--------|------------|
| E4.1 | Delivery Interface Design | 2 | P1 | ⏸️ | E2.6 |
| E4.2 | Email Delivery | 5 | P1 | ⏸️ | E4.1 |
| E4.3 | Telegram Delivery | 5 | P1 | ⏸️ | E4.1 |
| E4.4 | Google Calendar Integration | 8 | P2 | ⏸️ | E4.1 |
| E4.5 | Delivery Router | 3 | P1 | ⏸️ | E4.2, E4.3 |

**Total:** 23 points (or 15 without GCal)

---

### Later (Sprint 4) - Command Interface
**Tie it all together:**

| ID | Story | Points | Priority | Status | Depends On |
|----|-------|--------|----------|--------|------------|
| E5.1 | Design Claude Code Command | 2 | P0 | ⏸️ | E4.5 |
| E5.2 | Command Orchestration | 3 | P0 | ⏸️ | E5.1, E3.5 |
| E5.3 | Conversational Delivery Selection | 3 | P0 | ⏸️ | E5.2 |
| E5.4 | Error Handling & Feedback | 3 | P0 | ⏸️ | E5.2 |
| E5.5 | Documentation & Help | 2 | P0 | ⏸️ | E5.3, E5.4 |

**Total:** 13 points

---

### Future (Sprint 5+) - Polish
**Post-MVP enhancements:**

| ID | Story | Points | Priority | Status | Depends On |
|----|-------|--------|----------|--------|------------|
| E6.1 | Event Categorization | 5 | P2 | ⏸️ | E5.5 (MVP) |
| E6.2 | Kid-Friendly Scoring | 5 | P2 | ⏸️ | E5.5 (MVP) |
| E6.3 | Natural Language Summarization | 3 | P2 | ⏸️ | E5.5 (MVP) |

**Total:** 13 points

---

## Story Details with Acceptance Criteria

### Epic 1: Source Research & Evaluation

---

#### E1.1: Evaluate KNCO RSS Feed
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Research/Spike

**As a** developer
**I want to** scrape a sample dataset from KNCO Trumba RSS
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 50 events from KNCO feed
- [ ] Extract all available fields (title, description, date, location, age range, etc.)
- [ ] Document metadata completeness (% events with each field)
- [ ] Calculate kid-relevance ratio (manual review of sample)
- [ ] Measure scraping difficulty (1-5 scale with justification)
- [ ] Store findings in `docs/source-evaluation.md` (KNCO section)

**Technical Tasks:**
1. Write quick-and-dirty Python script to fetch RSS
2. Parse with `feedparser` library
3. Extract fields, count nulls
4. Manually review 20 random events for kid-relevance
5. Document challenges (HTML entities, GUID extraction, etc.)

**Definition of Done:**
- Findings documented with metrics
- Sample data stored in `data/samples/knco_sample.xml`
- Scraping difficulty scored with rationale

---

#### E1.2: Evaluate Nevada County Library
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Research/Spike

**As a** developer
**I want to** scrape a sample dataset from Nevada County Library calendar
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 20 events from library calendar
- [ ] Extract all available fields
- [ ] Document metadata completeness
- [ ] Calculate kid-relevance ratio
- [ ] Measure scraping difficulty (1-5 scale)
- [ ] Investigate RSS/API options (LibCal may have structured export)
- [ ] Store findings in `docs/source-evaluation.md` (Library section)

**Technical Tasks:**
1. Inspect page source (check for RSS link, JSON API, etc.)
2. Test scraping methods (BeautifulSoup vs feedparser)
3. Extract sample dataset
4. Manually review for kid-relevance (likely high)
5. Document approach

**Definition of Done:**
- Findings documented with metrics
- Sample data stored in `data/samples/library_sample.html` (or RSS)
- Recommended scraping method identified

---

#### E1.3: Evaluate Nevada County Calendar
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Research/Spike

**As a** developer
**I want to** scrape a sample dataset from Nevada County government calendar
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 20 events from county calendar
- [ ] Extract all available fields
- [ ] Document metadata completeness
- [ ] Calculate kid-relevance ratio (expected: lower than library)
- [ ] Measure scraping difficulty (1-5 scale)
- [ ] Check for iCal export option (easier than HTML scraping)
- [ ] Store findings in `docs/source-evaluation.md` (County section)

**Technical Tasks:**
1. Locate county calendar URL
2. Check for iCal/RSS export links
3. Scrape sample (iCal preferred, HTML fallback)
4. Assess kid-relevance (may be low - government/senior events)
5. Document

**Definition of Done:**
- Findings documented with metrics
- Sample data stored
- Recommendation: Include or skip for MVP?

---

#### E1.4: Prioritize Sources for MVP
**Story Points:** 2
**Priority:** P0 (Critical)
**Type:** Decision/Planning

**As a** product owner
**I want to** rank sources by value/effort ratio
**So that** I focus MVP development on highest-ROI sources

**Acceptance Criteria:**
- [ ] Complete evaluation matrix with scores for all Tier 1 sources
- [ ] Scoring dimensions: Volume, Kid-Relevance %, Metadata Quality, Scraping Difficulty
- [ ] Apply weights (e.g., kid-relevance 2x > volume)
- [ ] Rank sources 1-3
- [ ] Document decision rationale in `docs/source-evaluation.md`
- [ ] Update PROJECT-BRIEF.md with final MVP source selection

**Evaluation Matrix:**
| Source | Volume (0-10) | Kid % (0-10) | Quality (0-10) | Difficulty (1-5) | Weighted Score |
|--------|---------------|--------------|----------------|------------------|----------------|
| KNCO   | ? | ? | ? | 3 | ? |
| Library| ? | ? | ? | ? | ? |
| County | ? | ? | ? | ? | ? |

**Weighting Formula:**
```
Score = (Volume * 1) + (Kid% * 2) + (Quality * 1.5) - (Difficulty * 2)
```

**Definition of Done:**
- Matrix completed with documented scores
- Top 3 sources selected (or decision to use all Tier 1)
- Team alignment on which scrapers to build

---

### Epic 2: Core Scraping Engine

---

#### E2.1: Python Project Setup
**Story Points:** 2
**Priority:** P0 (Critical)
**Type:** Infrastructure

**As a** developer
**I want to** initialize a Python project with proper structure
**So that** I have a solid foundation for development

**Acceptance Criteria:**
- [ ] Create virtual environment (`python -m venv venv`)
- [ ] Activate venv and verify isolation
- [ ] Create `requirements.txt` with base dependencies
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Create project directory structure (see below)
- [ ] Create `.env.example` with required variables
- [ ] Create `.gitignore` (exclude venv, .env, __pycache__)
- [ ] Create `README.md` with setup instructions
- [ ] Verify Python 3.11+ (`python --version`)

**Directory Structure:**
```
nevada-county-kids-events/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   └── base.py
│   ├── processors/
│   │   └── __init__.py
│   ├── storage/
│   │   └── __init__.py
│   └── delivery/
│       └── __init__.py
├── tests/
│   └── __init__.py
└── data/
    └── samples/
```

**Requirements.txt:**
```
requests>=2.31.0
beautifulsoup4>=4.12.0
feedparser>=6.0.10
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

**Definition of Done:**
- Project structure created
- Dependencies installed without errors
- Can run `python -m src --help` (even if empty)
- Git initialized with first commit

---

#### E2.2: KNCO RSS Scraper
**Story Points:** 5
**Priority:** P0 (Critical)
**Type:** Feature

**As a** developer
**I want to** fetch and parse events from KNCO Trumba RSS feed
**So that** I can extract structured event data

**Acceptance Criteria:**
- [ ] Implement `src/scrapers/base.py` with `BaseScraper` abstract class
- [ ] Implement `src/scrapers/knco.py` with `KNCOScraper(BaseScraper)`
- [ ] Fetch RSS feed via HTTP GET (handle 404/timeout)
- [ ] Parse XML using `feedparser`
- [ ] Extract fields (see below)
- [ ] Handle HTML entities (`&amp;nbsp;` → ` `)
- [ ] Extract `source_event_id` from GUID (regex: `event/(\d+)`)
- [ ] Return list of normalized event dictionaries
- [ ] Log scraping statistics (events found, errors)
- [ ] Unit test with sample RSS fixture

**Fields to Extract:**
```python
{
    'title': str (required),
    'description': str (required, strip HTML tags),
    'event_date': str (required, ISO format),
    'venue': str (optional, parse from description),
    'city_area': str (optional, parse from description),
    'age_range': str (optional, parse from description),
    'price': str (optional, parse from description),
    'is_free': bool (infer from price or keywords),
    'source_url': str (required, RSS item link),
    'source_event_id': str (required, from GUID),
}
```

**HTML Parsing Example:**
```
Description HTML:
<b>City/Area</b>:&amp;nbsp;Nevada City<br/>
<b>Age</b>:&nbsp;3-5 years<br/>
<b>Price</b>: Free

Extracted:
city_area = "Nevada City"
age_range = "3-5 years"
price = "Free"
is_free = True
```

**Definition of Done:**
- Scraper returns 200+ events from KNCO
- All fields extracted correctly (validated with sample)
- Unit test passes with fixture
- No unhandled exceptions

---

#### E2.3: Data Normalizer
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Feature

**As a** developer
**I want to** transform scraper output into standardized schema
**So that** events from different sources are consistent

**Acceptance Criteria:**
- [ ] Implement `src/processors/normalizer.py`
- [ ] Define `NormalizedEvent` dataclass (matches DB schema)
- [ ] Validate required fields (title, event_date, source_name)
- [ ] Parse date strings to `datetime` objects (handle ISO 8601, other formats)
- [ ] Generate `content_hash` (MD5 of title+date+description)
- [ ] Set default values for missing optional fields (`None`)
- [ ] Calculate `quality_score` (0-100 based on completeness)
- [ ] Log validation errors (missing required fields)
- [ ] Return list of `NormalizedEvent` objects
- [ ] Unit test with various input formats

**Content Hash Algorithm:**
```python
import hashlib

def generate_content_hash(event):
    content = f"{event['title']}|{event['event_date']}|{event['description'][:200]}"
    return hashlib.md5(content.encode()).hexdigest()
```

**Quality Score:**
```python
score = 0
score += 20 if event.title else 0
score += 20 if event.event_date else 0
score += 20 if event.description else 0
score += 10 if event.venue else 0
score += 10 if event.age_range else 0
score += 10 if event.price else 0
score += 10 if len(event.description) > 50 else 0
# Max: 100
```

**Definition of Done:**
- Normalizer handles all scrapers' output formats
- Validation catches missing required fields
- Unit tests pass with edge cases
- Quality scores are reasonable

---

#### E2.4: Supabase Integration
**Story Points:** 5
**Priority:** P0 (Critical)
**Type:** Feature

**As a** developer
**I want to** store normalized events in Supabase Postgres
**So that** data persists for caching and retrieval

**Acceptance Criteria:**
- [ ] Implement `src/storage/supabase.py` with `SupabaseClient` class
- [ ] Load credentials from `.env` (SUPABASE_URL, SUPABASE_KEY)
- [ ] Connect to Postgres using `psycopg2`
- [ ] Implement `upsert_events(events: List[NormalizedEvent])`
  - SQL: INSERT ... ON CONFLICT ... DO UPDATE
  - Handle conflict on `(source_name, source_event_id)`
  - Update `scraped_at` timestamp on conflict
  - Batch insert (single transaction)
- [ ] Implement `get_cached_events(source_name, ttl_hours=6)`
  - Query by source, filter by `scraped_at > NOW() - INTERVAL`
  - Return list of event dicts
- [ ] Test connection on init (fail fast if unreachable)
- [ ] Log SQL errors with context
- [ ] Integration test with real Supabase instance

**UPSERT SQL:**
```sql
INSERT INTO events (
  title, description, event_date, venue, city_area,
  source_name, source_url, source_event_id, content_hash,
  age_range, price, is_free, quality_score, scraped_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (source_name, source_event_id)
DO UPDATE SET
  title = EXCLUDED.title,
  description = EXCLUDED.description,
  event_date = EXCLUDED.event_date,
  venue = EXCLUDED.venue,
  city_area = EXCLUDED.city_area,
  age_range = EXCLUDED.age_range,
  price = EXCLUDED.price,
  is_free = EXCLUDED.is_free,
  quality_score = EXCLUDED.quality_score,
  scraped_at = NOW();
```

**Definition of Done:**
- Events saved to Supabase successfully
- UPSERT prevents duplicates (same run)
- Cache query returns correct events
- Integration test passes

---

#### E2.5: Cache Layer
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Feature

**As a** developer
**I want to** check cache before scraping
**So that** repeat queries within TTL are instant

**Acceptance Criteria:**
- [ ] Implement `src/storage/cache.py` with `CacheManager` class
- [ ] Method: `get_or_fetch(source_name, scraper_func, ttl_hours=6)`
  - Check DB for cached events (`get_cached_events()`)
  - If found: Return cached (log cache HIT)
  - If not found: Call scraper, store, return (log cache MISS)
- [ ] Log cache statistics (hit rate, age of data)
- [ ] Configuration: TTL from env var (`CACHE_TTL_HOURS`)
- [ ] Method: `invalidate_cache(source_name)` for testing
- [ ] Unit test with mocked DB and scraper

**Cache Logic:**
```python
def get_or_fetch(source_name, scraper_func, ttl_hours=6):
    cached = self.db.get_cached_events(source_name, ttl_hours)
    if cached:
        age = datetime.now() - cached[0]['scraped_at']
        logger.info(f"Cache HIT for {source_name}: {len(cached)} events (age: {age})")
        return cached

    logger.info(f"Cache MISS for {source_name}, scraping...")
    events = scraper_func()
    self.db.upsert_events(events)
    return events
```

**Definition of Done:**
- Cache hit returns existing data
- Cache miss triggers scrape + store
- TTL configurable via .env
- Unit tests pass

---

#### E2.6: Orchestrator (Single Source)
**Story Points:** 3
**Priority:** P0 (Critical)
**Type:** Feature

**As a** developer
**I want to** coordinate scraping, normalization, and storage
**So that** I have end-to-end working prototype

**Acceptance Criteria:**
- [ ] Implement `src/orchestrator.py` with `EventOrchestrator` class
- [ ] Method: `fetch_events(sources=['knco'], use_cache=True)`
  - Get scraper instance for each source
  - Use cache manager to get/fetch events
  - Normalize events
  - Return combined list
- [ ] CLI interface: `python -m src.orchestrator --source knco`
- [ ] Log execution summary (sources, events found, cache hits, duration)
- [ ] Handle scraper errors gracefully (log, continue)
- [ ] Integration test: Full pipeline, verify DB contains events

**CLI Example:**
```bash
$ python -m src.orchestrator --source knco
[INFO] Fetching events from: knco
[INFO] Cache MISS for knco, scraping...
[INFO] Scraped 200 events from KNCO
[INFO] Normalized 200 events (0 validation errors)
[INFO] Upserted 200 events to database
[SUCCESS] Total: 200 events (execution time: 3.2s)
```

**Definition of Done:**
- CLI script runs without errors
- 200+ events in Supabase after run
- Second run shows cache HIT
- Integration test passes

---

### Epic 3: Multi-Source Integration

*(Stories E3.1 - E3.5 follow same detail pattern as above)*

**Summary:**
- E3.1: Library Scraper (5 pts) - Build second scraper
- E3.2: County Scraper (5 pts) - Build third scraper
- E3.3: Deduplication (5 pts) - Cross-source matching logic
- E3.4: Parallel Scraping (3 pts) - Concurrent execution
- E3.5: Quality Validation (3 pts) - Data quality checks

---

### Epic 4: Delivery Layer

**Summary:**
- E4.1: Delivery Interface (2 pts) - Abstract base class
- E4.2: Email Delivery (5 pts) - SMTP with HTML template
- E4.3: Telegram Delivery (5 pts) - Telegram bot integration
- E4.4: Google Calendar (8 pts) - OAuth + Calendar API
- E4.5: Delivery Router (3 pts) - Method selection logic

---

### Epic 5: Slash Command Interface

**Summary:**
- E5.1: Command Design (2 pts) - `.claude/commands/get-events.md`
- E5.2: Command Orchestration (3 pts) - Parse args, execute pipeline
- E5.3: Conversational Selection (3 pts) - Interactive delivery choice
- E5.4: Error Handling (3 pts) - User-friendly error messages
- E5.5: Documentation (2 pts) - README, help text

---

### Epic 6: Polish & Optimization

**Summary:**
- E6.1: Categorization (5 pts) - Event type classification
- E6.2: Kid-Friendly Scoring (5 pts) - Relevance algorithm
- E6.3: Summarization (3 pts) - One-sentence summaries

---

## Dependency Map

```
E1: Source Research (11 pts)
 └─> E1.1, E1.2, E1.3 (parallel)
      └─> E1.4 (decision)
           └─> E2: Core Engine (21 pts)
                ├─> E2.1 (setup)
                │    └─> E2.2 (scraper)
                │         ├─> E2.3 (normalizer)
                │         └─> E2.4 (storage)
                │              └─> E2.5 (cache)
                │                   └─> E2.6 (orchestrator)
                │                        ├─> E3: Multi-Source (21 pts)
                │                        │    ├─> E3.1, E3.2 (parallel)
                │                        │    │    └─> E3.3 (dedup)
                │                        │    │         ├─> E3.4 (parallel scraping)
                │                        │    │         └─> E3.5 (quality)
                │                        │    │
                │                        └─> E4: Delivery (23 pts)
                │                             ├─> E4.1 (interface)
                │                             │    ├─> E4.2 (email) \
                │                             │    ├─> E4.3 (telegram) > E4.5 (router)
                │                             │    └─> E4.4 (gcal)   /
                │                             │
                │                             └─> E5: Slash Command (13 pts)
                │                                  ├─> E5.1 (design)
                │                                  │    └─> E5.2 (orchestration)
                │                                  │         ├─> E5.3 (conversational)
                │                                  │         ├─> E5.4 (errors)
                │                                  │         └─> E5.5 (docs)
                │                                  │              └─> **MVP COMPLETE**
                │                                  │
                │                                  └─> E6: Polish (13 pts)
                │                                       ├─> E6.1 (categorization)
                │                                       ├─> E6.2 (scoring)
                │                                       └─> E6.3 (summarization)
```

---

## Velocity Tracking

### Sprint Velocity Table

| Sprint | Planned Points | Completed Points | Velocity | Notes |
|--------|---------------|------------------|----------|-------|
| 0 (Research) | 11 | - | - | Source evaluation |
| 1 (Foundation) | 21 | - | - | Single-source prototype |
| 2 (Multi-Source) | 21 | - | - | 3 scrapers + dedup |
| 3 (Delivery) | 15-23 | - | - | Email + Telegram (+ GCal?) |
| 4 (MVP) | 13 | - | - | Slash command |
| 5+ (Polish) | Variable | - | - | Post-MVP enhancements |

**Fill in "Completed Points" after each sprint to track actual velocity.**

---

## Story Point Estimation Guide

**1 point:** Trivial (1 hour or less)
- Update configuration
- Write simple documentation

**2 points:** Simple (2-4 hours)
- Basic file/class creation
- Simple integration

**3 points:** Moderate (4-8 hours)
- Feature with clear requirements
- Some complexity, few unknowns

**5 points:** Complex (1-2 days)
- Significant feature
- Multiple components
- Some unknowns

**8 points:** Very Complex (3-5 days)
- Large feature
- Many dependencies
- Research required

**13 points:** Epic-level (1+ week)
- Should be broken down into smaller stories

---

## Burndown Tracking

**Total MVP Points:** 87 (Epics 1-5)
**Total Project Points:** 102 (including Epic 6)

### Sprint-by-Sprint Burndown

| After Sprint | Points Remaining | % Complete |
|--------------|------------------|------------|
| Start | 102 | 0% |
| Sprint 0 | 91 | 11% |
| Sprint 1 | 70 | 31% |
| Sprint 2 | 49 | 52% |
| Sprint 3 | 26-34 | 66-74% |
| Sprint 4 (MVP) | 13 | 87% |
| Sprint 5+ | 0 | 100% |

---

## Ready for Development Checklist

Before starting Sprint 0:
- [ ] Project brief approved
- [ ] PRD reviewed
- [ ] Scrum backlog reviewed (this document)
- [ ] Supabase database accessible
- [ ] Development environment ready (Python 3.11+)
- [ ] Source URLs confirmed accessible
- [ ] Time allocated for research sprint

---

## Notes & Conventions

**Story Status Icons:**
- 🔵 Ready (no blockers)
- ⏸️ Blocked (dependency not met)
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked (external issue)

**Priority Levels:**
- P0: Critical (blocks MVP)
- P1: High (important for MVP)
- P2: Low (post-MVP enhancement)
- P3: Nice-to-have (backlog)

**Acceptance Criteria Format:**
- [ ] Checkbox format for easy tracking
- Measurable, testable conditions
- No ambiguity in "done"

---

**Document Status:** ✅ Ready for Sprint Planning
**Next Action:** Begin Sprint 0 (Source Research)
**Estimated MVP Timeline:** 4-5 sprints (flexible, no hard deadlines)

---

*End of Scrum Backlog*
