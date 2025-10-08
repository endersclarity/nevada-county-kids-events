#!/usr/bin/env python3
"""
Basic validation tests for KNCO evaluation script
Story: E1.1 - Evaluate KNCO RSS Feed

Note: This is a research/spike story, so tests are exploratory rather than comprehensive.
"""

import unittest
import os
import json
from evaluate_knco import (
    extract_guid_id,
    extract_metadata_from_description,
    parse_event,
    rate_scraping_difficulty
)


class TestGUIDExtraction(unittest.TestCase):
    """Test GUID ID extraction from Trumba format."""

    def test_extract_guid_standard_format(self):
        """Test extraction from standard Trumba GUID format."""
        guid = "http://uid.trumba.com/event/177609910"
        result = extract_guid_id(guid)
        self.assertEqual(result, "177609910")

    def test_extract_guid_different_id(self):
        """Test extraction with different numeric ID."""
        guid = "http://uid.trumba.com/event/123456789"
        result = extract_guid_id(guid)
        self.assertEqual(result, "123456789")

    def test_extract_guid_invalid_format(self):
        """Test handling of invalid GUID format."""
        guid = "http://example.com/other/12345"
        result = extract_guid_id(guid)
        # Should return original if pattern doesn't match
        self.assertEqual(result, guid)


class TestMetadataExtraction(unittest.TestCase):
    """Test metadata extraction from HTML descriptions."""

    def test_extract_with_nbsp(self):
        """Test extraction with &nbsp; encoding."""
        description = "<b>City/Area</b>:&nbsp;Nevada City<br/><b>Price</b>:&nbsp;Free"
        result = extract_metadata_from_description(description)
        self.assertEqual(result['city_area'], "Nevada City")
        self.assertEqual(result['price'], "Free")

    def test_extract_with_amp_nbsp(self):
        """Test extraction with &amp;nbsp; encoding."""
        description = "<b>City/Area</b>:&amp;nbsp;Grass Valley<br/><b>Price</b>:&amp;nbsp;$10"
        result = extract_metadata_from_description(description)
        self.assertEqual(result['city_area'], "Grass Valley")
        self.assertEqual(result['price'], "$10")

    def test_extract_age_range(self):
        """Test extraction of age range field."""
        description = "<b>Age</b>:&nbsp;3-5 years<br/><b>City/Area</b>:&nbsp;Nevada City"
        result = extract_metadata_from_description(description)
        self.assertEqual(result['age_range'], "3-5 years")

    def test_extract_venue(self):
        """Test extraction of venue field."""
        description = "<b>Venue</b>:&nbsp;Main Library<br/><b>Price</b>:&nbsp;Free"
        result = extract_metadata_from_description(description)
        self.assertEqual(result['venue'], "Main Library")

    def test_missing_fields_return_none(self):
        """Test that missing fields return None."""
        description = "<p>Just plain text with no structured metadata</p>"
        result = extract_metadata_from_description(description)
        self.assertIsNone(result['city_area'])
        self.assertIsNone(result['age_range'])
        self.assertIsNone(result['venue'])
        self.assertIsNone(result['price'])


class TestEventParsing(unittest.TestCase):
    """Test parsing of RSS feed entries."""

    def test_parse_event_basic(self):
        """Test parsing of basic event entry."""
        entry = {
            'title': 'Test Event',
            'description': '<b>City/Area</b>:&nbsp;Nevada City<br/><b>Price</b>:&nbsp;Free',
            'published': '2025-10-07',
            'link': 'https://example.com/event',
            'id': 'http://uid.trumba.com/event/12345',
            'summary': 'Test summary'
        }

        result = parse_event(entry)

        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['source_event_id'], '12345')
        self.assertEqual(result['city_area'], 'Nevada City')
        self.assertEqual(result['price'], 'Free')

    def test_parse_event_missing_optional_fields(self):
        """Test parsing when optional metadata is missing."""
        entry = {
            'title': 'Test Event',
            'description': 'Plain description',
            'published': '',
            'link': 'https://example.com/event',
            'id': 'http://uid.trumba.com/event/12345',
            'summary': ''
        }

        result = parse_event(entry)

        self.assertEqual(result['title'], 'Test Event')
        self.assertIsNone(result['city_area'])
        self.assertIsNone(result['venue'])


class TestScrapingDifficultyRating(unittest.TestCase):
    """Test scraping difficulty assessment."""

    def test_difficulty_rating_structure(self):
        """Test that difficulty rating returns expected structure."""
        result = rate_scraping_difficulty()

        self.assertIn('score', result)
        self.assertIn('scale', result)
        self.assertIn('justification', result)
        self.assertIn('challenges', result)

        # Check score is in valid range
        self.assertGreaterEqual(result['score'], 1)
        self.assertLessEqual(result['score'], 5)

        # Check lists are not empty
        self.assertGreater(len(result['justification']), 0)
        self.assertGreater(len(result['challenges']), 0)


class TestOutputFiles(unittest.TestCase):
    """Test that evaluation script generates expected output files."""

    def test_results_json_exists(self):
        """Test that results JSON file was created."""
        file_path = 'data/knco_evaluation_results.json'
        self.assertTrue(os.path.exists(file_path), f"Results file not found: {file_path}")

    def test_results_json_structure(self):
        """Test that results JSON has expected structure."""
        file_path = 'data/knco_evaluation_results.json'

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required keys
            required_keys = [
                'evaluation_date',
                'feed_url',
                'event_count',
                'completeness',
                'kid_relevance',
                'scraping_difficulty'
            ]

            for key in required_keys:
                self.assertIn(key, data, f"Missing key in results: {key}")

            # Check event count meets acceptance criteria (>= 50)
            self.assertGreaterEqual(
                data['event_count'],
                50,
                "Event count should be at least 50"
            )

    def test_sample_xml_exists(self):
        """Test that sample XML file was created."""
        file_path = 'data/samples/knco_sample.xml'
        self.assertTrue(os.path.exists(file_path), f"Sample XML not found: {file_path}")

    def test_sample_xml_not_empty(self):
        """Test that sample XML file is not empty."""
        file_path = 'data/samples/knco_sample.xml'

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            self.assertGreater(file_size, 0, "Sample XML file is empty")


if __name__ == '__main__':
    # Change to script directory for file path tests
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    unittest.main(verbosity=2)
