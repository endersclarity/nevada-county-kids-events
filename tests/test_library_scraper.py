"""Unit tests for Library scraper"""
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from src.scrapers.library import LibraryScraper


class TestLibraryScraper(unittest.TestCase):
    """Test Nevada County Library scraper"""

    @classmethod
    def setUpClass(cls):
        """Load sample HTML data"""
        sample_path = Path(__file__).parent.parent / "data" / "samples" / "library_sample.html"
        with open(sample_path, 'r', encoding='utf-8') as f:
            cls.sample_html = f.read()
        cls.soup = BeautifulSoup(cls.sample_html, 'html.parser')
        cls.event_elements = cls.soup.find_all('div', class_='s-lc-ea-e')

    def test_parse_elements(self):
        """Test parsing HTML elements"""
        scraper = LibraryScraper()
        events = scraper.parse(self.event_elements)

        # Should have parsed 3 events
        self.assertEqual(len(events), 3, "Should parse 3 events from sample")

        # Check first event structure
        event = events[0]
        self.assertEqual(event['title'], 'Stay & Play')
        self.assertIn('Caregivers', event['description'])
        self.assertEqual(event['event_date'], '2025-10-08')
        self.assertEqual(event['time_range'], '10:00 AM - 11:30 AM')
        self.assertIn('Madelyn Helling Library', event['venue'])
        self.assertEqual(event['source_event_id'], '14015157')

    def test_extract_event_id(self):
        """Test event ID extraction from URL"""
        scraper = LibraryScraper()

        # Test valid URL
        url = "/event/14015157"
        event_id = scraper._extract_event_id(url)
        self.assertEqual(event_id, "14015157")

        # Test full URL
        url = "https://nevadacountyca.libcal.com/event/14015200"
        event_id = scraper._extract_event_id(url)
        self.assertEqual(event_id, "14015200")

        # Test empty URL
        event_id = scraper._extract_event_id("")
        self.assertEqual(event_id, "")

    def test_extract_date(self):
        """Test date extraction"""
        scraper = LibraryScraper()

        text = "Date: Wednesday, October 8, 2025"
        date = scraper._extract_date(text)
        self.assertEqual(date, "2025-10-08")

        # Test with full event text
        text2 = "Date: Friday, October 10, 2025 Time: 3:00 PM"
        date2 = scraper._extract_date(text2)
        self.assertEqual(date2, "2025-10-10")

    def test_extract_time(self):
        """Test time range extraction"""
        scraper = LibraryScraper()

        text = "Time: 10:00 AM - 11:30 AM"
        time_range = scraper._extract_time(text)
        self.assertEqual(time_range, "10:00 AM - 11:30 AM")

        # Test with lowercase
        text2 = "time: 3:00 pm - 4:00 pm"
        time_range2 = scraper._extract_time(text2)
        self.assertEqual(time_range2, "3:00 pm - 4:00 pm")

    def test_extract_venue(self):
        """Test venue extraction"""
        scraper = LibraryScraper()

        text = "Location: Penn Valley Library Audience: Ages 5-10"
        venue = scraper._extract_venue(text)
        self.assertEqual(venue, "Penn Valley Library")

        # Test with longer venue name
        text2 = "Location: Gene Albaugh Community Room, Madelyn Helling Library Audience: Preschool"
        venue2 = scraper._extract_venue(text2)
        self.assertIn("Madelyn Helling Library", venue2)

    def test_extract_audience(self):
        """Test audience extraction"""
        scraper = LibraryScraper()

        text = "Audience: Ages 8-12 Categories: STEAM"
        audience = scraper._extract_audience(text)
        self.assertEqual(audience, "Ages 8-12")

        # Test multiple audiences
        text2 = "Audience: Preschool Babies Toddlers Categories: Storytime"
        audience2 = scraper._extract_audience(text2)
        self.assertIn("Preschool", audience2)
        self.assertIn("Babies", audience2)

    def test_extract_categories(self):
        """Test category extraction"""
        scraper = LibraryScraper()

        text = "Categories: STEAM Date: Wednesday"
        categories = scraper._extract_categories(text)
        self.assertEqual(categories, "STEAM")

        # Test with subcategory
        text2 = "Categories: Storytime > Stay & Play Date: Friday"
        categories2 = scraper._extract_categories(text2)
        self.assertIn("Storytime", categories2)

    def test_required_fields_present(self):
        """Test that all required fields are present"""
        scraper = LibraryScraper()
        events = scraper.parse(self.event_elements)

        for event in events:
            # Required fields must exist
            self.assertIsNotNone(event.get('title'))
            self.assertIsNotNone(event.get('description'))
            self.assertIsNotNone(event.get('event_date'))
            self.assertIsNotNone(event.get('source_url'))
            self.assertIsNotNone(event.get('source_event_id'))
            # Library events should be free
            self.assertTrue(event.get('is_free'))
            # Should have city_area set
            self.assertEqual(event.get('city_area'), 'Nevada County')

    def test_all_events_have_kid_relevance(self):
        """Verify sample events are kid-focused"""
        scraper = LibraryScraper()
        events = scraper.parse(self.event_elements)

        for event in events:
            # All sample events should have kid-relevant audiences
            audience = event.get('age_range', '').lower()
            self.assertTrue(
                any(kid_term in audience for kid_term in ['ages', 'preschool', 'babies', 'toddlers', 'tweens']),
                f"Event '{event['title']}' should have kid-relevant audience"
            )


if __name__ == '__main__':
    unittest.main()
