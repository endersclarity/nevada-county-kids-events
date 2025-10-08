# Nevada County Kids Events Agent - Project Brief

**Project Name:** Nevada County Kids Events Agent
**Project Type:** On-Demand Event Aggregation & Delivery System
**Status:** 🟡 Planning
**Created:** 2025-10-07
**Last Updated:** 2025-10-07

---

## Executive Summary

Build a Claude Code slash command agent that scrapes, synthesizes, and delivers kid-friendly events in Nevada County, CA on demand. The user invokes a command, the agent gathers current events from multiple sources, processes/enriches the data, and delivers via user-selected method (email, Telegram, Google Calendar, etc.).

**Core Value Proposition:**
Replace manual event hunting across 10+ fragmented sources with a single conversational command that delivers curated, kid-appropriate events in your preferred format.

---

## Problem Statement

### Current Pain Points
- **Fragmented Sources:** Events scattered across county websites, library calendars, radio station feeds, community boards
- **No Kid-Focus Filter:** Most calendars mix adult/senior events with kid activities
- **Manual Effort Required:** Must check multiple sites weekly, copy/paste into personal calendar
- **Missed Opportunities:** Events fall through the cracks due to obscure posting locations
- **No Quality Signal:** Can't distinguish "worth attending" from "low-value" events

### Why Existing Solutions Fall Short
- **n8n Attempt Failed:** Code propagation issues, opaque debugging, webhook limitations (see BUILD-FROM-SCRATCH.md)
- **Manual Aggregation:** Time-consuming, error-prone, unsustainable
- **Generic Event Apps:** Not Nevada County-specific, lack kid-friendly filtering
- **Google Alerts:** Miss events posted to calendars vs news sites

---

## Goals & Success Criteria

### Primary Goal
**Functional slash command** that delivers curated kid events on demand with flexible delivery options.

### MVP Success Criteria
- ✅ User runs `/get-events` (or similar command)
- ✅ Agent scrapes 3+ prioritized sources
- ✅ Returns cleaned, deduplicated event list
- ✅ Offers delivery method selection (email/telegram/calendar/etc)
- ✅ Successfully delivers via chosen method
- ✅ Entire flow completes in <2 minutes

### Secondary Goals
- **Learning Objective:** Understand Python scraping, data synthesis, multi-modal delivery
- **Portability:** Architecture should inform eventual n8n rebuild (if desired)
- **Extensibility:** Easy to add new sources and delivery methods

### Non-Goals (Out of Scope for MVP)
- ❌ Public-facing interface (just personal use)
- ❌ Real-time notifications (on-demand only)
- ❌ Advanced AI categorization (future enhancement)
- ❌ Historical event tracking/analytics
- ❌ User accounts/multi-user support

---

## User Personas

### Primary: Project Owner (You)
- **Role:** Parent in Nevada County seeking kid activities
- **Tech Savvy:** High - comfortable with CLI, Python, databases
- **Frequency:** Weekly event discovery (Fridays for weekend planning)
- **Preferences:**
  - Flexible delivery (sometimes email, sometimes calendar)
  - Information density over aesthetics
  - Control and transparency over "magic"
- **Pain Points:** Wastes 30+ min/week manually checking sites

---

## Technical Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│  User Interface Layer                               │
│  - Claude Code Slash Command                        │
│  - Natural language command parsing                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│  Orchestration Layer                                │
│  - Source selection logic                           │
│  - Parallel scraping coordinator                    │
│  - Delivery method router                           │
└─────────────────┬───────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
┌─────▼─────┐ ┌──▼──────┐ ┌──▼──────┐
│ Scraper 1 │ │Scraper 2│ │Scraper 3│
│  (KNCO)   │ │(Library)│ │ (County)│
└─────┬─────┘ └──┬──────┘ └──┬──────┘
      │          │           │
      └──────────┼───────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│  Data Processing Layer                              │
