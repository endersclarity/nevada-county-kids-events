"""Unit tests for data normalizer"""
import unittest
from datetime import datetime
from src.processors.normalizer import Normalizer, NormalizedEvent


class TestNormalizer(unittest.TestCase):
    """Test data normalizer"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = Normalizer("test_source")

    def test_normalize_valid_event(self):
        """Test normalizing a valid event"""
        events = [{
            'title': 'Test Event',
            'description': 'A test event description',
            'event_date': '2025-10-15T10:00:00',
            'venue': 'Test Venue',
            'city_area': 'Nevada City',
            'age_range': 'All Ages',
            'price': 'Free',
            'is_free': True,
            'source_url': 'http://example.com',
            'source_event_id': '12345'
        }]

        normalized = self.normalizer.normalize(events)

        self.assertEqual(len(normalized), 1)
        event = normalized[0]

        self.assertIsInstance(event, NormalizedEvent)
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.source_name, 'test_source')
        self.assertIsNotNone(event.content_hash)
        self.assertGreater(event.quality_score, 0)

    def test_validate_required_fields(self):
        """Test validation catches missing required fields"""
        # Missing title
        events1 = [{'event_date': '2025-10-15'}]
        normalized1 = self.normalizer.normalize(events1)
        self.assertEqual(len(normalized1), 0)

        # Missing event_date
        events2 = [{'title': 'Test'}]
        normalized2 = self.normalizer.normalize(events2)
        self.assertEqual(len(normalized2), 0)

    def test_parse_date_formats(self):
        """Test parsing various date formats"""
        # ISO 8601
        date1 = self.normalizer._parse_date('2025-10-15T10:00:00')
        self.assertIsInstance(date1, datetime)

        # Simple date
        date2 = self.normalizer._parse_date('2025-10-15')
        self.assertIsInstance(date2, datetime)

        # Invalid date
        date3 = self.normalizer._parse_date('invalid')
        self.assertIsNone(date3)

        # Empty string
        date4 = self.normalizer._parse_date('')
        self.assertIsNone(date4)

    def test_content_hash_generation(self):
        """Test content hash is generated and consistent"""
        title = "Test Event"
        date = datetime(2025, 10, 15)
        desc = "Description"

        hash1 = self.normalizer._generate_content_hash(title, date, desc)
        hash2 = self.normalizer._generate_content_hash(title, date, desc)

        # Same input should produce same hash
        self.assertEqual(hash1, hash2)

        # Different input should produce different hash
        hash3 = self.normalizer._generate_content_hash("Different", date, desc)
        self.assertNotEqual(hash1, hash3)

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        # Minimal event (title + date only)
        score1 = self.normalizer._calculate_quality_score(
            title="Test",
            event_date=datetime(2025, 10, 15),
            description=None,
            venue=None,
            age_range=None,
            price=None
        )
        self.assertEqual(score1, 40)  # 20 + 20

        # Complete event with short description
        score2 = self.normalizer._calculate_quality_score(
            title="Test",
            event_date=datetime(2025, 10, 15),
            description="Short",
            venue="Venue",
            age_range="All Ages",
            price="Free"
        )
        self.assertEqual(score2, 90)  # 20 + 20 + 20 + 10 + 10 + 10

        # Complete event with long description
        score3 = self.normalizer._calculate_quality_score(
            title="Test",
            event_date=datetime(2025, 10, 15),
            description="A" * 100,  # Long description
            venue="Venue",
            age_range="All Ages",
            price="Free"
        )
        self.assertEqual(score3, 100)  # 20 + 20 + 20 + 10 + 10 + 10 + 10

    def test_quality_score_boundaries(self):
        """Test quality score never exceeds 100"""
        score = self.normalizer._calculate_quality_score(
            title="Test",
            event_date=datetime(2025, 10, 15),
            description="A" * 500,
            venue="Venue",
            age_range="All Ages",
            price="Free"
        )
        self.assertLessEqual(score, 100)

    def test_normalize_multiple_events(self):
        """Test normalizing multiple events"""
        events = [
            {
                'title': 'Event 1',
                'event_date': '2025-10-15',
                'description': 'First event'
            },
            {
                'title': 'Event 2',
                'event_date': '2025-10-16',
                'description': 'Second event'
            },
            {
                'title': '',  # Invalid - missing title
                'event_date': '2025-10-17'
            }
        ]

        normalized = self.normalizer.normalize(events)

        # Should have 2 valid events (third is invalid)
        self.assertEqual(len(normalized), 2)

    def test_to_dict_conversion(self):
        """Test NormalizedEvent to dictionary conversion"""
        event = NormalizedEvent(
            title="Test",
            event_date=datetime(2025, 10, 15, 10, 0, 0),
            source_name="test",
            content_hash="abc123",
            quality_score=80,
            description="Test description"
        )

        data = event.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['title'], 'Test')
        self.assertIsInstance(data['event_date'], str)  # Should be ISO format
        self.assertIn('2025-10-15', data['event_date'])

    def test_quality_filtering(self):
        """Test quality score filtering"""
        events = [
            {
                'title': 'High Quality Event',
                'event_date': '2025-10-15',
                'description': 'A' * 100,  # Long description
                'venue': 'Test Venue',
                'age_range': '5-12',
                'price': 'Free'
            },
            {
                'title': 'Low Quality Event',
                'event_date': '2025-10-16',
                # No other fields
            }
        ]

        # Filter events with score < 50
        normalized = self.normalizer.normalize(events, min_quality_score=50, log_quality_stats=False)

        # Should only get the high-quality event
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0].title, 'High Quality Event')

    def test_quality_stats_logging(self):
        """Test quality statistics logging"""
        events = [
            {
                'title': f'Event {i}',
                'event_date': f'2025-10-{15+i}',
                'description': 'A' * 100 if i % 3 == 0 else 'Short',
                'venue': 'Venue' if i % 2 == 0 else None,
                'age_range': '5-12' if i % 2 == 1 else None,
                'price': 'Free' if i % 3 == 0 else None
            }
            for i in range(10)
        ]

        # This should log quality stats
        normalized = self.normalizer.normalize(events, log_quality_stats=True)

        # All events should be normalized
        self.assertEqual(len(normalized), 10)

        # Verify all have quality scores
        for event in normalized:
            self.assertGreaterEqual(event.quality_score, 0)
            self.assertLessEqual(event.quality_score, 100)

    def test_quality_tiers(self):
        """Test quality tier categorization"""
        # High quality (80-100)
        high_quality_events = [{
            'title': 'High Quality',
            'event_date': '2025-10-15',
            'description': 'A' * 100,
            'venue': 'Venue',
            'age_range': '5-12',
            'price': 'Free'
        }]
        high_normalized = self.normalizer.normalize(high_quality_events, log_quality_stats=False)
        self.assertGreaterEqual(high_normalized[0].quality_score, 80)

        # Medium quality (50-79)
        medium_quality_events = [{
            'title': 'Medium Quality',
            'event_date': '2025-10-15',
            'description': 'Short description',
            'venue': 'Venue'
        }]
        medium_normalized = self.normalizer.normalize(medium_quality_events, log_quality_stats=False)
        self.assertGreaterEqual(medium_normalized[0].quality_score, 50)
        self.assertLess(medium_normalized[0].quality_score, 80)

        # Low quality (0-49)
        low_quality_events = [{
            'title': 'Low Quality',
            'event_date': '2025-10-15',
        }]
        low_normalized = self.normalizer.normalize(low_quality_events, log_quality_stats=False)
        self.assertLess(low_normalized[0].quality_score, 50)


if __name__ == '__main__':
    unittest.main()
