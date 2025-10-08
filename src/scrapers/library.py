"""Nevada County Library Scraper"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .base import BaseScraper
from ..config import Config

logger = logging.getLogger(__name__)

class LibraryScraper(BaseScraper):
    """
    Scraper for Nevada County Library events (Kids & Teens Calendar).

    Uses Selenium to handle JavaScript-rendered content.
    """

    EVENTS_URL = "https://nevadacountyca.gov/calendar.aspx?CID=81"

    def __init__(self):
        super().__init__("library")
        self._driver = None

    def _get_driver(self):
        """Get or create Selenium WebDriver instance."""
        if self._driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=chrome_options)
        return self._driver

    def __del__(self):
        """Clean up WebDriver on instance destruction."""
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse library events using Selenium.

        Returns:
            List of parsed event dictionaries
        """
        try:
            logger.info(f"Fetching events from {self.EVENTS_URL} (using Selenium)")
            driver = self._get_driver()
            driver.get(self.EVENTS_URL)

            import time
            wait = WebDriverWait(driver, 15)

            try:
                # Wait for list view link and click it
                list_tab = wait.until(
                    EC.presence_of_element_located((By.LINK_TEXT, "List"))
                )
                logger.debug("Found List tab, clicking it")
                list_tab.click()

                # Wait for list view to load
                time.sleep(2)
                wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "h3"))
                )
                logger.debug("List view loaded")
            except Exception as e:
                logger.warning(f"Could not switch to list view: {e}")
                time.sleep(3)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find calendar container
            calendar_div = soup.find('div', id='CID81')
            if not calendar_div:
                logger.warning("Could not find calendar container (CID81)")
                return []

            # Find all list items
            event_elements = calendar_div.find_all('li')

            if not event_elements:
                logger.warning("No event <li> elements found in calendar")
                return []

            logger.debug(f"Found {len(event_elements)} event <li> elements")

            events = self.parse(event_elements)
            logger.info(f"Successfully scraped {len(events)} events from Library")

            return events

        except Exception as e:
            logger.error(f"Error fetching library events: {e}")
            return []

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
        Parse a single event <li> element from Nevada County calendar list view.

        Structure:
        <li>
          <h3><span>Event Title</span></h3>
          <div class="subHeader">Date, Time @ Location</div>
          <p class="icalDescription">Description...</p>
        </li>
        """
        # Extract title from h3
        title_elem = element.find('h3')
        if not title_elem:
            return {}

        title = title_elem.get_text(strip=True)

        # Extract description from p.icalDescription
        desc_elem = element.find('p', class_='icalDescription')
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # Extract date/time/location from subHeader div
        # Format: "October 7, 2025, 10:30 AM - 10:45 AM @ Grass Valley Library"
        subheader_elem = element.find('div', class_='subHeader')
        if not subheader_elem:
            return {}

        subheader_text = subheader_elem.get_text(strip=True)

        # Split on @ to separate date/time from location
        parts = subheader_text.split('@')
        datetime_part = parts[0].strip() if len(parts) > 0 else ""
        venue = parts[1].strip() if len(parts) > 1 else ""

        # Parse date and time from datetime_part
        # Format: "October 7, 2025, 10:30 AM - 10:45 AM"
        event_date = ""
        time_range = ""

        if datetime_part:
            # Try to extract date
            date_match = re.search(r'(\w+\s+\d+,\s+\d{4})', datetime_part)
            if date_match:
                date_str = date_match.group(1)
                try:
                    dt = datetime.strptime(date_str, "%B %d, %Y")
                    event_date = dt.date().isoformat()
                except ValueError:
                    pass

            # Extract time range
            time_match = re.search(r'(\d{1,2}:\d{2}\s+[AP]M\s*-\s*\d{1,2}:\d{2}\s+[AP]M)', datetime_part)
            if time_match:
                time_range = time_match.group(1)

        # Extract link (if any)
        link_elem = element.find('a', href=True)
        source_url = link_elem.get('href', '') if link_elem else ""
        if source_url and not source_url.startswith('http'):
            source_url = f"https://nevadacountyca.gov{source_url}"

        source_event_id = self._extract_event_id(source_url)

        # Build event dictionary
        event = {
            'title': title,
            'description': description,
            'event_date': event_date,
            'time_range': time_range,
            'venue': venue,
            'city_area': 'Nevada County',
            'age_range': '',
            'price': None,
            'is_free': True,
            'source_url': source_url,
            'source_event_id': source_event_id,
            'categories': '',
        }

        return event

    def _extract_event_id(self, url: str) -> str:
        """Extract event ID from URL."""
        if not url:
            return ""

        # Nevada County calendar URLs: calendar.aspx?EID=12345
        match = re.search(r'[?&]EID=(\d+)', url)
        if match:
            return match.group(1)

        return ""
