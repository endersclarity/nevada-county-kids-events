# Building Nevada County Kids Events Bot - From Scratch

**Project:** Nevada County Kids Events Aggregator
**Approach:** Incremental development, node by node
**Started:** 2025-10-06
**Status:** 🔴 **INCOMPLETE - Technical Blockers**

---

## Session 1 Summary (2025-10-06)

### What We Built
- Created workflow: `Nevada County Events Scraper` (ID: `EAdNPKCQrLvPbfD0`)
- 5 nodes total:
  1. Manual Trigger
  2. Schedule Trigger (daily 6am)
  3. Fetch KNCO RSS (HTTP Request)
  4. Parse RSS Events (Code node with regex XML parsing)
  5. Store Events in DB (PostgreSQL with UPSERT)

### What Works
✅ **RSS Fetching** - Successfully fetches 200 events from KNCO Trumba feed
✅ **Parser** - Extracts events from XML using regex
✅ **Database Schema** - Created `events` table in Supabase with proper indexes
✅ **Schedule Trigger** - Set to run daily at 6am automatically

### What Doesn't Work
❌ **Data Extraction** - Parser runs but extracts NO metadata:
  - `source_event_id`: NULL (guid extraction failing)
  - `age_range`: NULL (HTML entity parsing failing)
  - `city_area`: NULL (metadata extraction failing)
  - `venue`: NULL
  - `price`: NULL
  - Result: 200 events with only title/description/date populated

❌ **UPSERT Logic** - Switched to manual SQL with parameterized queries but untested due to extraction failures

❌ **Webhook Testing** - Could not get production webhook to register for automated testing

### Root Cause Analysis

**Problem:** Parser code updates didn't propagate to actual execution
- Updated parser 3 times with fixes
- Executions still ran old parser code
- Result: No metadata extracted despite code fixes

**Attempted Fixes:**
1. Fixed `source_event_id` extraction regex from `/\/(\\d+)$/` to `/event\/(\\d+)/`
2. Added HTML entity handling for `&amp;nbsp;` vs `&nbsp;`
3. Switched from buggy `upsert` operation to `executeQuery` with manual SQL
4. None took effect in actual execution

**Likely Issue:** n8n caching old node code or execution using stale workflow version

---

## Database Schema (IMPLEMENTED)

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
  source_name TEXT NOT NULL DEFAULT 'knco',
  source_url TEXT,
  source_event_id TEXT,  -- Added for proper deduplication
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Deduplication
  content_hash TEXT,  -- Kept for cross-source dedup

  -- Event metadata
  event_types TEXT[],
  age_range TEXT,
  price TEXT,
  is_free BOOLEAN,

  -- AI enrichment (future)
  kid_friendly_score INTEGER,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_source ON events(source_name);
CREATE INDEX idx_events_content_hash ON events(content_hash);
CREATE UNIQUE INDEX idx_source_event_unique ON events(source_name, source_event_id);
```

---

## Key Learnings

### ✅ What Worked Well
1. **Incremental approach** - Building node by node made debugging easier
2. **Advanced elicitation analysis** - Running all 5 analysis methods revealed the root cause (design assumption violated: single-run vs daily operation)
3. **Database design** - Using `source_event_id` from RSS `<guid>` for proper UPSERT was the right call
4. **Documentation** - BUILD-FROM-SCRATCH.md format effective for tracking progress

### ❌ What Didn't Work
1. **n8n MCP workflow updates** - Node parameter changes didn't propagate to executions
2. **Webhook registration** - Production webhooks require manual UI toggle, impossible to automate
3. **Testing automation** - Can't programmatically trigger workflows reliably
4. **Code validation** - No way to verify parser changes took effect without manual UI execution

### 🔧 Technical Gotchas

#### Parser Regex Issues
```javascript
// RSS has HTML entities escaped
<b>City/Area</b>:&amp;nbsp;Nevada City  // Actual
<b>City/Area</b>:&nbsp;Nevada City     // Expected

