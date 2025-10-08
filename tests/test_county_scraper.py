"""Unit tests for County scraper"""
import unittest
from pathlib import Path
from src.scrapers.county import CountyScraper


class TestCountyScraper(unittest.TestCase):
    """Test Nevada County calendar scraper"""

    @classmethod
    def setUpClass(cls):
        """Load sample iCal data"""
        sample_path = Path(__file__).parent.parent / "data" / "samples" / "county_sample.ics"
        with open(sample_path, 'r', encoding='utf-8') as f:
            cls.sample_ical = f.read()

    def test_parse_ical(self):
        """Test parsing iCal format"""
        scraper = CountyScraper()
        events = scraper._parse_ical(self.sample_ical)

        # Should have parsed 3 events
        self.assertEqual(len(events), 3, "Should parse 3 events from sample")

        # Check first event structure
        event = events[0]
        self.assertEqual(event['title'], 'Build, Make, Play')
        self.assertIn('Grass Valley Library', event['description'])
        self.assertEqual(event['event_date'], '2025-10-15')
        self.assertEqual(event['venue'], 'Grass Valley Library')
        self.assertEqual(event['source_event_id'], '12345@nevadacountyca.gov')

    def test_extract_ical_field(self):
        """Test iCal field extraction"""
        scraper = CountyScraper()

        block = """
        SUMMARY:Test Event
        DESCRIPTION:This is a test\, with comma
        LOCATION:Test Location
        """

        summary = scraper._extract_ical_field(block, 'SUMMARY')
        self.assertEqual(summary, 'Test Event')

        description = scraper._extract_ical_field(block, 'DESCRIPTION')
        self.assertEqual(description, 'This is a test, with comma')

        location = scraper._extract_ical_field(block, 'LOCATION')
        self.assertEqual(location, 'Test Location')

        # Non-existent field
        missing = scraper._extract_ical_field(block, 'NONEXISTENT')
        self.assertEqual(missing, '')

    def test_parse_ical_date(self):
        """Test iCal date parsing"""
        scraper = CountyScraper()

        # Full datetime format
        date1 = scraper._parse_ical_date('20251015T100000')
        self.assertEqual(date1, '2025-10-15')

        # Date-only format
        date2 = scraper._parse_ical_date('VALUE=DATE:20251020')
        self.assertEqual(date2, '2025-10-20')

        # Empty input
        date3 = scraper._parse_ical_date('')
        self.assertEqual(date3, '')

    def test_parse_ical_event(self):
        """Test parsing single iCal event"""
        scraper = CountyScraper()

        event_block = """
        UID:test123@example.com
        DTSTART:20251020T140000
        SUMMARY:Test Event
        DESCRIPTION:Test description
        LOCATION:Test Venue
        URL:https://example.com/event/123
        """

        event = scraper._parse_ical_event(event_block)

        self.assertEqual(event['title'], 'Test Event')
        self.assertEqual(event['description'], 'Test description')
        self.assertEqual(event['event_date'], '2025-10-20')
        self.assertEqual(event['venue'], 'Test Venue')
        self.assertEqual(event['source_event_id'], 'test123@example.com')
        self.assertEqual(event['source_url'], 'https://example.com/event/123')
        self.assertTrue(event['is_free'])

    def test_required_fields_present(self):
        """Test that all required fields are present"""
        scraper = CountyScraper()
        events = scraper._parse_ical(self.sample_ical)

        for event in events:
            # Required fields must exist
            self.assertIsNotNone(event.get('title'))
            self.assertIsNotNone(event.get('description'))
            self.assertIsNotNone(event.get('event_date'))
            self.assertIsNotNone(event.get('source_url'))
            self.assertIsNotNone(event.get('source_event_id'))
            # County events should be free
            self.assertTrue(event.get('is_free'))
            # Should have city_area set
            self.assertEqual(event.get('city_area'), 'Nevada County')

    def test_mixed_event_types(self):
        """Verify sample includes both kid-relevant and government events"""
        scraper = CountyScraper()
        events = scraper._parse_ical(self.sample_ical)

        titles = [e['title'] for e in events]

        # Kid-relevant events
        self.assertIn('Build, Make, Play', titles)
        self.assertIn('LEGO Club', titles)

        # Government event (low kid-relevance)
        self.assertIn('Board of Supervisors Meeting', titles)


if __name__ == '__main__':
    unittest.main()
