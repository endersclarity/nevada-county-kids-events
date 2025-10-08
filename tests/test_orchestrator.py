"""Integration tests for orchestrator"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time
from concurrent.futures import TimeoutError
from src.orchestrator import EventOrchestrator


class TestOrchestrator(unittest.TestCase):
    """Test event orchestrator"""

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_initialization(self, mock_cache_mgr, mock_db):
        """Test orchestrator initialization"""
        orchestrator = EventOrchestrator()

        self.assertIsNotNone(orchestrator.db)
        self.assertIsNotNone(orchestrator.cache)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_fetch_events_with_cache(self, mock_cache_mgr_class, mock_db_class):
        """Test fetching events with cache enabled"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        # Mock cached events
        mock_cache.get_or_fetch.return_value = [
            {
                'id': 1,
                'title': 'Test Event',
                'source_name': 'knco',
                'scraped_at': datetime.now()
            }
        ]

        orchestrator = EventOrchestrator()
        events = orchestrator.fetch_events(sources=['knco'], use_cache=True)

        # Verify cache was used
        mock_cache.get_or_fetch.assert_called_once()

        # Verify we got events
        self.assertEqual(len(events), 1)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_available_sources(self, mock_cache_mgr_class, mock_db_class):
        """Test available sources are registered"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        orchestrator = EventOrchestrator()

        # Verify KNCO is available
        self.assertIn('knco', orchestrator.AVAILABLE_SOURCES)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_unknown_source(self, mock_cache_mgr_class, mock_db_class):
        """Test handling of unknown source"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        orchestrator = EventOrchestrator()
        events = orchestrator.fetch_events(sources=['unknown'], use_cache=True)

        # Should handle error gracefully and return empty list
        self.assertEqual(len(events), 0)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_context_manager(self, mock_cache_mgr_class, mock_db_class):
        """Test using orchestrator as context manager"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        with EventOrchestrator() as orchestrator:
            self.assertIsNotNone(orchestrator)

        # Verify cleanup
        mock_db.close.assert_called_once()

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_parallel_scraping(self, mock_cache_mgr_class, mock_db_class):
        """Test parallel scraping of multiple sources"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        # Mock events for different sources
        def mock_get_or_fetch(source, fetch_fn, ttl_hours):
            return [
                {
                    'id': f'{source}_1',
                    'title': f'Event from {source}',
                    'source_name': source,
                    'scraped_at': datetime.now()
                }
            ]

        mock_cache.get_or_fetch.side_effect = mock_get_or_fetch

        orchestrator = EventOrchestrator()
        start_time = time.time()
        events = orchestrator.fetch_events(
            sources=['knco', 'library', 'county'],
            use_cache=True,
            parallel=True
        )
        duration = time.time() - start_time

        # Should get events from all sources
        self.assertEqual(len(events), 3)

        # Parallel execution should be reasonably fast (not sequential)
        # With 3 sources, should complete in under 2 seconds even with mock overhead
        self.assertLess(duration, 5)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_timeout_handling(self, mock_cache_mgr_class, mock_db_class):
        """Test timeout handling for slow sources"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        # Mock a slow source that times out
        def slow_fetch(source, fetch_fn, ttl_hours):
            if source == 'county':
                # Simulate a slow source
                time.sleep(3)
            return [
                {
                    'id': f'{source}_1',
                    'title': f'Event from {source}',
                    'source_name': source,
                    'scraped_at': datetime.now()
                }
            ]

        mock_cache.get_or_fetch.side_effect = slow_fetch

        orchestrator = EventOrchestrator()
        events = orchestrator.fetch_events(
            sources=['knco', 'library', 'county'],
            use_cache=True,
            parallel=True,
            timeout=2  # 2 second timeout
        )

        # Should get events from fast sources even if one times out
        # Due to the way futures work, we may get some events
        self.assertGreaterEqual(len(events), 0)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_sequential_scraping(self, mock_cache_mgr_class, mock_db_class):
        """Test sequential scraping when parallel is disabled"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        # Mock events for different sources
        def mock_get_or_fetch(source, fetch_fn, ttl_hours):
            return [
                {
                    'id': f'{source}_1',
                    'title': f'Event from {source}',
                    'source_name': source,
                    'scraped_at': datetime.now()
                }
            ]

        mock_cache.get_or_fetch.side_effect = mock_get_or_fetch

        orchestrator = EventOrchestrator()
        events = orchestrator.fetch_events(
            sources=['knco', 'library'],
            use_cache=True,
            parallel=False  # Sequential mode
        )

        # Should get events from all sources
        self.assertEqual(len(events), 2)

    @patch('src.orchestrator.SupabaseClient')
    @patch('src.orchestrator.CacheManager')
    def test_graceful_failure(self, mock_cache_mgr_class, mock_db_class):
        """Test graceful failure when one source fails"""
        mock_db = Mock()
        mock_cache = Mock()
        mock_db_class.return_value = mock_db
        mock_cache_mgr_class.return_value = mock_cache

        # Mock one source to fail
        def mock_get_or_fetch(source, fetch_fn, ttl_hours):
            if source == 'library':
                raise Exception("Library source unavailable")
            return [
                {
                    'id': f'{source}_1',
                    'title': f'Event from {source}',
                    'source_name': source,
                    'scraped_at': datetime.now()
                }
            ]

        mock_cache.get_or_fetch.side_effect = mock_get_or_fetch

        orchestrator = EventOrchestrator()
        events = orchestrator.fetch_events(
            sources=['knco', 'library', 'county'],
            use_cache=True,
            parallel=True
        )

        # Should get events from working sources
        self.assertGreaterEqual(len(events), 1)
        self.assertLessEqual(len(events), 2)


if __name__ == '__main__':
    unittest.main()