│  - Normalization (schema standardization)           │
│  - Deduplication (cross-source matching)            │
│  - Enrichment (categorization, scoring - future)    │
│  - Caching (optional staleness-based refresh)       │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│  Storage Layer                                      │
│  - Supabase Postgres (events table)                 │
│  - Cache metadata (last_scraped, source_health)     │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│  Delivery Layer                                     │
│  - Email formatter & sender                         │
│  - Telegram bot integration                         │
│  - Google Calendar API                              │
│  - (Extensible interface for future methods)        │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

**Language:** Python 3.11+
- **Why:** Rich scraping ecosystem, beginner-friendly, easy n8n translation

**Scraping:**
- `requests` - HTTP client
- `BeautifulSoup4` - HTML parsing
- `feedparser` - RSS/Atom parsing
- `icalendar` - iCal parsing (if needed)

**Database:**
- Supabase Postgres (existing setup from n8n attempt)
- `psycopg2` - Postgres driver

**Delivery:**
- `smtplib` - Email (built-in)
- `python-telegram-bot` - Telegram integration
- `google-api-python-client` - Google Calendar
- (Others as needed)

**Development:**
- Claude Code - Primary development environment
- Git - Version control (existing repo)
- Virtual environment (`venv`) - Dependency isolation

**Deployment:**
- Local execution (Windows machine)
- Future: Docker container (optional portability)

### Data Schema

