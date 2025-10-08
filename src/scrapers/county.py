"""Nevada County Government Calendar Scraper"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar
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
    # iCal feed URL (Main Calendar - all county events)
    ICAL_URL = "https://www.nevadacountyca.gov/common/modules/iCalendar/iCalendar.aspx?catID=14&feed=calendar"

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
        """Parse iCal format using icalendar library."""
        events = []

        try:
            cal = Calendar.from_ical(ical_text)

            for component in cal.walk('VEVENT'):
                try:
                    event = self._parse_ical_event(component)
                    if event and event.get('title'):
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing iCal event: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing iCal calendar: {e}")

        return events

    def _parse_ical_event(self, vevent) -> Dict[str, Any]:
        """Parse a single iCal VEVENT component."""
        # Extract fields
        title = str(vevent.get('SUMMARY', ''))
        description = str(vevent.get('DESCRIPTION', ''))
        location = str(vevent.get('LOCATION', ''))
        uid = str(vevent.get('UID', ''))

        # Parse date
        event_date = ''
        dtstart = vevent.get('DTSTART')
        if dtstart:
            try:
                dt = dtstart.dt
                if hasattr(dt, 'date'):
                    event_date = dt.date().isoformat()
                else:
                    event_date = dt.isoformat()
            except Exception as e:
                logger.debug(f"Error parsing date: {e}")

        # Clean up description (remove HTML tags and extra whitespace)
        description = re.sub(r'<[^>]+>', ' ', description)
        description = re.sub(r'\s+', ' ', description).strip()

        # Clean up location (remove HTML tags)
        location = re.sub(r'<[^>]+>', ' ', location)
        location = re.sub(r'\s+', ' ', location).strip()

        # Build event dictionary
        event = {
            'title': title,
            'description': description[:500] if description else '',  # Limit description length
            'event_date': event_date,
            'venue': location[:200] if location else '',  # Limit venue length
            'city_area': 'Nevada County',
            'age_range': '',  # County events rarely specify age range
            'price': None,
            'is_free': True,  # Government events are typically free
            'source_url': self.CALENDAR_URL,
            'source_event_id': uid,
        }

        return event

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
