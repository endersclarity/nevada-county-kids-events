"""Data normalizer for event data"""
import hashlib
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class NormalizedEvent:
    """Normalized event data structure matching database schema"""

    # Required fields
    title: str
    event_date: datetime
    source_name: str

    # Generated fields
    content_hash: str
    quality_score: int

    # Optional fields
    description: Optional[str] = None
    venue: Optional[str] = None
    city_area: Optional[str] = None
    source_url: Optional[str] = None
    source_event_id: Optional[str] = None
    age_range: Optional[str] = None
    price: Optional[str] = None
    is_free: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        data = asdict(self)
        # Convert datetime to ISO format string
        data['event_date'] = self.event_date.isoformat()
        return data


class Normalizer:
    """Normalize event data from various sources into standard format"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    def normalize(
        self,
        events: List[Dict[str, Any]],
        min_quality_score: int = 0,
        log_quality_stats: bool = True
    ) -> List[NormalizedEvent]:
        """
        Normalize a list of raw event dictionaries.

        Args:
            events: Raw event data from scraper
            min_quality_score: Minimum quality score (0-100) to include events (default: 0)
            log_quality_stats: Whether to log quality statistics (default: True)

        Returns:
            List of NormalizedEvent objects
        """
        normalized = []
        validation_errors = 0
        filtered_count = 0

        for event in events:
            try:
                normalized_event = self._normalize_event(event)
                if normalized_event:
                    # Filter by quality score
                    if normalized_event.quality_score < min_quality_score:
                        filtered_count += 1
                        logger.debug(
                            f"Event '{normalized_event.title}' filtered (quality score: {normalized_event.quality_score})"
                        )
                        continue

                    normalized.append(normalized_event)
            except Exception as e:
                validation_errors += 1
                logger.error(f"Validation error for event '{event.get('title', 'Unknown')}': {e}")
                continue

        # Log quality statistics
        if log_quality_stats and normalized:
            self._log_quality_stats(normalized)

        logger.info(
            f"Normalized {len(normalized)} events "
            f"({validation_errors} validation errors, {filtered_count} filtered by quality)"
        )

        return normalized

    def _log_quality_stats(self, events: List[NormalizedEvent]) -> None:
        """Log quality statistics for normalized events."""
        if not events:
            return

        scores = [e.quality_score for e in events]
        avg_score = sum(scores) / len(scores)

        # Count by quality tier
        high_quality = sum(1 for s in scores if s >= 80)
        medium_quality = sum(1 for s in scores if 50 <= s < 80)
        low_quality = sum(1 for s in scores if s < 50)

        # Calculate percentages
        total = len(events)
        high_pct = (high_quality / total * 100) if total > 0 else 0
        med_pct = (medium_quality / total * 100) if total > 0 else 0
        low_pct = (low_quality / total * 100) if total > 0 else 0

        logger.info("=" * 50)
        logger.info(f"Quality Stats: Avg={avg_score:.0f}, High={high_pct:.0f}%, Med={med_pct:.0f}%, Low={low_pct:.0f}%")
        if low_quality > 0:
            logger.warning(f"{low_quality} events below quality threshold (score < 50)")
        logger.info("=" * 50)

    def _normalize_event(self, event: Dict[str, Any]) -> Optional[NormalizedEvent]:
        """Normalize a single event."""

        # Validate required fields
        title = event.get('title', '').strip()
        if not title:
            logger.warning("Event missing required field: title")
            return None

        # Parse event date
        event_date = self._parse_date(event.get('event_date', ''))
        if not event_date:
            logger.warning(f"Event '{title}' missing valid event_date")
            return None

        # Extract optional fields with defaults
        description = event.get('description', '')[:2000] if event.get('description') else None
        venue = event.get('venue', '')[:200] if event.get('venue') else None
        city_area = event.get('city_area', '')[:100] if event.get('city_area') else None
        source_url = event.get('source_url', '')[:500] if event.get('source_url') else None
        source_event_id = event.get('source_event_id', '')[:100] if event.get('source_event_id') else None
        age_range = event.get('age_range', '')[:50] if event.get('age_range') else None
        price = event.get('price', '')[:100] if event.get('price') else None
        is_free = event.get('is_free', False)

        # Generate content hash
        content_hash = self._generate_content_hash(title, event_date, description or '')

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            title=title,
            event_date=event_date,
            description=description,
            venue=venue,
            age_range=age_range,
            price=price
        )

        return NormalizedEvent(
            title=title,
            event_date=event_date,
            source_name=self.source_name,
            content_hash=content_hash,
            quality_score=quality_score,
            description=description,
            venue=venue,
            city_area=city_area,
            source_url=source_url,
            source_event_id=source_event_id,
            age_range=age_range,
            price=price,
            is_free=is_free
        )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string into datetime object.

        Handles:
        - ISO 8601: 2025-10-15T10:00:00-07:00
        - Simple date: 2025-10-15
        - Other common formats
        """
        if not date_str:
            return None

        # Try ISO 8601 format first
        for fmt in [
            '%Y-%m-%dT%H:%M:%S%z',   # With timezone
            '%Y-%m-%dT%H:%M:%S',     # Without timezone
            '%Y-%m-%d',              # Simple date
            '%Y/%m/%d',              # Slash separator
            '%m/%d/%Y',              # US format
        ]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Try fromisoformat as fallback
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            pass

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def _generate_content_hash(self, title: str, event_date: datetime, description: str) -> str:
        """
        Generate MD5 hash for duplicate detection.

        Uses title + date + first 200 chars of description.
        """
        content = f"{title}|{event_date.isoformat()}|{description[:200]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _calculate_quality_score(
        self,
        title: str,
        event_date: datetime,
        description: Optional[str],
        venue: Optional[str],
        age_range: Optional[str],
        price: Optional[str]
    ) -> int:
        """
        Calculate quality score (0-100) based on data completeness.

        Scoring:
        - Title: 20 points
        - Event date: 20 points
        - Description: 20 points (10 extra if > 50 chars)
        - Venue: 10 points
        - Age range: 10 points
        - Price: 10 points
        """
        score = 0

        # Required fields (always have these if we get here)
        score += 20 if title else 0
        score += 20 if event_date else 0

        # Optional fields
        if description:
            score += 20
            if len(description) > 50:
                score += 10

        score += 10 if venue else 0
        score += 10 if age_range else 0
        score += 10 if price else 0

        return min(score, 100)  # Cap at 100