// Need to handle both:
const patterns = [
  new RegExp(`<b>${label}</b>:&nbsp;([^<]+)`, 'i'),
  new RegExp(`<b>${label}</b>:&amp;nbsp;([^<]+)`, 'i')
];
```

#### GUID Extraction
```javascript
// RSS format:
<guid>http://uid.trumba.com/event/177609910</guid>

// Correct regex:
const idMatch = guid.match(/event\/(\d+)/);  // ✅
// NOT:
const idMatch = guid.match(/\/(\d+)$/);      // ❌ (matches anything ending in digits)
```

#### Postgres UPSERT via MCP
```javascript
// n8n-mcp upsert operation with onConflict doesn't work
// Use executeQuery instead:
{
  operation: "executeQuery",
  query: "INSERT INTO ... ON CONFLICT (...) DO UPDATE SET ...",
  options: {
    queryReplacement: "={{ $json.field1 }},={{ $json.field2 }},..."
  }
}
```

---

## Current State

**Workflow ID:** `EAdNPKCQrLvPbfD0`
**Workflow URL:** http://localhost:5678/workflow/EAdNPKCQrLvPbfD0
**Status:** Active with schedule trigger (6am daily)

**Database:**
- Project: telegram-qa-bot (Supabase)
- Table: `events`
- Current data: 200 events (title/description/date only, no metadata)

**Next Steps to Resume:**
1. Verify parser changes took effect by running workflow in UI
2. Check execution output to see if metadata is now extracted
3. Query database to verify `source_event_id` and metadata populated
4. Test UPSERT logic by running workflow twice (should update, not error)
5. Once working, add second source (Library calendar)

---

## Source Priority Matrix

### Tier 1: RSS/iCal feeds (easiest)
| Source | Status | Notes |
|--------|--------|-------|
| **KNCO (Trumba)** | 🔴 Partial | Fetching works, metadata extraction broken |
| **Nevada County Library** | ⏸️ Not started | LibCal structured HTML |
| **County Calendar** | ⏸️ Not started | iCal option available |

### Tier 2: Static HTML (medium)
| Source | Status | Notes |
|--------|--------|-------|
| All sources | ⏸️ Not started | Blocked on Tier 1 completion |

---

## Useful Commands

### Query Current Events
```sql
SELECT
  COUNT(*) as total,
  COUNT(DISTINCT source_event_id) as unique_ids,
  COUNT(CASE WHEN age_range IS NOT NULL THEN 1 END) as with_age,
  COUNT(CASE WHEN city_area IS NOT NULL THEN 1 END) as with_city,
  MAX(scraped_at) as last_scrape
FROM events
WHERE source_name = 'knco';
```

### Sample Event Data
```sql
SELECT title, age_range, city_area, source_event_id, event_date
FROM events
WHERE source_name = 'knco'
LIMIT 5;
```

---

## Timeline

**Session 1 (2025-10-06):**
- Created workflow structure
- Built parser (3 iterations)
- Implemented UPSERT logic
- Hit blocker: Parser updates not taking effect
- **Duration:** ~3 hours
- **Result:** Infrastructure complete, data extraction broken

---

## Lessons for Future Projects

1. **Verify code changes take effect** - Don't assume MCP updates propagate immediately
2. **Test in UI first** - When automation fails, manual verification is essential
3. **Webhooks are problematic** - Production webhooks can't be automated, use schedules instead
4. **Advanced elicitation is valuable** - Running multiple analysis methods (Failure Mode, First Principles, 5 Whys, etc.) revealed design flaws quickly

---

**Last Updated:** 2025-10-07 05:45 UTC
**Status:** Blocked on parser execution verification
**Recommendation:** Resume by testing workflow manually in UI to verify latest parser code works

---

## Fun Factor: NOT FUN 😤

Original goals:
- 🎯 Solves real problem (finding kid events) - **Still true**
- 🕷️ Learning new skill (web scraping) - **Learned n8n limitations instead**
- 🧩 Each source is a mini-puzzle - **Blocked on first source**
- 📊 Visible progress (events accumulating in DB) - **Data incomplete**
- 🤖 AI categorization is magic - **Never reached Phase 3**
- 🎁 End result is actually useful - **Not functional yet**

Reality: Fought tooling more than solved the problem.
