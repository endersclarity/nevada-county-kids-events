"""Unit tests for Supabase client"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.storage.supabase import SupabaseClient
from src.processors.normalizer import NormalizedEvent


class TestSupabaseClient(unittest.TestCase):
    """Test Supabase client"""

    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_connection(self, mock_connect, mock_config):
        """Test database connection"""
        mock_config.SUPABASE_URL = "https://test-project.supabase.co"
        mock_config.SUPABASE_KEY = "test-key"

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        client = SupabaseClient()

        self.assertIsNotNone(client.conn)
        mock_connect.assert_called_once()

    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_missing_credentials(self, mock_connect, mock_config):
        """Test error when credentials are missing"""
        mock_config.SUPABASE_URL = None
        mock_config.SUPABASE_KEY = None

        with self.assertRaises(ValueError):
            SupabaseClient()

    @patch('src.storage.supabase.execute_values')
    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_upsert_events(self, mock_connect, mock_config, mock_execute_values):
        """Test upserting events"""
        mock_config.SUPABASE_URL = "https://test-project.supabase.co"
        mock_config.SUPABASE_KEY = "test-key"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = SupabaseClient()

        # Create test events
        events = [
            NormalizedEvent(
                title="Test Event",
                event_date=datetime(2025, 10, 15),
                source_name="test",
                content_hash="abc123",
                quality_score=80
            )
        ]

        result = client.upsert_events(events)

        self.assertEqual(result, 1)
        mock_execute_values.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_upsert_empty_list(self, mock_connect, mock_config):
        """Test upserting empty list"""
        mock_config.SUPABASE_URL = "https://test-project.supabase.co"
        mock_config.SUPABASE_KEY = "test-key"

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        client = SupabaseClient()
        result = client.upsert_events([])

        self.assertEqual(result, 0)

    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_get_cached_events(self, mock_connect, mock_config):
        """Test retrieving cached events"""
        mock_config.SUPABASE_URL = "https://test-project.supabase.co"
        mock_config.SUPABASE_KEY = "test-key"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock query results
        mock_cursor.fetchall.return_value = [
            (
                1, 'Test Event', 'Description', datetime(2025, 10, 15),
                'Venue', 'Nevada City', 'test', 'http://example.com',
                '12345', 'hash123', 'All Ages', 'Free', True, 90,
                datetime(2025, 10, 7)
            )
        ]

        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = SupabaseClient()
        events = client.get_cached_events('test', ttl_hours=6)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['title'], 'Test Event')
        self.assertEqual(events[0]['source_name'], 'test')

    @patch('src.storage.supabase.Config')
    @patch('src.storage.supabase.psycopg2.connect')
    def test_context_manager(self, mock_connect, mock_config):
        """Test using client as context manager"""
        mock_config.SUPABASE_URL = "https://test-project.supabase.co"
        mock_config.SUPABASE_KEY = "test-key"

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with SupabaseClient() as client:
            self.assertIsNotNone(client)

        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
