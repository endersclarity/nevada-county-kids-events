"""KNCO Trumba RSS Scraper"""
import re
import logging
from typing import List, Dict, Any
import requests
import feedparser
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..config import Config

logger = logging.getLogger(__name__)

class KNCOScraper(BaseScraper):
    """Scraper for KNCO Trumba RSS feed"""

    RSS_URL = "https://www.trumba.com/calendars/KNCO.rss"

    def __init__(self):
        super().__init__("knco")

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse KNCO RSS feed.

        Returns:
            List of parsed event dictionaries
        """
        try:
            logger.info(f"Fetching RSS feed from {self.RSS_URL}")
            response = requests.get(
                self.RSS_URL,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            # Parse RSS with feedparser
            feed = feedparser.parse(response.content)

            if not feed.entries:
                logger.warning("No entries found in RSS feed")
                return []

            events = self.parse(feed.entries)
            logger.info(f"Successfully scraped {len(events)} events from KNCO")

            return events

        except requests.Timeout:
            logger.error(f"Timeout fetching {self.RSS_URL}")
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in fetch: {e}")
            return []

    def parse(self, entries: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse RSS entries into structured event data.

        Args:
            entries: Feedparser entry objects

        Returns:
            List of event dictionaries
        """
        events = []

        for entry in entries:
            try:
                event = self._parse_entry(entry)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing entry '{entry.get('title', 'Unknown')}': {e}")
                continue

        return events

    def _parse_entry(self, entry: Any) -> Dict[str, Any]:
        """Parse a single RSS entry."""
        # Extract basic fields
        title = entry.get('title', '').strip()
        description_html = entry.get('description', '')
        link = entry.get('link', '')
        guid = entry.get('guid', '')

        # Parse date from published or category
        event_date = self._extract_date(entry)

        # Extract source_event_id from GUID
        source_event_id = self._extract_event_id(guid)

        # Parse HTML description
        parsed_data = self._parse_description_html(description_html)

        # Build event dictionary
        event = {
            'title': title,
            'description': parsed_data.get('description', ''),
            'event_date': event_date,
            'venue': parsed_data.get('venue'),
            'city_area': parsed_data.get('city_area'),
            'age_range': parsed_data.get('age_range'),
            'price': parsed_data.get('price'),
            'is_free': parsed_data.get('is_free', False),
            'source_url': link,
            'source_event_id': source_event_id,
        }

        return event

    def _extract_event_id(self, guid: str) -> str:
        """Extract event ID from GUID like 'http://uid.trumba.com/event/177609910'"""
        if not guid:
            return ""

        match = re.search(r'event/(\d+)', guid)
        if match:
            return match.group(1)

        return guid

    def _extract_date(self, entry: Any) -> str:
        """Extract event date from entry (use category field or description)"""
        from datetime import datetime

        # Try published date first
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6])
            return dt.isoformat()

        # Try category field (Trumba format: "2025/10/07 (Tue)")
        category = entry.get('category', '')
        if category:
            # Extract date portion before parentheses
            date_match = re.search(r'(\d{4}/\d{2}/\d{2})', category)
            if date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), '%Y/%m/%d')
                    return dt.isoformat()
                except ValueError:
                    pass

        # Try extracting from description (e.g., "Tuesday, October 7, 2025, 11am")
        description = entry.get('description', '')
        # Look for patterns like "October 7, 2025" or "Oct 7, 2025"
        date_patterns = [
            r'(\w+day,?\s+\w+\s+\d{1,2},?\s+\d{4})',  # "Tuesday, October 7, 2025"
            r'(\w+\s+\d{1,2},?\s+\d{4})',  # "October 7, 2025"
        ]
        for pattern in date_patterns:
            match = re.search(pattern, description)
            if match:
                date_str = match.group(1)
                # Try parsing with various formats
                for fmt in ['%A, %B %d, %Y', '%A %B %d, %Y', '%B %d, %Y', '%b %d, %Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.isoformat()
                    except ValueError:
                        continue

        # Fallback to empty string (normalizer will filter these out)
        return ""

    def _parse_description_html(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML description to extract metadata fields.

        Args:
            html: HTML description string

        Returns:
            Dictionary with extracted fields
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove images and links for clean text
        for tag in soup.find_all(['img', 'a']):
            tag.decompose()

        # Get clean text
        text = soup.get_text(separator=' ', strip=True)

        # Handle HTML entities
        text = text.replace('&nbsp;', ' ')
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        # Extract structured metadata using regex
        data = {
            'description': text[:500],  # First 500 chars as description
            'city_area': self._extract_field(text, r'City/Area\s*:\s*([^<\n]+)'),
            'age_range': self._extract_field(text, r'Age range\s*:\s*([^<\n]+)'),
            'price': self._extract_field(text, r'Price\s*:\s*([^<\n]+)'),
            'venue': self._extract_field(text, r'Event location\s*:\s*([^<\n]+)'),
        }

        # Determine if free
        price = data.get('price', '').lower()
        data['is_free'] = 'free' in price or '$0' in price

        return data

    def _extract_field(self, text: str, pattern: str) -> str:
        """Extract a single field using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Stop at next field label (matches pattern like "Age range :" or "Price :")
            value = re.split(r'\s+(?:[A-Z][a-z]+(?:\s+[a-z]+)*\s*:)', value)[0]
            # Clean up common artifacts
            value = re.sub(r'\s+', ' ', value).strip()
            return value
        return ""
