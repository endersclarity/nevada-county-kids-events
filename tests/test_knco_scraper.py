"""Unit tests for KNCO scraper"""
import unittest
from pathlib import Path
import feedparser
from src.scrapers.knco import KNCOScraper


class TestKNCOScraper(unittest.TestCase):
    """Test KNCO RSS scraper"""

    @classmethod
    def setUpClass(cls):
        """Load sample RSS data"""
        sample_path = Path(__file__).parent.parent / "data" / "samples" / "knco_sample.xml"
        with open(sample_path, 'r', encoding='utf-8') as f:
            cls.sample_xml = f.read()
        cls.feed = feedparser.parse(cls.sample_xml)

    def test_parse_entries(self):
        """Test parsing RSS entries"""
        scraper = KNCOScraper()
        events = scraper.parse(self.feed.entries)

        # Should have parsed events
        self.assertGreater(len(events), 0, "Should parse at least one event")

        # Check first event structure
        event = events[0]
        self.assertIn('title', event)
        self.assertIn('description', event)
        self.assertIn('event_date', event)
        self.assertIn('source_url', event)
        self.assertIn('source_event_id', event)

    def test_extract_event_id(self):
        """Test event ID extraction from GUID"""
        scraper = KNCOScraper()

        # Test valid GUID
        guid = "http://uid.trumba.com/event/177609910"
        event_id = scraper._extract_event_id(guid)
        self.assertEqual(event_id, "177609910")

        # Test empty GUID
        event_id = scraper._extract_event_id("")
        self.assertEqual(event_id, "")

    def test_parse_description_html(self):
        """Test HTML description parsing"""
        scraper = KNCOScraper()

        html = """
        <b>City/Area</b>:&nbsp;Nevada City<br/>
        <b>Age range</b>:&nbsp;All Ages<br/>
        <b>Price</b>:&nbsp;free - donations welcome<br/>
        """

        data = scraper._parse_description_html(html)

        self.assertEqual(data['city_area'], 'Nevada City')
        self.assertEqual(data['age_range'], 'All Ages')
        self.assertIn('free', data['price'].lower())
        self.assertTrue(data['is_free'])

    def test_parse_price_variations(self):
        """Test various price formats"""
        scraper = KNCOScraper()

        # Free event
        html1 = "<b>Price</b>:&nbsp;FREE<br/>"
        data1 = scraper._parse_description_html(html1)
        self.assertTrue(data1['is_free'])

        # Paid event
        html2 = "<b>Price</b>:&nbsp;$15<br/>"
        data2 = scraper._parse_description_html(html2)
        self.assertFalse(data2['is_free'])

    def test_required_fields_present(self):
        """Test that all required fields are present"""
        scraper = KNCOScraper()
        events = scraper.parse(self.feed.entries[:5])  # Test first 5 events

        for event in events:
            # Required fields must exist (can be empty string)
            self.assertIsNotNone(event.get('title'))
            self.assertIsNotNone(event.get('description'))
            self.assertIsNotNone(event.get('event_date'))
            self.assertIsNotNone(event.get('source_url'))
            self.assertIsNotNone(event.get('source_event_id'))


if __name__ == '__main__':
    unittest.main()
