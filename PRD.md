# Nevada County Kids Events Agent - Product Requirements Document (PRD)

**Product Name:** Nevada County Kids Events Agent
**Version:** 1.0 (MVP)
**Status:** 🟡 Planning
**Document Owner:** Project Owner + Mary (Business Analyst)
**Created:** 2025-10-07
**Last Updated:** 2025-10-07

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [User Stories & Requirements](#user-stories--requirements)
3. [Epic Breakdown](#epic-breakdown)
4. [Technical Specifications](#technical-specifications)
5. [API Contracts & Interfaces](#api-contracts--interfaces)
6. [Data Models](#data-models)
7. [Acceptance Criteria](#acceptance-criteria)
8. [Dependencies & Constraints](#dependencies--constraints)
9. [Release Plan](#release-plan)
10. [Appendices](#appendices)

---

## Product Overview

### Vision Statement
Enable Nevada County parents to discover kid-friendly local events through a single conversational command, eliminating the need to manually search across fragmented sources.

### Problem Statement
Parents spend 30+ minutes weekly hunting for kid activities across 10+ websites, calendars, and community boards. Most events are buried in generic calendars mixing adult/senior content, and obscure posting locations cause families to miss opportunities.

### Solution
A Claude Code slash command (`/get-events`) that scrapes, deduplicates, and synthesizes events from prioritized sources on demand, delivering results via user-selected method (email, Telegram, Google Calendar).

### Target Users
- **Primary:** Project owner (parent in Nevada County)
- **Secondary:** Other local parents (future expansion)

### Success Metrics (MVP)
- ✅ Command completes end-to-end in <2 minutes
- ✅ Returns events from 3+ sources
- ✅ <5% duplicate events in results
- ✅ At least 2 delivery methods functional
- ✅ User satisfaction: "More fun than frustrating"

---

## User Stories & Requirements

### Epic 1: Source Research & Evaluation

#### Story 1.1: Evaluate KNCO RSS Feed
**As a** developer
**I want to** scrape a sample dataset from KNCO Trumba RSS
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 50 events from KNCO feed
- [ ] Extract all available fields (title, description, date, location, age range, etc.)
- [ ] Document metadata completeness (% events with each field)
- [ ] Calculate kid-relevance ratio (manual review of sample)
- [ ] Measure scraping difficulty (1-5 scale with justification)
- [ ] Store findings in `docs/source-evaluation.md`

**Technical Notes:**
- URL: `http://uid.trumba.com/...` (existing from n8n attempt)
- Format: RSS/XML (Trumba-specific schema)
- Known challenges: HTML entity encoding (`&amp;nbsp;` vs `&nbsp;`)

---

#### Story 1.2: Evaluate Nevada County Library
**As a** developer
**I want to** scrape a sample dataset from Nevada County Library calendar
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 20 events from library calendar
- [ ] Extract all available fields
- [ ] Document metadata completeness
- [ ] Calculate kid-relevance ratio
- [ ] Measure scraping difficulty (1-5 scale)
- [ ] Store findings in `docs/source-evaluation.md`

**Technical Notes:**
- URL: https://nevadacounty.librarymarket.com/events
- Format: LibCal HTML (may have RSS option)
- Expected: High kid-relevance (library programs)

---

#### Story 1.3: Evaluate Nevada County Calendar
**As a** developer
**I want to** scrape a sample dataset from Nevada County government calendar
**So that** I can assess event volume, quality, and kid-relevance

**Acceptance Criteria:**
- [ ] Fetch at least 20 events from county calendar
- [ ] Extract all available fields
- [ ] Document metadata completeness
- [ ] Calculate kid-relevance ratio (likely lower than others)
- [ ] Measure scraping difficulty (1-5 scale)
- [ ] Check for iCal export option (easier than HTML scraping)
- [ ] Store findings in `docs/source-evaluation.md`

**Technical Notes:**
- Format: Unknown (investigate iCal vs HTML)
- Expected: Lower kid-relevance (government/senior events mixed in)

---

#### Story 1.4: Prioritize Sources for MVP
**As a** product owner
**I want to** rank sources by value/effort ratio
**So that** I focus MVP development on highest-ROI sources

**Acceptance Criteria:**
- [ ] Complete evaluation matrix with scores for all Tier 1 sources
- [ ] Scoring dimensions: Volume, Kid-Relevance %, Metadata Quality, Scraping Difficulty
- [ ] Weight dimensions (e.g., kid-relevance > volume)
- [ ] Rank sources 1-3
- [ ] Document decision rationale in `docs/source-evaluation.md`
- [ ] Update PROJECT-BRIEF.md with final source selection

**Decision Matrix Template:**
| Source | Volume (0-10) | Kid % (0-10) | Quality (0-10) | Difficulty (1-5) | Weighted Score |
|--------|---------------|--------------|----------------|------------------|----------------|
| KNCO   | ? | ? | ? | 3 | ? |
| Library| ? | ? | ? | ? | ? |
| County | ? | ? | ? | ? | ? |

---

### Epic 2: Core Scraping Engine (Single Source)

#### Story 2.1: Set Up Python Project Structure
**As a** developer
**I want to** initialize a Python project with proper structure and dependencies
**So that** I have a solid foundation for development

**Acceptance Criteria:**
- [ ] Create virtual environment (`venv`)
- [ ] Initialize `requirements.txt` with base dependencies:
  - `requests>=2.31.0`
  - `beautifulsoup4>=4.12.0`
  - `feedparser>=6.0.10`
  - `psycopg2-binary>=2.9.9`
  - `python-dotenv>=1.0.0`
- [ ] Create project directory structure (see Technical Specs)
- [ ] Initialize git repository (if not already)
- [ ] Create `.env.example` with required environment variables
- [ ] Create `README.md` with setup instructions
- [ ] Verify `python --version` >= 3.11

**Environment Variables:**
```
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon_key]
CACHE_TTL_HOURS=6
```

---

#### Story 2.2: Build KNCO RSS Scraper
**As a** developer
**I want to** fetch and parse events from KNCO Trumba RSS feed
**So that** I can extract structured event data

**Acceptance Criteria:**
- [ ] Implement `src/scrapers/knco.py` with `KNCOScraper` class
- [ ] Inherit from `BaseScraper` abstract class
- [ ] Fetch RSS feed via HTTP GET (handle 404/timeout errors)
- [ ] Parse XML using `feedparser`
- [ ] Extract fields for each event:
  - `title` (required)
  - `description` (required)
  - `event_date` (required, parse to datetime)
  - `venue` (optional, extract from description HTML)
  - `city_area` (optional, extract from description HTML)
  - `age_range` (optional, extract from description HTML)
  - `price` (optional, extract from description HTML)
  - `source_event_id` (required, extract from `<guid>`)
  - `source_url` (required, RSS item link)
- [ ] Return list of normalized event dictionaries
- [ ] Handle HTML entities (`&amp;nbsp;` → ` `)
- [ ] Log scraping statistics (events found, parse errors, etc.)
- [ ] Unit test with sample RSS fixture

**Technical Notes:**
- Use regex patterns for HTML metadata extraction (from n8n learnings)
- Handle both `&nbsp;` and `&amp;nbsp;` variations
- GUID format: `http://uid.trumba.com/event/177609910` → extract `177609910`

---

#### Story 2.3: Build Data Normalizer
**As a** developer
**I want to** transform scraper output into standardized schema
**So that** events from different sources are consistent

**Acceptance Criteria:**
- [ ] Implement `src/processors/normalizer.py`
- [ ] Define `NormalizedEvent` schema (matches DB schema)
- [ ] Validate required fields (title, event_date, source_name)
- [ ] Parse date strings to `datetime` objects (handle multiple formats)
- [ ] Generate `content_hash` for deduplication (hash of title+date+description)
- [ ] Set default values for missing optional fields
- [ ] Log validation errors (events with missing required fields)
- [ ] Return list of validated `NormalizedEvent` objects
- [ ] Unit test with various input formats

**Content Hash Algorithm:**
```python
import hashlib
content = f"{title}|{event_date.isoformat()}|{description[:200]}"
content_hash = hashlib.md5(content.encode()).hexdigest()
```

---

#### Story 2.4: Integrate Supabase Storage
**As a** developer
**I want to** store normalized events in Supabase Postgres
**So that** data persists for caching and retrieval

**Acceptance Criteria:**
- [ ] Implement `src/storage/supabase.py` with `SupabaseClient` class
- [ ] Connect to Supabase using `psycopg2` (credentials from `.env`)
- [ ] Implement `upsert_events()` method:
  - SQL: `INSERT ... ON CONFLICT (source_name, source_event_id) DO UPDATE ...`
  - Handle conflict on unique index `idx_source_event_unique`
  - Update `scraped_at` timestamp on conflict
  - Batch insert (multiple events in single transaction)
- [ ] Implement `get_cached_events()` method:
  - Query events by `source_name`
  - Filter by `scraped_at > NOW() - INTERVAL '6 hours'` (cache TTL)
  - Return list of event dictionaries
- [ ] Implement connection pooling for efficiency
- [ ] Log SQL errors with event context
- [ ] Test connection on initialization (fail fast if DB unreachable)
- [ ] Integration test with real Supabase instance

**SQL Template:**
```sql
INSERT INTO events (
  title, description, event_date, venue, city_area,
  source_name, source_url, source_event_id, content_hash,
  age_range, price, scraped_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (source_name, source_event_id)
DO UPDATE SET
  title = EXCLUDED.title,
  description = EXCLUDED.description,
  event_date = EXCLUDED.event_date,
  venue = EXCLUDED.venue,
  city_area = EXCLUDED.city_area,
  age_range = EXCLUDED.age_range,
  price = EXCLUDED.price,
  scraped_at = NOW();
```

---

#### Story 2.5: Implement Cache Layer
**As a** developer
**I want to** check cache before scraping
**So that** repeat queries within TTL window are instant

**Acceptance Criteria:**
- [ ] Implement `src/storage/cache.py` with `CacheManager` class
- [ ] Method: `get_or_fetch(source_name, scraper_func, ttl_hours=6)`
  - Check DB for events with `scraped_at > NOW() - ttl_hours`
  - If found: Return cached events (log cache hit)
  - If not found: Call `scraper_func()`, store results, return
- [ ] Log cache statistics (hit rate, age of cached data)
- [ ] Configuration: TTL hours from environment variable
- [ ] Manual cache invalidation method (for testing)
- [ ] Unit test with mocked DB and scraper

**Cache Logic:**
```python
def get_or_fetch(source_name, scraper_func, ttl_hours=6):
    cached = db.get_cached_events(source_name, ttl_hours)
    if cached:
        logger.info(f"Cache HIT for {source_name} ({len(cached)} events)")
        return cached

    logger.info(f"Cache MISS for {source_name}, scraping...")
    events = scraper_func()
    db.upsert_events(events)
    return events
```

---

#### Story 2.6: Build Single-Source Orchestrator
**As a** developer
**I want to** coordinate scraping, normalization, and storage
**So that** I have end-to-end working prototype

**Acceptance Criteria:**
- [ ] Implement `src/orchestrator.py` with `EventOrchestrator` class
- [ ] Method: `fetch_events(sources=['knco'], use_cache=True)`
  - For each source, get scraper instance
  - Use cache manager to get/fetch events
  - Normalize events
  - Return combined list
- [ ] Log execution summary (sources queried, events found, cache hits)
- [ ] Handle scraper errors gracefully (log error, continue with other sources)
- [ ] Command-line interface for testing: `python -m src.orchestrator --source knco`
- [ ] Integration test: Run full pipeline, verify DB contains events

**Expected Output:**
```
$ python -m src.orchestrator --source knco
[INFO] Fetching events from: knco
[INFO] Cache MISS for knco, scraping...
[INFO] Scraped 200 events from KNCO Trumba RSS
[INFO] Normalized 200 events (0 validation errors)
[INFO] Upserted 200 events to database
[SUCCESS] Total events fetched: 200
```

---

### Epic 3: Multi-Source Integration & Deduplication

#### Story 3.1: Build Library Calendar Scraper
**As a** developer
**I want to** scrape events from Nevada County Library
**So that** I can aggregate a second source

**Acceptance Criteria:**
- [ ] Implement `src/scrapers/library.py` with `LibraryScraper` class
- [ ] Inherit from `BaseScraper` abstract class
- [ ] Determine optimal scraping method (RSS vs HTML parsing)
- [ ] Extract same fields as KNCO scraper
- [ ] Handle library-specific HTML structure
- [ ] Set `source_name = 'library'`
- [ ] Return normalized event dictionaries
- [ ] Unit test with sample data fixture
- [ ] Document scraping approach in code comments

**Investigation:**
- Check for RSS feed option first (easier)
- If HTML: Use BeautifulSoup with CSS selectors
- LibCal may have structured JSON API (investigate)

---

#### Story 3.2: Build County Calendar Scraper
**As a** developer
**I want to** scrape events from Nevada County government calendar
**So that** I can aggregate a third source

**Acceptance Criteria:**
- [ ] Implement `src/scrapers/county.py` with `CountyScraper` class
- [ ] Inherit from `BaseScraper` abstract class
- [ ] Check for iCal export option (use `icalendar` library if available)
- [ ] Fallback to HTML scraping if no iCal
- [ ] Extract same fields as other scrapers
- [ ] Set `source_name = 'county'`
- [ ] Return normalized event dictionaries
- [ ] Unit test with sample data
- [ ] Document scraping approach

**Priority:**
- iCal > RSS > HTML (in order of ease)

---

#### Story 3.3: Implement Cross-Source Deduplication
**As a** developer
**I want to** detect duplicate events across sources
**So that** users don't see the same event multiple times

**Acceptance Criteria:**
- [ ] Implement `src/processors/deduplicator.py` with `Deduplicator` class
- [ ] Method: `deduplicate(events_list) -> deduplicated_events_list`
- [ ] Strategy 1: Exact match on `content_hash`
- [ ] Strategy 2: Fuzzy match on title similarity + date proximity
  - Use Levenshtein distance or similar (consider `python-Levenshtein`)
  - Threshold: 85% title similarity + same date = duplicate
- [ ] When duplicates found:
  - Keep event from prioritized source (KNCO > Library > County)
  - Merge metadata (take non-null values from all duplicates)
  - Log deduplication action
- [ ] Return deduplicated list with metadata count
- [ ] Unit test with synthetic duplicates (exact and fuzzy)

**Example:**
```
Input:
  - KNCO: "Story Time at Library" (2025-10-15, venue=null)
  - Library: "Storytime @ Main Branch" (2025-10-15, venue="Main Library")

Output:
  - "Story Time at Library" (2025-10-15, venue="Main Library") [merged]
```

---

#### Story 3.4: Parallel Scraping with Timeout
**As a** developer
**I want to** scrape multiple sources concurrently
**So that** total execution time is minimized

**Acceptance Criteria:**
- [ ] Update `EventOrchestrator` to use `concurrent.futures.ThreadPoolExecutor`
- [ ] Launch scraper threads in parallel (max workers = # sources)
- [ ] Set timeout per source (30 seconds default, configurable)
- [ ] If source times out: Log warning, continue with other sources
- [ ] If source errors: Log error, continue with other sources
- [ ] Aggregate results from successful sources
- [ ] Log execution summary (which sources succeeded/failed, total time)
- [ ] Integration test: Mock slow source, verify timeout works

**Expected Behavior:**
```
$ python -m src.orchestrator --sources knco,library,county
[INFO] Scraping 3 sources in parallel...
[INFO] knco completed in 2.3s (200 events)
[INFO] library completed in 1.8s (30 events)
[WARN] county timed out after 30s (0 events)
[SUCCESS] Total: 230 events from 2/3 sources
```

---

#### Story 3.5: Data Quality Validation
**As a** developer
**I want to** flag low-quality events
**So that** users can filter or deprioritize incomplete data

**Acceptance Criteria:**
- [ ] Define quality score algorithm (0-100)
  - Required fields present (+20 each): title, date, description
  - Optional fields present (+10 each): venue, age_range, price
  - Description length > 50 chars (+10)
  - Future event (not past) (+10)
- [ ] Add `quality_score` field to normalized events
- [ ] Log quality statistics (avg score, % low-quality events)
- [ ] Option to filter events below quality threshold
- [ ] Unit test scoring algorithm

**Quality Tiers:**
- **High:** 80-100 (complete metadata)
- **Medium:** 50-79 (missing some fields)
- **Low:** 0-49 (minimal data, consider excluding)

---

### Epic 4: Delivery Layer

#### Story 4.1: Design Delivery Interface
**As a** developer
**I want to** create an abstract delivery interface
**So that** adding new delivery methods is consistent

**Acceptance Criteria:**
- [ ] Implement `src/delivery/base.py` with `BaseDelivery` abstract class
- [ ] Define interface methods:
  - `deliver(events_list, **options) -> DeliveryResult`
  - `validate_config() -> bool` (check credentials/settings)
  - `format_events(events_list) -> formatted_output`
- [ ] Define `DeliveryResult` dataclass (success, message, metadata)
- [ ] Document interface contract in docstrings
- [ ] Create example implementation for testing

**Interface:**
```python
from abc import ABC, abstractmethod

class BaseDelivery(ABC):
    @abstractmethod
    def deliver(self, events: List[dict], **options) -> DeliveryResult:
        """Send events via this delivery method"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Check if delivery method is properly configured"""
        pass
```

---

#### Story 4.2: Build Email Delivery
**As a** user
**I want to** receive events via email
**So that** I can read them in my inbox

**Acceptance Criteria:**
- [ ] Implement `src/delivery/email.py` with `EmailDelivery` class
- [ ] Use `smtplib` for sending (Gmail SMTP or configurable)
- [ ] Create HTML email template:
  - Subject: "Nevada County Kids Events - [Date Range]"
  - Header with summary (X events found)
  - Event cards with: title, date, venue, description, source
  - Footer with timestamp
- [ ] Format events into HTML using template
- [ ] Send email to configured recipient (from `.env`)
- [ ] Handle SMTP errors gracefully (auth failure, network issues)
- [ ] Return `DeliveryResult` with success status
- [ ] Test with real email (manual verification)

**Environment Variables:**
```
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=your-email@gmail.com
```

---

#### Story 4.3: Build Telegram Delivery
**As a** user
**I want to** receive events via Telegram
**So that** I can read them on mobile

**Acceptance Criteria:**
- [ ] Implement `src/delivery/telegram.py` with `TelegramDelivery` class
- [ ] Install `python-telegram-bot` library
- [ ] Create Telegram bot via @BotFather (get token)
- [ ] Format events as Telegram messages (Markdown formatting)
- [ ] Handle message length limits (split into multiple messages if needed)
- [ ] Send to configured chat ID (from `.env`)
- [ ] Handle API errors (invalid token, blocked bot, etc.)
- [ ] Return `DeliveryResult` with success status
- [ ] Test with real Telegram account

**Environment Variables:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

---

#### Story 4.4: Build Google Calendar Integration
**As a** user
**I want to** add events to Google Calendar
**So that** they appear in my calendar app

**Acceptance Criteria:**
- [ ] Implement `src/delivery/gcal.py` with `GoogleCalendarDelivery` class
- [ ] Install `google-api-python-client` and `google-auth` libraries
- [ ] Set up OAuth2 credentials (Google Cloud Console)
- [ ] Authenticate user (one-time OAuth flow, store refresh token)
- [ ] For each event:
  - Create calendar event with title, date, description, location
  - Set event source URL as metadata
  - Avoid duplicates (check if event already exists by source_event_id)
- [ ] Batch create events (API efficiency)
- [ ] Handle API errors (quota exceeded, auth failure)
- [ ] Return `DeliveryResult` with success status
- [ ] Test with real Google Calendar

**OAuth Setup:**
- Create project in Google Cloud Console
- Enable Google Calendar API
- Create OAuth 2.0 credentials (Desktop app)
- Store `credentials.json` (not in git)
- Generate `token.json` on first run (stored locally)

---

#### Story 4.5: Delivery Method Router
**As a** developer
**I want to** route delivery requests to appropriate handler
**So that** orchestrator can support multiple methods

**Acceptance Criteria:**
- [ ] Implement `src/delivery/router.py` with `DeliveryRouter` class
- [ ] Registry of available delivery methods (name -> class mapping)
- [ ] Method: `deliver(events, method_name, **options)`
  - Validate method exists (return error if unknown)
  - Instantiate delivery class
  - Validate configuration (call `validate_config()`)
  - Execute delivery
  - Return result
- [ ] Support multiple simultaneous deliveries (e.g., email + telegram)
- [ ] Log delivery attempts and results
- [ ] Unit test with mocked delivery classes

**Registry:**
```python
DELIVERY_METHODS = {
    'email': EmailDelivery,
    'telegram': TelegramDelivery,
    'gcal': GoogleCalendarDelivery,
}
```

---

### Epic 5: Slash Command Interface

#### Story 5.1: Design Claude Code Command
**As a** developer
**I want to** create a slash command specification
**So that** users can invoke the agent from Claude Code

**Acceptance Criteria:**
- [ ] Create `.claude/commands/get-events.md`
- [ ] Define command syntax and parameters
- [ ] Document usage examples
- [ ] Specify prompt template for command execution
- [ ] Define expected outputs (formatted event list + delivery options)
- [ ] Test command registration in Claude Code

**Command Spec:**
```markdown
# /get-events

Fetch and deliver Nevada County kids events.

## Usage
/get-events [options]

## Options
--sources: Comma-separated list (default: all)
--days: Days ahead to include (default: 14)
--delivery: Method (email|telegram|gcal) (default: ask)
--no-cache: Force fresh scrape

## Examples
/get-events
/get-events --sources knco,library --days 7 --delivery email
```

---

#### Story 5.2: Build Command Orchestration
**As a** developer
**I want to** parse command arguments and execute workflow
**So that** the slash command triggers the full pipeline

**Acceptance Criteria:**
- [ ] Update `EventOrchestrator` with `execute_command(args)` method
- [ ] Parse command arguments (--sources, --days, --delivery, --no-cache)
- [ ] Apply date range filter (next X days)
- [ ] Call scraping pipeline (with or without cache)
- [ ] If delivery method specified: Auto-deliver
- [ ] If no delivery method: Present options conversationally
- [ ] Return formatted summary for Claude Code to display
- [ ] Handle errors gracefully (show user-friendly messages)

**Execution Flow:**
```
User: /get-events --days 7
Agent: Fetching events for next 7 days...
Agent: [Scrapes sources]
Agent: Found 42 events from 3 sources (15 KNCO, 12 Library, 15 County)
Agent: How would you like to receive them?
  1. Email
  2. Telegram
  3. Google Calendar
  4. Show in terminal
User: 1
Agent: [Delivers via email]
Agent: ✅ Sent 42 events to your inbox!
```

---

#### Story 5.3: Conversational Delivery Selection
**As a** user
**I want to** choose delivery method interactively
**So that** I don't have to remember command flags

**Acceptance Criteria:**
- [ ] After fetching events, present delivery options as numbered list
- [ ] Accept user input (number or method name)
- [ ] Validate input (reject invalid choices)
- [ ] Execute chosen delivery method
- [ ] Provide confirmation message with details
- [ ] Option to deliver via multiple methods ("all" or "1,2")
- [ ] Remember last choice (optional: use as default next time)

**Example Interaction:**
```
Agent: Found 28 events. How would you like them?
  1. Email (your-email@gmail.com)
  2. Telegram (@yourusername)
  3. Google Calendar (Primary Calendar)
  4. Show here

User: 2
Agent: Sending to Telegram...
Agent: ✅ Delivered 28 events to @yourusername
```

---

#### Story 5.4: Error Handling & User Feedback
**As a** user
**I want to** understand what went wrong if command fails
**So that** I can fix issues or retry

**Acceptance Criteria:**
- [ ] Catch all exception types at orchestrator level
- [ ] Classify errors:
  - **User Error:** Invalid arguments, bad configuration
  - **Scraper Error:** Source unreachable, parse failure
  - **Delivery Error:** SMTP auth failure, API quota
  - **System Error:** Database connection, unexpected exceptions
- [ ] Provide user-friendly error messages with actionable guidance
- [ ] Log technical details for debugging (stack traces)
- [ ] Graceful degradation: Show partial results if some sources fail
- [ ] Suggest fixes (e.g., "Check SMTP credentials in .env")

**Error Examples:**
```
❌ Source 'knco' failed: Connection timeout
   → Showing events from other sources (library, county)

❌ Email delivery failed: Invalid SMTP credentials
   → Check EMAIL_PASSWORD in .env file

❌ No events found for next 7 days
   → Try expanding date range (--days 14)
```

---

#### Story 5.5: Command Documentation & Help
**As a** user
**I want to** see usage documentation
**So that** I understand how to use the command

**Acceptance Criteria:**
- [ ] Create `README.md` in project root with:
  - Quick start guide
  - Installation instructions
  - Command usage examples
  - Configuration guide (.env setup)
  - Troubleshooting section
- [ ] Add docstrings to all public methods
- [ ] Create `--help` flag for command
- [ ] Document delivery method setup (OAuth for GCal, bot token for Telegram)
- [ ] Include sample outputs and screenshots

**README Sections:**
- Installation
- Configuration
- Usage Examples
- Delivery Method Setup
- Troubleshooting
- Development (for contributors)

---

### Epic 6: Polish & Optimization (Post-MVP)

#### Story 6.1: Event Categorization
**As a** user
**I want to** events categorized by type
**So that** I can filter by interest

**Acceptance Criteria:**
- [ ] Define category taxonomy (Arts, Sports, Education, Outdoor, etc.)
- [ ] Build categorization logic (keyword matching in title/description)
- [ ] Store categories in `event_types` field (array)
- [ ] Add `--category` filter to command
- [ ] Display categories in delivery outputs
- [ ] Test accuracy with sample events

**Future:** Use AI categorization (requires API cost)

---

#### Story 6.2: Kid-Friendly Scoring
**As a** user
**I want to** events ranked by kid-appropriateness
**So that** I prioritize the best options

**Acceptance Criteria:**
- [ ] Define scoring algorithm (keyword presence, age range match, venue type)
- [ ] Calculate score (0-100) for each event
- [ ] Store in `kid_friendly_score` field
- [ ] Sort results by score (highest first)
- [ ] Add `--min-score` filter to command
- [ ] Test accuracy with manual review

**Scoring Factors:**
- Age range matches target (0-12 years): +30
- Kid-friendly keywords in description: +20
- Free event: +15
- Known kid-friendly venue (library, park): +15
- Outdoor activity: +10
- Educational content: +10

---

#### Story 6.3: Natural Language Summarization
**As a** user
**I want to** a brief summary of each event
**So that** I can quickly scan options

**Acceptance Criteria:**
- [ ] Generate 1-sentence summary per event (extract or create)
- [ ] Highlight key details (age range, cost, unique selling point)
- [ ] Include summary in delivery outputs
- [ ] Keep under 100 characters for readability

**Future:** Use AI summarization (requires API cost)

---

## Technical Specifications

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              Claude Code Slash Command                   │
│                   /get-events [args]                     │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                 EventOrchestrator                        │
│  - Parse command args                                    │
│  - Select sources                                        │
│  - Apply filters (date range, categories)                │
│  - Route to delivery                                     │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┬───────────────┐
       │                 │                 │               │
┌──────▼──────┐   ┌──────▼──────┐   ┌─────▼──────┐  ┌─────▼──────┐
│ KNCOScraper │   │LibraryScraper│  │CountyScraper│  │  (Future)  │
│  (Trumba)   │   │  (LibCal)   │   │  (iCal?)    │  │  Scrapers  │
└──────┬──────┘   └──────┬──────┘   └─────┬──────┘  └─────┬──────┘
       │                 │                 │               │
       └─────────────────┴─────────────────┴───────────────┘
                         │
                  ┌──────▼──────────┐
                  │  CacheManager   │
                  │  Check DB TTL   │
                  └──────┬──────────┘
                         │
       ┌─────────────────┴─────────────────┐
       │                                   │
    Cache HIT                          Cache MISS
       │                                   │
       ▼                                   ▼
┌──────────────┐                  ┌────────────────┐
│ Return Cached│                  │  Scrape Fresh  │
│    Events    │                  │  + Normalize   │
└──────┬───────┘                  └────────┬───────┘
       │                                   │
       └───────────────┬───────────────────┘
                       │
              ┌────────▼─────────┐
              │  Deduplicator    │
              │ Cross-source     │
              │  matching        │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │   Data Quality   │
              │   Validation     │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Supabase Storage │
              │  Upsert Events   │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Delivery Router  │
              └────────┬─────────┘
                       │
       ┌───────────────┼───────────────┬─────────────┐
       │               │               │             │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌───▼────┐
│   Email     │ │  Telegram   │ │   GCal     │ │Terminal│
│  Delivery   │ │  Delivery   │ │  Delivery  │ │Display │
└─────────────┘ └─────────────┘ └────────────┘ └────────┘
```

### Technology Stack Details

**Core Dependencies:**
```
Python 3.11+
requests==2.31.0          # HTTP client
beautifulsoup4==4.12.0    # HTML parsing
feedparser==6.0.10        # RSS/Atom parsing
psycopg2-binary==2.9.9    # PostgreSQL driver
python-dotenv==1.0.0      # Environment config
```

**Delivery Dependencies:**
```
python-telegram-bot==20.7  # Telegram integration
google-api-python-client==2.100.0  # Google Calendar
google-auth==2.23.0        # Google OAuth
```

**Optional/Future:**
```
icalendar==5.0.0          # iCal parsing (if county uses this)
python-Levenshtein==0.21.1  # Fuzzy deduplication
PyPDF2==3.0.0             # PDF parsing (AdventureMama)
```

---

## API Contracts & Interfaces

### BaseScraper Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

class BaseScraper(ABC):
    """Abstract base class for all event scrapers"""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.source_name = self._get_source_name()

    @abstractmethod
    def _get_source_name(self) -> str:
        """Return unique source identifier (e.g., 'knco', 'library')"""
        pass

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape events from source and return normalized dictionaries.

        Returns:
            List of event dictionaries with schema:
            {
                'title': str (required),
                'description': str (required),
                'event_date': datetime (required),
                'venue': Optional[str],
                'city_area': Optional[str],
                'age_range': Optional[str],
                'price': Optional[str],
                'is_free': Optional[bool],
                'source_name': str (auto-set),
                'source_url': str (required),
                'source_event_id': str (required for dedup),
            }

        Raises:
            ScraperException: If source unreachable or parse fails
        """
        pass

    def _make_request(self, url: str, timeout: int = 30) -> str:
        """Helper: HTTP GET with error handling"""
        # Implementation in base class
        pass
```

### Normalizer Interface

```python
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NormalizedEvent:
    """Standardized event schema"""
    title: str
    description: str
    event_date: datetime
    source_name: str
    source_url: str
    source_event_id: str
    content_hash: str
    venue: Optional[str] = None
    city_area: Optional[str] = None
    age_range: Optional[str] = None
    price: Optional[str] = None
    is_free: Optional[bool] = None
    quality_score: int = 0

class Normalizer:
    def normalize(self, raw_events: List[Dict], source_name: str) -> List[NormalizedEvent]:
        """
        Transform raw scraper output to standardized schema.

        Args:
            raw_events: List of dicts from scraper
            source_name: Source identifier

        Returns:
            List of NormalizedEvent objects

        Raises:
            ValidationException: If required fields missing
        """
        pass

    def _generate_content_hash(self, event: Dict) -> str:
        """Generate MD5 hash for deduplication"""
        pass

    def _calculate_quality_score(self, event: NormalizedEvent) -> int:
        """Calculate quality score (0-100)"""
        pass
```

### Delivery Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class DeliveryResult:
    """Result of delivery attempt"""
    success: bool
    message: str
    events_delivered: int
    metadata: Dict = None

class BaseDelivery(ABC):
    """Abstract base class for delivery methods"""

    @abstractmethod
    def deliver(self, events: List[Dict], **options) -> DeliveryResult:
        """
        Send events via this delivery method.

        Args:
            events: List of normalized event dicts
            **options: Method-specific options

        Returns:
            DeliveryResult with success status

        Raises:
            DeliveryException: If delivery fails unrecoverably
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Check if delivery method is properly configured.

        Returns:
            True if ready to deliver, False otherwise
        """
        pass

    @abstractmethod
    def format_events(self, events: List[Dict]) -> str:
        """
        Format events for this delivery method.

        Args:
            events: List of event dicts

        Returns:
            Formatted output (HTML, Markdown, plain text, etc.)
        """
        pass
```

---

## Data Models

### Database Schema

**Events Table** (existing):
```sql
CREATE TABLE events (
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

-- Indexes
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_source ON events(source_name);
CREATE INDEX idx_events_content_hash ON events(content_hash);
CREATE UNIQUE INDEX idx_source_event_unique ON events(source_name, source_event_id);
CREATE INDEX idx_events_scraped_at ON events(scraped_at);
```

### Python Data Models

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class EventSource:
    """Configuration for an event source"""
    name: str
    scraper_class: type
    priority: int  # For deduplication (1=highest)
    enabled: bool = True
    config: dict = None

@dataclass
class CacheMetadata:
    """Cache state for a source"""
    source_name: str
    last_scraped: datetime
    event_count: int
    is_stale: bool
    ttl_hours: int

@dataclass
class ScrapingResult:
    """Result of scraping operation"""
    source_name: str
    success: bool
    events_found: int
    errors: List[str]
    duration_seconds: float
    cache_hit: bool
```

---

## Acceptance Criteria

### Epic-Level Acceptance

**Epic 1: Source Research**
- [ ] All 3 Tier 1 sources evaluated with documented metrics
- [ ] Top 3 sources selected for MVP with justification
- [ ] Sample datasets stored in `data/samples/`
- [ ] Source evaluation report in `docs/source-evaluation.md`

**Epic 2: Core Scraping Engine**
- [ ] KNCO scraper returns 200+ events with metadata
- [ ] Events stored in Supabase without duplicates (same run)
- [ ] Cache layer prevents re-scraping within 6 hours
- [ ] Command-line script runs end-to-end successfully
- [ ] Unit tests pass with >80% coverage

**Epic 3: Multi-Source Integration**
- [ ] 3 scrapers operational (KNCO, Library, County/other)
- [ ] Deduplication reduces combined results by <5% (proves cross-source matches exist)
- [ ] Parallel scraping completes in <30 seconds total
- [ ] Graceful failure: 1 source down doesn't break entire flow
- [ ] Integration tests pass

**Epic 4: Delivery Layer**
- [ ] At least 2 delivery methods functional (email + 1 other)
- [ ] Email includes HTML formatting and all event details
- [ ] Delivery errors handled gracefully with user feedback
- [ ] Configuration validation prevents runtime failures
- [ ] Manual testing confirms receipt

**Epic 5: Slash Command**
- [ ] `/get-events` command registered in Claude Code
- [ ] End-to-end flow completes in <2 minutes
- [ ] User can select delivery method conversationally
- [ ] Errors display helpful messages (not stack traces)
- [ ] Documentation complete in README

**Epic 6: Polish** (Post-MVP)
- [ ] Categorization adds value (user validation)
- [ ] Kid-friendly scoring correlates with manual assessment
- [ ] Performance optimizations reduce execution time by 20%+

---

## Dependencies & Constraints

### External Dependencies

**Required:**
- Supabase Postgres database (existing)
- Python 3.11+ runtime
- Internet connection (for scraping)

**Optional (for delivery):**
- Gmail account (for email delivery)
- Telegram account + bot token (for Telegram)
- Google account + OAuth credentials (for Calendar)

### Technical Constraints

- **Rate Limiting:** Respect source `robots.txt`, add delays between requests
- **Scraping Ethics:** Only scrape publicly accessible calendars, identify with polite User-Agent
- **Data Retention:** Keep events in DB indefinitely (for historical analysis), but only show future events by default
- **Performance:** Scraping all sources must complete <2 minutes
- **Reliability:** Gracefully handle source outages (show partial results)

### Development Constraints

- **Environment:** Local Windows machine (no server deployment for MVP)
- **Budget:** Zero additional costs (no paid APIs, no cloud hosting)
- **Timeline:** No hard deadlines, exploration-driven
- **Team:** Solo development (self-documenting code required)

---

## Release Plan

### Version 0.1 - Source Research (Week 1-2)
**Goal:** Identify best sources for MVP

**Deliverables:**
- Source evaluation report
- Sample datasets
- Scraper proofs-of-concept

**Success Criteria:**
- Top 3 sources selected
- Confidence in scraping feasibility

---

### Version 0.2 - Single-Source Prototype (Week 3-4)
**Goal:** End-to-end working pipeline with 1 source

**Deliverables:**
- KNCO scraper (production-ready)
- Normalizer + storage layer
- Cache implementation
- CLI script

**Success Criteria:**
- `python -m src.orchestrator --source knco` works
- 200+ events in Supabase
- Cache hit on second run

---

### Version 0.3 - Multi-Source Integration (Week 5-6)
**Goal:** 3 sources + deduplication

**Deliverables:**
- Library + County scrapers
- Deduplication logic
- Parallel scraping
- Quality validation

**Success Criteria:**
- Combined results from 3 sources
- <5% duplicates detected
- Executes in <30 seconds

---

### Version 0.4 - Delivery Layer (Week 7-8)
**Goal:** 2+ delivery methods working

**Deliverables:**
- Email delivery (HTML formatting)
- Telegram OR Google Calendar delivery
- Delivery router
- Configuration guides

**Success Criteria:**
- Receive events in inbox
- Receive via secondary method
- Error handling works

---

### Version 1.0 - MVP Complete (Week 9-10)
**Goal:** Slash command end-to-end

**Deliverables:**
- `/get-events` command
- Conversational delivery selection
- Error handling
- Documentation (README)

**Success Criteria:**
- Complete flow in <2 minutes
- User satisfaction: "This works!"
- Documented for future maintenance

---

### Version 1.1+ - Enhancements (Post-MVP)
**Goal:** Polish and intelligence

**Potential Features:**
- Event categorization
- Kid-friendly scoring
- Additional sources (AdventureMama PDF)
- Performance optimizations
- Advanced filtering

**Prioritization:** Based on usage patterns and feedback

---

## Appendices

### A. Sample Data Structures

**Raw Scraper Output (KNCO):**
```python
{
    'title': 'Story Time at Nevada City Library',
    'description': '<b>City/Area</b>:&amp;nbsp;Nevada City<br/><b>Age</b>:&nbsp;3-5 years<br/>Join us for stories and songs!',
    'event_date': '2025-10-15T10:00:00-07:00',
    'source_url': 'http://uid.trumba.com/event/177609910',
    'guid': 'http://uid.trumba.com/event/177609910'
}
```

**Normalized Event:**
```python
{
    'title': 'Story Time at Nevada City Library',
    'description': 'Join us for stories and songs!',
    'event_date': datetime(2025, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
    'venue': None,
    'city_area': 'Nevada City',
    'age_range': '3-5 years',
    'price': None,
    'is_free': True,
    'source_name': 'knco',
    'source_url': 'http://uid.trumba.com/event/177609910',
    'source_event_id': '177609910',
    'content_hash': 'a3f2c8b9e1d4...',
    'quality_score': 75
}
```

---

### B. Environment Variables Reference

**Required:**
```bash
# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Cache
CACHE_TTL_HOURS=6
```

**Optional (Email Delivery):**
```bash
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
EMAIL_RECIPIENT=your-email@gmail.com
```

**Optional (Telegram Delivery):**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

**Optional (Google Calendar):**
```bash
GCAL_CREDENTIALS_FILE=credentials.json
GCAL_TOKEN_FILE=token.json
GCAL_CALENDAR_ID=primary
```

---

### C. Error Codes

| Code | Error | User Message | Technical Action |
|------|-------|--------------|------------------|
| E001 | Source Unreachable | "Couldn't connect to [source]. Using cached data." | Log timeout, use cache if available |
| E002 | Parse Failure | "Found events but couldn't read them from [source]." | Log parse error, skip source |
| E003 | Database Error | "Couldn't save events. Please check database connection." | Log SQL error, retry once |
| E004 | Invalid Config | "Missing configuration for [feature]. Check .env file." | Log missing var, halt execution |
| E005 | Delivery Failure | "[Method] delivery failed: [reason]. Try another method?" | Log delivery error, offer alternatives |

---

### D. Testing Strategy

**Unit Tests:**
- Scraper parsing logic (with fixtures)
- Normalizer validation rules
- Deduplicator matching algorithm
- Quality scoring calculations

**Integration Tests:**
- Full scraping pipeline (mock HTTP requests)
- Database upsert operations
- Cache hit/miss scenarios
- Delivery method execution

**Manual Testing:**
- End-to-end command execution
- Real source scraping (verify data accuracy)
- Delivery receipt (check email inbox, Telegram, etc.)
- Error handling (simulate network failures)

**Test Data:**
- Store sample RSS/HTML in `data/samples/`
- Create fixtures for edge cases (missing fields, malformed dates)
- Mock responses for external APIs

---

### E. Future Enhancements (Out of Scope for V1)

**Advanced AI Features** (requires paid API):
- Natural language event summaries
- Smart categorization with ML
- Personalized recommendations
- Automatic kid-friendly scoring with context understanding

**Additional Sources:**
- AdventureMama (PDF extraction)
- Facebook Events API (if access granted)
- Eventbrite (Nevada County search)
- Meetup.com (family-oriented groups)

**User Features:**
- Multi-user support (different preferences)
- Event favorites/bookmarks
- Recurring event detection
- Calendar sync (bidirectional)

**Analytics:**
- Most popular events (track views/clicks)
- Source quality trends over time
- User engagement metrics

**Deployment:**
- Docker containerization
- Cloud hosting (AWS Lambda, Render, etc.)
- Scheduled background jobs (cron in cloud)
- Web interface (FastAPI + React)

---

**Document Status:** ✅ Ready for Development
**Next Step:** Begin Epic 1 - Source Research & Evaluation
**Approval:** Awaiting project owner sign-off

---

## Sign-Off

**Product Owner:** ________________  Date: _______
**Technical Lead:** ________________  Date: _______
**Business Analyst:** Mary (Agent)  Date: 2025-10-07

---

*End of PRD*
