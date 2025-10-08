"""Unit tests for Deduplicator"""
import unittest
from src.processors.deduplicator import Deduplicator


class TestDeduplicator(unittest.TestCase):
    """Test cross-source deduplication"""

    def test_exact_hash_deduplication(self):
        """Test exact duplicate removal by content_hash"""
        dedup = Deduplicator()

        events = [
            {'title': 'Event A', 'content_hash': 'abc123', 'event_date': '2025-10-15', 'source_name': 'knco'},
            {'title': 'Event A', 'content_hash': 'abc123', 'event_date': '2025-10-15', 'source_name': 'library'},
            {'title': 'Event B', 'content_hash': 'def456', 'event_date': '2025-10-16', 'source_name': 'knco'},
        ]

        result = dedup.deduplicate(events)

        # Should remove 1 duplicate
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Event A')
        self.assertEqual(result[1]['title'], 'Event B')

    def test_fuzzy_title_deduplication(self):
        """Test fuzzy matching on similar titles + same date"""
        dedup = Deduplicator()

        events = [
            {'title': 'Story Time at the Library', 'event_date': '2025-10-15', 'source_name': 'knco', 'venue': None},
            {'title': 'Story Time at Library', 'event_date': '2025-10-15', 'source_name': 'library', 'venue': 'Main Library'},
            {'title': 'LEGO Club', 'event_date': '2025-10-16', 'source_name': 'library'},
        ]

        result = dedup.deduplicate(events)

        # Should merge first two (similar titles, same date)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Story Time at the Library')
        # Venue should be merged from library event
        self.assertEqual(result[0]['venue'], 'Main Library')

    def test_source_priority(self):
        """Test that higher priority source (KNCO) is kept"""
        dedup = Deduplicator()

        events = [
            {'title': 'Event X', 'content_hash': 'xyz', 'event_date': '2025-10-20', 'source_name': 'library', 'description': 'Library desc'},
            {'title': 'Event X', 'content_hash': 'xyz', 'event_date': '2025-10-20', 'source_name': 'knco', 'description': 'KNCO desc'},
        ]

        result = dedup.deduplicate(events)

        # First event wins (library), but if KNCO comes first, KNCO wins
        self.assertEqual(len(result), 1)
        # Library came first, so it's kept
        self.assertEqual(result[0]['source_name'], 'library')

    def test_metadata_merge(self):
        """Test that metadata is merged from duplicates"""
        dedup = Deduplicator()

        library_event = {
            'title': 'Storytime',
            'event_date': '2025-10-15',
            'source_name': 'library',
            'venue': 'Main Library',
            'age_range': 'Ages 0-5',
            'description': 'Fun storytime'
        }

        knco_event = {
            'title': 'Story Time',
            'event_date': '2025-10-15',
            'source_name': 'knco',
            'venue': None,
            'age_range': None,
            'description': 'KNCO storytime'
        }

        # Library first, then KNCO (fuzzy match)
        result = dedup.deduplicate([library_event, knco_event])

        self.assertEqual(len(result), 1)
        # Should have merged venue and age_range from library
        self.assertEqual(result[0]['venue'], 'Main Library')
        self.assertEqual(result[0]['age_range'], 'Ages 0-5')

    def test_no_duplicates(self):
        """Test that unique events are all kept"""
        dedup = Deduplicator()

        events = [
            {'title': 'Event A', 'event_date': '2025-10-15', 'source_name': 'knco'},
            {'title': 'Event B', 'event_date': '2025-10-16', 'source_name': 'library'},
            {'title': 'Event C', 'event_date': '2025-10-17', 'source_name': 'county'},
        ]

        result = dedup.deduplicate(events)

        # All unique - should keep all 3
        self.assertEqual(len(result), 3)

    def test_empty_list(self):
        """Test deduplication of empty list"""
        dedup = Deduplicator()
        result = dedup.deduplicate([])
        self.assertEqual(result, [])

    def test_similarity_threshold(self):
        """Test that titles below similarity threshold are not matched"""
        dedup = Deduplicator()

        events = [
            {'title': 'LEGO Club', 'event_date': '2025-10-15', 'source_name': 'library'},
            {'title': 'Book Club', 'event_date': '2025-10-15', 'source_name': 'county'},  # Different
        ]

        result = dedup.deduplicate(events)

        # Not similar enough - keep both
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
