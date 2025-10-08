"""Nevada County Government Calendar Scraper"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..config import Config

logger = logging.getLogger(__name__)

class CountyScraper(BaseScraper):
    """
    Scraper for Nevada County government calendar.

    Uses iCal export if available, falls back to HTML scraping.
    Note: County calendar has lower kid-relevance (government meetings, etc.)
    """

    CALENDAR_URL = "https://www.nevadacountyca.gov/Calendar.aspx"
    # iCal subscription URL pattern (if available)
    ICAL_URL = "https://www.nevadacountyca.gov/icalendar.aspx"

    def __init__(self):
        super().__init__("county")

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse county calendar events.

        Returns:
            List of parsed event dictionaries
        """
        # Try iCal first (preferred method)
        try:
            logger.info("Attempting to fetch county calendar via iCal")
            events = self._fetch_ical()
            if events:
                logger.info(f"Successfully scraped {len(events)} events from County (iCal)")
                return events
        except Exception as e:
            logger.warning(f"iCal fetch failed, falling back to HTML: {e}")

        # Fallback to HTML scraping
        try:
            logger.info(f"Fetching county calendar from {self.CALENDAR_URL}")
            response = requests.get(
                self.CALENDAR_URL,
                timeout=Config.REQUEST_TIMEOUT,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find event elements (CivicEngage calendar buttons)
            event_elements = soup.find_all('button', {'class': lambda x: x and 'calendar' in x.lower()})

            if not event_elements:
                logger.warning("No event elements found on county calendar page")
                return []

            events = self.parse(event_elements)
            logger.info(f"Successfully scraped {len(events)} events from County (HTML)")

            return events

        except requests.Timeout:
            logger.error(f"Timeout fetching {self.CALENDAR_URL}")
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching county calendar: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in fetch: {e}")
            return []

    def _fetch_ical(self) -> List[Dict[str, Any]]:
        """
        Fetch events from iCal export (if available).

        Returns:
            List of event dictionaries
        """
        try:
            response = requests.get(
                self.ICAL_URL,
                timeout=Config.REQUEST_TIMEOUT,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()

            # Parse iCal format
            events = self._parse_ical(response.text)
            return events

        except Exception as e:
            logger.debug(f"iCal fetch error: {e}")
            raise

    def _parse_ical(self, ical_text: str) -> List[Dict[str, Any]]:
        """Parse iCal format into event dictionaries."""
        events = []

        # Simple iCal parser (VEVENT blocks)
        event_blocks = re.findall(r'BEGIN:VEVENT(.*?)END:VEVENT', ical_text, re.DOTALL)

        for block in event_blocks:
            try:
                event = self._parse_ical_event(block)
                if event and event.get('title'):
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing iCal event: {e}")
                continue

        return events

    def _parse_ical_event(self, event_block: str) -> Dict[str, Any]:
        """Parse a single iCal VEVENT block."""
        # Extract fields
        title = self._extract_ical_field(event_block, 'SUMMARY')
        description = self._extract_ical_field(event_block, 'DESCRIPTION')
        location = self._extract_ical_field(event_block, 'LOCATION')
        dtstart = self._extract_ical_field(event_block, 'DTSTART')
        dtend = self._extract_ical_field(event_block, 'DTEND')
        uid = self._extract_ical_field(event_block, 'UID')
        url = self._extract_ical_field(event_block, 'URL')

        # Parse date
        event_date = self._parse_ical_date(dtstart)

        # Build event dictionary
        event = {
            'title': title,
            'description': description or '',
            'event_date': event_date,
            'venue': location or '',
            'city_area': 'Nevada County',
            'age_range': '',  # County events rarely specify age range
            'price': None,
            'is_free': True,  # Government events are typically free
            'source_url': url or self.CALENDAR_URL,
            'source_event_id': uid or '',
        }

        return event

    def _extract_ical_field(self, block: str, field: str) -> str:
        """Extract a field value from iCal block."""
        pattern = rf'{field}[;:]([^\r\n]+)'
        match = re.search(pattern, block)
        if match:
            value = match.group(1).strip()
            # Remove iCal escaping
            value = value.replace('\\,', ',').replace('\\n', '\n').replace('\\\\', '\\')
            return value
        return ""

    def _parse_ical_date(self, dtstart: str) -> str:
        """Parse iCal date format to ISO date."""
        if not dtstart:
            return ""

        try:
            # iCal format: YYYYMMDDTHHMMSS or YYYYMMDD
            date_str = dtstart.split('VALUE=DATE:')[-1].split('T')[0]
            if len(date_str) == 8:
                dt = datetime.strptime(date_str, '%Y%m%d')
                return dt.date().isoformat()
        except Exception:
            pass

        return ""

    def parse(self, elements: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse HTML elements into structured event data.

        Args:
            elements: BeautifulSoup elements containing event data

        Returns:
            List of event dictionaries
        """
        events = []

        for element in elements:
            try:
                event = self._parse_element(element)
                if event and event.get('title'):
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing event element: {e}")
                continue

        return events

    def _parse_element(self, element: Any) -> Dict[str, Any]:
        """
        Parse a single event HTML button element.

        CivicEngage calendar buttons typically contain event title
        and may have data attributes with event info.
        """
        # Extract title from button text
        title = element.get_text(strip=True)

        # Remove date suffix pattern like " 08 202"
        title = re.sub(r'\s+\d{2}\s+\d{3}$', '', title)

        # Extract event ID from button attributes
        event_id = element.get('data-eventid') or element.get('id', '')

        # Build minimal event dictionary
        # (HTML scraping from calendar view has limited info)
        event = {
            'title': title,
            'description': '',
            'event_date': '',  # Would need to parse from calendar context
            'venue': '',
            'city_area': 'Nevada County',
            'age_range': '',
            'price': None,
            'is_free': True,
            'source_url': self.CALENDAR_URL,
            'source_event_id': event_id,
        }

        return event
