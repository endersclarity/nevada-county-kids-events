"""Unit tests for cache manager"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from src.storage.cache import CacheManager
from src.processors.normalizer import NormalizedEvent


class TestCacheManager(unittest.TestCase):
    """Test cache manager"""

    def setUp(self):
        """Set up test cache manager with mocked DB client"""
        self.mock_db = Mock()
        self.cache = CacheManager(self.mock_db)

    def test_cache_hit(self):
        """Test cache hit returns cached data"""
        # Mock cached data (recent)
        cached_events = [
            {
                'id': 1,
                'title': 'Cached Event',
                'source_name': 'test',
                'scraped_at': datetime.now() - timedelta(hours=2)
            }
        ]
        self.mock_db.get_cached_events.return_value = cached_events

        # Mock scraper (should not be called)
        scraper_func = Mock()

        # Execute
        result = self.cache.get_or_fetch('test', scraper_func, ttl_hours=6)

        # Verify
        self.assertEqual(result, cached_events)
        self.mock_db.get_cached_events.assert_called_once_with('test', 6)
        scraper_func.assert_not_called()  # Should not scrape on cache hit

    @patch('src.processors.normalizer.Normalizer')
    def test_cache_miss(self, mock_normalizer_class):
        """Test cache miss triggers scraping"""
        # Mock cache miss (empty)
        self.mock_db.get_cached_events.side_effect = [
            [],  # First call: cache miss
            [{'id': 1, 'title': 'Fresh Event'}]  # Second call: after upsert
        ]

        # Mock scraper returning raw events
        raw_events = [
            {
                'title': 'Fresh Event',
                'event_date': '2025-10-15T10:00:00',
                'description': 'A fresh event'
            }
        ]
        scraper_func = Mock(return_value=raw_events)

        # Mock upsert
        self.mock_db.upsert_events.return_value = 1

        # Mock normalizer
        mock_normalizer = Mock()
        mock_normalizer.normalize.return_value = [
            NormalizedEvent(
                title='Fresh Event',
                event_date=datetime(2025, 10, 15),
                source_name='test',
                content_hash='abc',
                quality_score=80
            )
        ]
        mock_normalizer_class.return_value = mock_normalizer

        # Execute
        result = self.cache.get_or_fetch('test', scraper_func, ttl_hours=6)

        # Verify scraper was called
        scraper_func.assert_called_once()

        # Verify events were normalized and upserted
        self.mock_db.upsert_events.assert_called_once()

        # Verify we got the freshly cached data
        self.assertEqual(len(result), 1)

    def test_cache_miss_with_empty_scraper_result(self):
        """Test cache miss with scraper returning no events"""
        # Mock cache miss
        self.mock_db.get_cached_events.return_value = []

        # Mock scraper returning empty list
        scraper_func = Mock(return_value=[])

        # Execute
        result = self.cache.get_or_fetch('test', scraper_func)

        # Verify
        self.assertEqual(result, [])
        scraper_func.assert_called_once()
        self.mock_db.upsert_events.assert_not_called()

    def test_cache_ttl_configuration(self):
        """Test TTL is passed correctly"""
        # Mock cache hit
        self.mock_db.get_cached_events.return_value = [
            {'id': 1, 'scraped_at': datetime.now()}
        ]

        scraper_func = Mock()

        # Call with custom TTL
        self.cache.get_or_fetch('test', scraper_func, ttl_hours=12)

        # Verify TTL was passed to DB query
        self.mock_db.get_cached_events.assert_called_once_with('test', 12)

    def test_cache_error_handling(self):
        """Test error handling during cache fetch"""
        # Mock cache miss
        self.mock_db.get_cached_events.return_value = []

        # Mock scraper that raises error
        scraper_func = Mock(side_effect=Exception("Scraper failed"))

        # Execute and expect exception
        with self.assertRaises(Exception):
            self.cache.get_or_fetch('test', scraper_func)

    def test_invalidate_cache(self):
        """Test cache invalidation"""
        # Call invalidate
        self.cache.invalidate_cache('test')

        # Just verify it doesn't crash
        # (Full implementation would verify DELETE query)


if __name__ == '__main__':
    unittest.main()
