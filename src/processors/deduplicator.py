"""Cross-source event deduplication"""
import logging
from typing import List, Dict, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Detect and merge duplicate events across sources.

    Strategies:
    1. Exact match on content_hash
    2. Fuzzy match: 85%+ title similarity + same date

    Priority: KNCO > Library > County
    """

    SOURCE_PRIORITY = {
        'knco': 1,
        'library': 2,
        'county': 3
    }

    SIMILARITY_THRESHOLD = 0.85

    def deduplicate(self, events: List[Dict]) -> List[Dict]:
        """
        Deduplicate events list.

        Args:
            events: List of normalized event dictionaries

        Returns:
            Deduplicated list with merged metadata
        """
        if not events:
            return []

        # Track seen hashes and titles
        seen_hashes: Set[str] = set()
        seen_by_date: Dict[str, List[Dict]] = {}
        deduplicated = []
        duplicates_found = 0

        for event in events:
            # Strategy 1: Exact hash match
            content_hash = event.get('content_hash', '')
            if content_hash and content_hash in seen_hashes:
                logger.debug(f"Exact duplicate found (hash): {event.get('title')}")
                duplicates_found += 1
                continue

            # Strategy 2: Fuzzy title + date match
            event_date = event.get('event_date', '')
            title = event.get('title', '')

            if event_date and title:
                # Check against events on same date
                if event_date in seen_by_date:
                    duplicate = self._find_fuzzy_duplicate(event, seen_by_date[event_date])
                    if duplicate:
                        # Merge metadata into existing event
                        self._merge_metadata(duplicate, event)
                        logger.debug(f"Fuzzy duplicate found: '{title}' ~= '{duplicate.get('title')}'")
                        duplicates_found += 1
                        continue

                # Not a duplicate - add to tracking
                if event_date not in seen_by_date:
                    seen_by_date[event_date] = []
                seen_by_date[event_date].append(event)

            # Add to deduplicated list
            if content_hash:
                seen_hashes.add(content_hash)
            deduplicated.append(event)

        logger.info(f"Deduplication: {len(events)} → {len(deduplicated)} ({duplicates_found} duplicates removed)")

        return deduplicated

    def _find_fuzzy_duplicate(self, event: Dict, candidates: List[Dict]) -> Dict:
        """
        Find fuzzy duplicate in candidates list.

        Returns:
            Duplicate event dict if found, None otherwise
        """
        title = event.get('title', '').lower()

        for candidate in candidates:
            candidate_title = candidate.get('title', '').lower()
            similarity = SequenceMatcher(None, title, candidate_title).ratio()

            if similarity >= self.SIMILARITY_THRESHOLD:
                return candidate

        return None

    def _merge_metadata(self, target: Dict, source: Dict):
        """
        Merge metadata from source into target (in-place).

        Takes non-null values from source and adds to target.
        Respects source priority (keeps higher priority source values).
        """
        target_priority = self.SOURCE_PRIORITY.get(target.get('source_name', ''), 999)
        source_priority = self.SOURCE_PRIORITY.get(source.get('source_name', ''), 999)

        # Only merge if target has higher priority (lower number)
        if source_priority < target_priority:
            # Source is higher priority - swap core fields
            for field in ['title', 'description', 'source_url']:
                if source.get(field):
                    target[field] = source[field]

        # Merge optional fields (take non-null from either source)
        for field in ['venue', 'age_range', 'price', 'time_range', 'categories']:
            if not target.get(field) and source.get(field):
                target[field] = source[field]

        # Log merge
        logger.debug(f"Merged metadata: {source.get('source_name')} → {target.get('source_name')}")
