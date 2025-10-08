"""Event orchestrator - coordinates scraping, normalization, and storage"""
import sys
import argparse
import logging
from typing import List
from datetime import datetime

from .config import Config
from .scrapers.knco import KNCOScraper
from .storage.supabase import SupabaseClient
from .storage.cache import CacheManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class EventOrchestrator:
    """Orchestrate event scraping and storage"""

    AVAILABLE_SOURCES = {
        'knco': KNCOScraper,
    }

    def __init__(self):
        """Initialize orchestrator with database connection"""
        try:
            self.db = SupabaseClient()
            self.cache = CacheManager(self.db)
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    def fetch_events(
        self,
        sources: List[str] = None,
        use_cache: bool = True
    ) -> List[dict]:
        """
        Fetch events from specified sources.

        Args:
            sources: List of source names (default: ['knco'])
            use_cache: Whether to use cache (default: True)

        Returns:
            Combined list of event dictionaries
        """
        if sources is None:
            sources = ['knco']

        start_time = datetime.now()
        all_events = []
        cache_hits = 0
        errors = 0

        logger.info(f"Fetching events from: {', '.join(sources)}")

        for source in sources:
            try:
                # Get scraper for this source
                scraper_class = self.AVAILABLE_SOURCES.get(source)
                if not scraper_class:
                    logger.error(f"Unknown source: {source}")
                    errors += 1
                    continue

                scraper = scraper_class()

                if use_cache:
                    # Use cache manager
                    events = self.cache.get_or_fetch(
                        source,
                        scraper.fetch,
                        ttl_hours=Config.CACHE_TTL_HOURS
                    )
                    # Check if it was a cache hit (events have scraped_at timestamp)
                    if events and 'scraped_at' in events[0]:
                        cache_hits += 1
                else:
                    # Bypass cache - scrape directly
                    logger.info(f"Bypassing cache for {source}")
                    raw_events = scraper.fetch()

                    from .processors.normalizer import Normalizer
                    normalizer = Normalizer(source)
                    normalized = normalizer.normalize(raw_events)

                    # Store in database
                    self.db.upsert_events(normalized)

                    # Convert to dict format
                    events = [e.to_dict() for e in normalized]

                all_events.extend(events)
                logger.info(f"Retrieved {len(events)} events from {source}")

            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                errors += 1
                continue

        # Calculate execution time
        duration = (datetime.now() - start_time).total_seconds()

        # Log summary
        logger.info("=" * 50)
        logger.info(f"[SUCCESS] Total: {len(all_events)} events")
        logger.info(f"Sources: {len(sources)} ({cache_hits} cache hits)")
        logger.info(f"Errors: {errors}")
        logger.info(f"Execution time: {duration:.2f}s")
        logger.info("=" * 50)

        return all_events

    def close(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Nevada County Kids Events - Event Orchestrator"
    )
    parser.add_argument(
        '--source',
        default='knco',
        help='Event source to scrape (default: knco)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Bypass cache and force fresh scrape'
    )

    args = parser.parse_args()

    try:
        with EventOrchestrator() as orchestrator:
            events = orchestrator.fetch_events(
                sources=[args.source],
                use_cache=not args.no_cache
            )

            if not events:
                logger.warning("No events retrieved")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
