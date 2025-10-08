"""Event orchestrator - coordinates scraping, normalization, and storage"""
import sys
import argparse
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

from .config import Config
from .scrapers.knco import KNCOScraper
from .scrapers.library import LibraryScraper
from .scrapers.county import CountyScraper
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
        'library': LibraryScraper,
        'county': CountyScraper,
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

    def _fetch_single_source(
        self,
        source: str,
        use_cache: bool,
        timeout: int,
        min_quality_score: int = None
    ) -> Tuple[str, List[dict], bool, float]:
        """
        Fetch events from a single source with timeout.

        Args:
            source: Source name
            use_cache: Whether to use cache
            timeout: Timeout in seconds
            min_quality_score: Minimum quality score (0-100) to include events

        Returns:
            Tuple of (source, events, is_cache_hit, duration)
        """
        source_start = datetime.now()

        if min_quality_score is None:
            min_quality_score = Config.MIN_QUALITY_SCORE

        try:
            scraper_class = self.AVAILABLE_SOURCES.get(source)
            if not scraper_class:
                raise ValueError(f"Unknown source: {source}")

            scraper = scraper_class()

            if use_cache:
                # Use cache manager
                events = self.cache.get_or_fetch(
                    source,
                    scraper.fetch,
                    ttl_hours=Config.CACHE_TTL_HOURS
                )
                # Check if it was a cache hit
                is_cache_hit = events and len(events) > 0 and 'scraped_at' in events[0]

                # If quality filtering is enabled and we have cached events, filter them
                if min_quality_score > 0 and events:
                    original_count = len(events)
                    events = [e for e in events if e.get('quality_score', 0) >= min_quality_score]
                    if len(events) < original_count:
                        logger.info(
                            f"Filtered {original_count - len(events)} cached events below quality score {min_quality_score}"
                        )
            else:
                # Bypass cache - scrape directly
                logger.info(f"Bypassing cache for {source}")
                raw_events = scraper.fetch()

                from .processors.normalizer import Normalizer
                normalizer = Normalizer(source)
                normalized = normalizer.normalize(
                    raw_events,
                    min_quality_score=min_quality_score,
                    log_quality_stats=True
                )

                # Store in database
                self.db.upsert_events(normalized)

                # Convert to dict format
                events = [e.to_dict() for e in normalized]
                is_cache_hit = False

            duration = (datetime.now() - source_start).total_seconds()
            return source, events, is_cache_hit, duration

        except Exception as e:
            duration = (datetime.now() - source_start).total_seconds()
            raise Exception(f"Error fetching from {source}: {e}")

    def fetch_events(
        self,
        sources: List[str] = None,
        use_cache: bool = True,
        timeout: int = None,
        parallel: bool = True,
        min_quality_score: int = None
    ) -> List[dict]:
        """
        Fetch events from specified sources.

        Args:
            sources: List of source names (default: ['knco'])
            use_cache: Whether to use cache (default: True)
            timeout: Per-source timeout in seconds (default: Config.SCRAPER_TIMEOUT)
            parallel: Whether to scrape sources in parallel (default: True)
            min_quality_score: Minimum quality score (0-100) to include events (default: Config.MIN_QUALITY_SCORE)

        Returns:
            Combined list of event dictionaries
        """
        if sources is None:
            sources = ['knco']

        if timeout is None:
            timeout = Config.SCRAPER_TIMEOUT

        if min_quality_score is None:
            min_quality_score = Config.MIN_QUALITY_SCORE

        start_time = datetime.now()
        all_events = []
        cache_hits = 0
        successful_sources = []
        failed_sources = []
        timed_out_sources = []

        if parallel and len(sources) > 1:
            logger.info(f"Scraping {len(sources)} sources in parallel...")

            # Use ThreadPoolExecutor for parallel execution
            with ThreadPoolExecutor(max_workers=len(sources)) as executor:
                # Submit all scraping tasks
                future_to_source = {
                    executor.submit(
                        self._fetch_single_source,
                        source,
                        use_cache,
                        timeout,
                        min_quality_score
                    ): source
                    for source in sources
                }

                # Process completed futures with timeout
                for future in as_completed(future_to_source, timeout=timeout + 5):
                    source = future_to_source[future]
                    try:
                        # Get result with timeout
                        source_name, events, is_cache_hit, duration = future.result(timeout=timeout)

                        all_events.extend(events)
                        successful_sources.append(source_name)

                        if is_cache_hit:
                            cache_hits += 1

                        logger.info(f"{source_name} completed in {duration:.1f}s ({len(events)} events)")

                    except TimeoutError:
                        logger.warning(f"{source} timed out after {timeout}s (0 events)")
                        timed_out_sources.append(source)
                    except Exception as e:
                        logger.error(f"{source} failed: {e}")
                        failed_sources.append(source)
        else:
            # Sequential execution (original behavior)
            logger.info(f"Fetching events from: {', '.join(sources)}")

            for source in sources:
                try:
                    source_name, events, is_cache_hit, duration = self._fetch_single_source(
                        source, use_cache, timeout, min_quality_score
                    )

                    all_events.extend(events)
                    successful_sources.append(source_name)

                    if is_cache_hit:
                        cache_hits += 1

                    logger.info(f"Retrieved {len(events)} events from {source_name}")

                except Exception as e:
                    logger.error(str(e))
                    failed_sources.append(source)

        # Calculate execution time
        duration = (datetime.now() - start_time).total_seconds()

        # Log execution summary
        logger.info("=" * 50)
        logger.info(f"[SUCCESS] Total: {len(all_events)} events from {len(successful_sources)}/{len(sources)} sources")

        if cache_hits > 0:
            logger.info(f"Cache hits: {cache_hits}")

        if timed_out_sources:
            logger.info(f"Timed out: {', '.join(timed_out_sources)}")

        if failed_sources:
            logger.info(f"Failed: {', '.join(failed_sources)}")

        logger.info(f"Total execution time: {duration:.1f}s")
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
        '--sources',
        default='knco',
        help='Comma-separated list of sources to scrape (default: knco)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Bypass cache and force fresh scrape'
    )
    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel scraping (scrape sources sequentially)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=None,
        help=f'Per-source timeout in seconds (default: {Config.SCRAPER_TIMEOUT})'
    )
    parser.add_argument(
        '--min-quality',
        type=int,
        default=None,
        help=f'Minimum quality score (0-100) to include events (default: {Config.MIN_QUALITY_SCORE})'
    )

    args = parser.parse_args()

    # Parse sources
    sources = [s.strip() for s in args.sources.split(',')]

    try:
        with EventOrchestrator() as orchestrator:
            events = orchestrator.fetch_events(
                sources=sources,
                use_cache=not args.no_cache,
                parallel=not args.no_parallel,
                timeout=args.timeout,
                min_quality_score=args.min_quality
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
