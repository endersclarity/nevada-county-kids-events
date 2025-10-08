"""Integration tests for orchestrator"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
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


if __name__ == '__main__':
    unittest.main()