**Events Table** (already exists in Supabase):
```sql
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,

  -- Event basics
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

  -- Event metadata
  event_types TEXT[],
  age_range TEXT,
  price TEXT,
  is_free BOOLEAN,

  -- Future: AI enrichment
  kid_friendly_score INTEGER,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Caching Strategy** (TBD - options outlined):
- **Option A:** Always scrape fresh (simple, slow)
- **Option B:** Cache with TTL (e.g., 6 hours) - check `scraped_at` timestamp
- **Option C:** Background job + query cache (original n8n approach)

**Recommendation:** Start with Option B (cache with 6-hour TTL) - balances freshness and speed.

---

## Source Research & Prioritization

### Phase 1: Source Evaluation (Epic 1) ✅ COMPLETE

**Methodology:**
1. Build proof-of-concept scraper for each source
2. Extract sample dataset (1 week of events)
3. Analyze metrics:
   - **Volume:** Events per week
   - **Kid Relevance:** % appropriate for children
   - **Data Quality:** Completeness of metadata (date, location, description)
   - **Scraping Difficulty:** Technical complexity (1-5 scale)
   - **Update Frequency:** How often new events appear
4. Score sources using weighted matrix
5. Prioritize top 3 for MVP

**Evaluation Completed:** 2025-10-07 (Stories E1.1-E1.4)

### Source Evaluation Results

**Sources Evaluated:**

| Source | Volume | Kid % | Quality | Difficulty | Score | Rank |
|--------|--------|-------|---------|------------|-------|------|
| **KNCO RSS** | 200/mo | 50% | 68% | 2/5 | 26.5 | #1 |
| **Library Calendar** | 35/mo | 82% | 100% | 4/5 | 26.0 | #2 |
| **County Calendar** | 75/mo | 44% | 60% | 3/5 | 18.0 | #3 |

**Full evaluation details:** [docs/source-evaluation.md](./docs/source-evaluation.md)

### MVP Source Selection ✅ FINAL

**✅ TIER 1 - Included in MVP:**

1. **KNCO RSS Feed** (Priority: HIGH)
   - **Format:** RSS (Trumba)
   - **Volume:** 200 events/month
   - **Kid-relevance:** 50%
   - **Scraping Difficulty:** 2/5 (Low)
   - **Implementation:** Use existing `evaluate_knco.py` as foundation
   - **Rationale:** Easiest to implement, highest volume, stable format

2. **Nevada County Library** (Priority: HIGH)
   - **Format:** LibCal HTML (JavaScript-rendered)
   - **Volume:** 35 events/month
   - **Kid-relevance:** 82%
   - **Scraping Difficulty:** 4/5 (High)
   - **Implementation:** Browser automation or LibCal API
   - **Rationale:** Highest kid-relevance, perfect metadata quality

**Combined MVP Coverage:**
- **Total Volume:** ~235 events/month
- **Avg Kid-relevance:** 66% (weighted by volume)
- **Complementary Strengths:** KNCO=volume, Library=quality

**⏸️ POST-MVP - Deferred:**

3. **Nevada County Government Calendar** (Priority: LOW)
   - **Format:** iCal export available
   - **Volume:** 75 events/month
   - **Kid-relevance:** 44%
   - **Scraping Difficulty:** 3/5 (Medium)
   - **Why Deferred:** Significant overlap with Library calendar, low kid-relevance
   - **Reconsider When:** MVP needs more volume or users request specific government events

**Other Sources Not Evaluated:**

**Tier 2: HTML Scraping (Future Consideration)**
| Source | Format | Expected Volume | Notes |
|--------|--------|-----------------|-------|
| Nevada City Chamber | HTML | Unknown | May require JavaScript rendering |
| Grass Valley Chamber | HTML | Unknown | Static HTML (easier) |
| Local Facebook Groups | Social Media | High | API restrictions, ethical concerns |
| Tahoe Donner | HTML | Unknown | Seasonal, specific community |

**Tier 3: PDF/Document Extraction (Future Consideration)**
| Source | Format | Expected Volume | Notes |
|--------|--------|-----------------|-------|
| AdventureMama | PDF | Unknown | Requires PDF download + text extraction (PyPDF2/pdfplumber) |

**Tier 4: Low Priority / Blocked**
- Individual venue websites (complexity scales poorly)
- Email newsletters (access issues)

---

## Feature Roadmap

### Phase 1: Foundation (Epic 1-2)
**Goal:** Working prototype with single source

**Features:**
- ✅ Source evaluation framework
- ✅ KNCO RSS scraper (refined from n8n version)
- ✅ Data normalization pipeline
- ✅ Supabase storage integration
- ✅ Basic deduplication (by source_event_id)
- ✅ Manual Python script execution

**Estimated Effort:** 2-3 sessions

---

### Phase 2: Multi-Source & Intelligence (Epic 3-4)
**Goal:** 3 sources with smart deduplication

**Features:**
- ✅ Library scraper
- ✅ County calendar scraper
- ✅ Cross-source deduplication (content_hash matching)
- ✅ Data quality validation (required fields check)
- ✅ Basic categorization (extract from descriptions)
- ✅ Caching layer (6-hour TTL)

**Estimated Effort:** 3-4 sessions

---

### Phase 3: Delivery Layer (Epic 5)
**Goal:** Multi-modal output

**Features:**
- ✅ Delivery interface abstraction
- ✅ Email formatter (HTML template)
- ✅ Email sender (SMTP)
- ✅ Telegram integration
- ✅ Google Calendar integration
- ✅ Delivery method selection logic

**Estimated Effort:** 2-3 sessions

---

### Phase 4: Command Interface (Epic 6)
**Goal:** Claude Code slash command

**Features:**
- ✅ Slash command registration
- ✅ Command orchestration logic
- ✅ Conversational delivery selection
- ✅ Error handling & user feedback
- ✅ Usage documentation

**Estimated Effort:** 1-2 sessions

---

### Phase 5: Enrichment & Polish (Epic 7 - Future)
**Goal:** Enhanced intelligence (post-MVP)

**Features:**
- ⏸️ Kid-friendly scoring algorithm
- ⏸️ Smart categorization (event types)
- ⏸️ Age range inference
- ⏸️ Price extraction normalization
- ⏸️ Natural language event summaries
- ⏸️ Relevance ranking

**Estimated Effort:** TBD (exploration phase)

---

## Project Structure

```
nevada-county-kids-events/
├── README.md                 # Project overview, setup instructions
├── PROJECT-BRIEF.md          # This document
├── PRD.md                    # Detailed product requirements (next step)
├── BUILD-FROM-SCRATCH.md     # Historical n8n attempt log
│
├── src/                      # Python source code
│   ├── __init__.py
│   ├── scrapers/             # Source-specific scrapers
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract scraper interface
│   │   ├── knco.py           # KNCO RSS scraper
│   │   ├── library.py        # Library calendar scraper
│   │   └── county.py         # County calendar scraper
│   │
│   ├── processors/           # Data processing
│   │   ├── __init__.py
│   │   ├── normalizer.py     # Schema standardization
│   │   ├── deduplicator.py   # Cross-source matching
│   │   └── enricher.py       # Future: categorization, scoring
│   │
│   ├── storage/              # Database layer
│   │   ├── __init__.py
│   │   ├── supabase.py       # Supabase client wrapper
│   │   └── cache.py          # Cache management
│   │
│   ├── delivery/             # Output methods
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract delivery interface
│   │   ├── email.py          # Email delivery
│   │   ├── telegram.py       # Telegram delivery
│   │   └── gcal.py           # Google Calendar delivery
│   │
│   ├── orchestrator.py       # Main coordination logic
│   └── config.py             # Configuration management
│
├── .claude/                  # Claude Code integration
│   └── commands/
│       └── get-events.md     # Slash command definition
│
├── tests/                    # Unit tests (future)
│   └── __init__.py
│
├── data/                     # Sample/test data
│   └── samples/
│       ├── knco_sample.xml
│       └── library_sample.html
│
├── docs/                     # Additional documentation
│   ├── source-evaluation.md  # Source research findings
│   └── architecture.md       # Technical deep-dive
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── LICENSE
```

---

## Risks & Mitigations

### Technical Risks

**Risk 1: Website Structure Changes**
- **Impact:** HIGH - Scrapers break when sources redesign
- **Likelihood:** MEDIUM - Happens 1-2x/year per source
- **Mitigation:**
  - Build resilient parsers with fallback logic
  - Monitor scraping success rate
  - Version control old parsing logic for rollback
  - Document HTML structure assumptions

**Risk 2: Rate Limiting / IP Blocking**
- **Impact:** MEDIUM - Can't scrape if blocked
- **Likelihood:** LOW - Small-scale scraping unlikely to trigger
- **Mitigation:**
  - Respect `robots.txt`
  - Add delays between requests (1-2 sec)
  - Cache aggressively to minimize requests
  - Use polite User-Agent header

**Risk 3: Incomplete Metadata**
- **Impact:** MEDIUM - Events lack key details (age range, price)
- **Likelihood:** HIGH - Sources vary in data quality
- **Mitigation:**
  - Accept incomplete data for MVP
  - Flag low-quality events in output
  - Manual enrichment for critical events (future)
  - Prioritize high-quality sources

**Risk 4: Delivery Service Dependencies**
- **Impact:** MEDIUM - Can't deliver if service down (Gmail, Telegram API)
- **Likelihood:** LOW - Major services are reliable
- **Mitigation:**
  - Fallback delivery methods
  - Graceful degradation (show in terminal if delivery fails)
  - Queue retry logic (future)

### Project Risks

**Risk 5: Scope Creep**
- **Impact:** HIGH - Never finish if keep adding features
- **Likelihood:** HIGH - Natural tendency to over-engineer
- **Mitigation:**
  - Strict MVP definition (this document)
  - Defer Phase 5 features until MVP works
  - "Working first, perfect later" principle

**Risk 6: Loss of Motivation**
- **Impact:** HIGH - Abandoned projects provide no value
- **Likelihood:** MEDIUM - Happens when stuck or bored
- **Mitigation:**
  - Incremental milestones with visible progress
  - "Fun factor" check at each phase
  - Flexibility to pivot approach if frustrating
  - No timeline pressure (exploration vs deadline)

---

## Open Questions

### Architecture Decisions
1. **Caching strategy:** Fresh scrape vs TTL cache vs background job?
   - **Recommendation:** Start with 6-hour TTL cache (Option B)
   - **Rationale:** Balances speed and freshness, simple to implement

2. **Error handling philosophy:** Fail fast vs graceful degradation?
   - **Recommendation:** Graceful degradation with logging
   - **Rationale:** Better UX - show partial results if 1 source fails

3. **Parallel vs sequential scraping:** Run scrapers concurrently?
   - **Recommendation:** Parallel with timeout (30 sec/source)
   - **Rationale:** Faster overall, acceptable if 1 source slow

### Feature Scope
4. **How much synthesis?** Deduplication? Categorization? Summarization?
   - **Decision:** "Yes to all, but working first" - defer to Phase 5

5. **Default delivery method:** If user doesn't specify, what happens?
   - **Options:** Ask user, default to terminal output, remember last choice
   - **Recommendation:** Ask user interactively (conversational UX)

6. **Event date range:** Show all future events or limit to next X days?
   - **Recommendation:** Configurable, default to next 14 days
   - **Rationale:** Weekend planner typically looks 1-2 weeks ahead

---

## Success Metrics (Post-MVP)

### Usage Metrics
- **Command invocations per week** (target: 1-2, Friday planning + ad-hoc)
- **Delivery method distribution** (which methods get used most?)
- **Average events returned per query** (too many = noise, too few = incomplete)

### Data Quality Metrics
- **Scraping success rate** (% of sources returning data)
- **Deduplication accuracy** (manual audit of cross-source matches)
- **Metadata completeness** (% events with age_range, venue, price)

### Outcome Metrics (Qualitative)
- **Time saved** (30 min/week manual → <5 min automated?)
- **Events discovered** (finding events missed by manual search?)
- **Satisfaction** ("Is this more fun than frustrating?")

---

## Timeline & Milestones

**No hard deadlines - exploration-driven development**

### Milestone 1: Source Research Complete
- All Tier 1 sources evaluated
- Top 3 prioritized for MVP
- Sample datasets extracted
- **Exit Criteria:** Decision matrix completed, next sources chosen

### Milestone 2: Single-Source Working Prototype
- KNCO scraper functional
- Data stored in Supabase
- Manual Python script execution
- **Exit Criteria:** `python main.py` returns 200 events in DB

### Milestone 3: Multi-Source Integration
- 3 scrapers operational
- Deduplication working
- Cache layer implemented
- **Exit Criteria:** Combined results show <5% duplicates

### Milestone 4: Delivery Layer Functional
- At least 2 delivery methods working (email + 1 other)
- User can select method
- **Exit Criteria:** Receive events in inbox via script

### Milestone 5: MVP Complete
- Claude Code slash command working
- End-to-end flow functional
- Documentation complete
- **Exit Criteria:** `/get-events` → delivered results in <2 min

### Milestone 6: Polish & Enhancements (Post-MVP)
- Categorization/enrichment added
- Additional sources integrated
- Performance optimizations
- **Exit Criteria:** TBD based on usage patterns

---

## Appendices

### A. Related Documents
- [BUILD-FROM-SCRATCH.md](./BUILD-FROM-SCRATCH.md) - n8n implementation attempt history
- PRD.md (to be created) - Detailed product requirements
- Epics/Stories breakdown (to be created) - Scrum planning artifacts

### B. External References
- [Nevada County Library Events](https://nevadacounty.librarymarket.com/events) - Primary source
- [KNCO Trumba Feed](http://uid.trumba.com/...) - RSS source
- [Supabase Documentation](https://supabase.com/docs) - Database platform
- [Claude Code Docs](https://docs.claude.com/claude-code) - Development environment

### C. Glossary
- **Synthesis:** Combined process of deduplication, normalization, categorization, and enrichment
- **Source Health:** Metric indicating scraping success rate and data quality per source
- **TTL (Time To Live):** Cache expiration period before data considered stale
- **Content Hash:** Fingerprint of event details used for deduplication across sources
- **Kid-Friendly Score:** Future metric (0-100) indicating event appropriateness for children

---

**Document Status:** ✅ Ready for PRD conversion
**Next Step:** Create detailed PRD with user stories, acceptance criteria, and technical specifications
**Owner:** Project Owner (You) + Mary (Business Analyst Agent)
