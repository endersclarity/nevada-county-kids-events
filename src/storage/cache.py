"""Cache manager for event data"""
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
from .supabase import SupabaseClient

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage caching of event data with TTL"""

    def __init__(self, db_client: SupabaseClient):
        """
        Initialize cache manager.

        Args:
            db_client: Supabase client for database operations
        """
        self.db = db_client

    def get_or_fetch(
        self,
        source_name: str,
        scraper_func: Callable[[], List[Dict[str, Any]]],
        ttl_hours: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get cached events or fetch fresh data if cache is stale.

        Args:
            source_name: Source identifier (e.g., 'knco')
            scraper_func: Function to call if cache miss (returns raw event dicts)
            ttl_hours: Cache time-to-live in hours

        Returns:
            List of event dictionaries
        """
        # Check cache first
        cached = self.db.get_cached_events(source_name, ttl_hours)

        if cached:
            # Cache hit
            age = datetime.now() - cached[0]['scraped_at']
            logger.info(
                f"Cache HIT for {source_name}: {len(cached)} events "
                f"(age: {age.total_seconds() / 3600:.1f} hours)"
            )
            return cached

        # Cache miss - fetch fresh data
        logger.info(f"Cache MISS for {source_name}, fetching fresh data...")

        try:
            # Call scraper function to get raw events
            raw_events = scraper_func()

            if not raw_events:
                logger.warning(f"Scraper returned no events for {source_name}")
                return []

            # Import normalizer here to avoid circular dependency
            from ..processors.normalizer import Normalizer

            # Normalize events
            normalizer = Normalizer(source_name)
            normalized_events = normalizer.normalize(raw_events)

            # Store in database
            count = self.db.upsert_events(normalized_events)
            logger.info(f"Cached {count} fresh events for {source_name}")

            # Convert back to dict format for return
            # (re-query to get database IDs and timestamps)
            return self.db.get_cached_events(source_name, ttl_hours)

        except Exception as e:
            logger.error(f"Error during cache fetch for {source_name}: {e}")
            raise

    def invalidate_cache(self, source_name: str):
        """
        Invalidate (clear) cache for a specific source.

        Useful for testing or forced refresh.

        Args:
            source_name: Source to invalidate
        """
        logger.info(f"Invalidating cache for {source_name}")

        # Delete events older than 0 hours (all events for this source)
        # This is done by upserting with very old scraped_at timestamp
        # In production, you might use a DELETE query instead

        # For now, we'll just log - actual implementation would delete from DB
        logger.warning("Cache invalidation not fully implemented (requires DELETE query)")
