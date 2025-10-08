# User Stories - Nevada County Kids Events

**Project:** Nevada County Kids Events Agent
**Total Stories:** 28
**Total Points:** 102 (87 to MVP)

---

## Quick Navigation

- [Epic 1: Source Research](#epic-1-source-research-11-pts) (4 stories, 11 pts)
- [Epic 2: Core Engine](#epic-2-core-scraping-engine-21-pts) (6 stories, 21 pts)
- [Epic 3: Multi-Source](#epic-3-multi-source-integration-21-pts) (5 stories, 21 pts)
- [Epic 4: Delivery](#epic-4-delivery-layer-23-pts) (5 stories, 23 pts)
- [Epic 5: Slash Command](#epic-5-slash-command-interface-13-pts) (5 stories, 13 pts)
- [Epic 6: Polish](#epic-6-polish--optimization-13-pts) (3 stories, 13 pts - Post-MVP)

---

## Epic Overview

### Epic 1: Source Research & Evaluation (11 pts)

**Status:** 🔵 Ready to start
**Goal:** Identify top 3 event sources for MVP

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E1.1 | Evaluate KNCO RSS Feed | 3 | 🔵 Ready |
| E1.2 | Evaluate Library Calendar | 3 | 🔵 Ready |
| E1.3 | Evaluate County Calendar | 3 | 🔵 Ready |
| E1.4 | Prioritize Sources | 2 | ⏸️ Blocked |

**Directory:** `epic-1-source-research/`

---

### Epic 2: Core Scraping Engine (21 pts)

**Status:** ⏸️ Blocked by E1
**Goal:** Working prototype with single source

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E2.1 | Python Project Setup | 2 | ⏸️ Blocked |
| E2.2 | KNCO RSS Scraper | 5 | ⏸️ Blocked |
| E2.3 | Data Normalizer | 3 | ⏸️ Blocked |
| E2.4 | Supabase Integration | 5 | ⏸️ Blocked |
| E2.5 | Cache Layer | 3 | ⏸️ Blocked |
| E2.6 | Orchestrator | 3 | ⏸️ Blocked |

**Directory:** `epic-2-core-engine/`

---

### Epic 3: Multi-Source Integration (21 pts)

**Status:** ⏸️ Blocked by E2
**Goal:** 3 sources + deduplication

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E3.1 | Library Scraper | 5 | ⏸️ Blocked |
| E3.2 | County Scraper | 5 | ⏸️ Blocked |
| E3.3 | Cross-Source Deduplication | 5 | ⏸️ Blocked |
| E3.4 | Parallel Scraping | 3 | ⏸️ Blocked |
| E3.5 | Data Quality Validation | 3 | ⏸️ Blocked |

**Directory:** `epic-3-multi-source/`

---

### Epic 4: Delivery Layer (23 pts)

**Status:** ⏸️ Blocked by E2
**Goal:** Multi-modal output (email, Telegram, calendar)

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E4.1 | Delivery Interface Design | 2 | ⏸️ Blocked |
| E4.2 | Email Delivery | 5 | ⏸️ Blocked |
| E4.3 | Telegram Delivery | 5 | ⏸️ Blocked |
| E4.4 | Google Calendar Integration | 8 | ⏸️ Blocked |
| E4.5 | Delivery Router | 3 | ⏸️ Blocked |

**Directory:** `epic-4-delivery/`

**Note:** E4.4 (Google Calendar) is optional for MVP - prioritize E4.2 + E4.3

---

### Epic 5: Slash Command Interface (13 pts)

**Status:** ⏸️ Blocked by E2+E4
**Goal:** Claude Code command end-to-end

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E5.1 | Design Claude Code Command | 2 | ⏸️ Blocked |
| E5.2 | Command Orchestration | 3 | ⏸️ Blocked |
| E5.3 | Conversational Delivery Selection | 3 | ⏸️ Blocked |
| E5.4 | Error Handling & Feedback | 3 | ⏸️ Blocked |
| E5.5 | Documentation & Help | 2 | ⏸️ Blocked |

**Directory:** `epic-5-slash-command/`

**🎯 MVP COMPLETE after E5.5!**

---

### Epic 6: Polish & Optimization (13 pts)

**Status:** ⏸️ Post-MVP
**Goal:** Enhanced intelligence (categorization, scoring)

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| E6.1 | Event Categorization | 5 | ⏸️ Blocked |
| E6.2 | Kid-Friendly Scoring | 5 | ⏸️ Blocked |
| E6.3 | Natural Language Summarization | 3 | ⏸️ Blocked |

**Directory:** `epic-6-polish/`

**Note:** These are enhancements to implement after MVP validation

---

## Story Status Legend

- 🔵 **Ready** - No blockers, ready to start
- ⏸️ **Blocked** - Waiting on dependencies
- 🟡 **In Progress** - Currently being worked on
- ✅ **Complete** - Done and verified

---

## Sprint Suggestions

### Sprint 0: Research (11 pts)
Complete Epic 1 (all 4 stories)

### Sprint 1: Foundation (21 pts)
Complete Epic 2 (all 6 stories)

### Sprint 2: Multi-Source (21 pts)
Complete Epic 3 (all 5 stories)

### Sprint 3: Delivery (15-23 pts)
Complete E4.1-E4.3 + E4.5 (skip GCal for now)

### Sprint 4: MVP (13 pts)
Complete Epic 5 (all 5 stories)

### Sprint 5+: Polish (13+ pts)
Epic 6 stories as needed

---

## Using This Directory

### To Start a Story:
1. Read the story card in the appropriate epic folder
2. Update status to 🟡 In Progress
3. Check Dependencies section - ensure blockers are complete
4. Follow Acceptance Criteria checklist
5. Mark DoD items as you complete them

### To Create a New Story:
1. Copy `templates/story-template.md`
2. Fill in all sections
3. Save to appropriate epic folder
4. Update this README with the new story

---

## Story Point Reference

- **1 pt:** Trivial (1 hour or less)
- **2 pts:** Simple (2-4 hours)
- **3 pts:** Moderate (4-8 hours)
- **5 pts:** Complex (1-2 days)
- **8 pts:** Very Complex (3-5 days)
- **13 pts:** Epic-level (should be broken down)

---

## Related Documents

- [PROJECT-BRIEF.md](../PROJECT-BRIEF.md) - Strategic overview
- [PRD.md](../PRD.md) - Detailed requirements
- [SCRUM-BACKLOG.md](../SCRUM-BACKLOG.md) - Sprint planning

---

**Created:** 2025-10-07
**Last Updated:** 2025-10-07
**Maintained by:** Product Owner (Sarah)
