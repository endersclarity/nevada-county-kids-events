#!/usr/bin/env python3
"""
Scrape Nevada County Library events calendar
Target: https://nevadacountyca.gov/calendar.aspx?CID=81 (Kids & Teens)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import sys

def scrape_library_calendar(url="https://nevadacountyca.gov/calendar.aspx?CID=81"):
    """Scrape Nevada County Library Kids & Teens calendar"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        events = []

        # Find all event entries (adjust selectors based on actual HTML structure)
        event_items = soup.find_all('div', class_='event') or soup.find_all('tr', class_='event')

        if not event_items:
            # Try alternative selectors
            event_items = soup.select('.catAgendaRow, .EventList, [class*="event"]')

        for item in event_items:
            try:
                event = {}

                # Extract title
                title_elem = item.find(['h2', 'h3', 'h4', 'a', 'span'], class_=lambda x: x and 'title' in x.lower() if x else False)
                event['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'

                # Extract date/time
                date_elem = item.find(['span', 'div', 'td'], class_=lambda x: x and 'date' in x.lower() if x else False)
                event['date'] = date_elem.get_text(strip=True) if date_elem else 'N/A'

                time_elem = item.find(['span', 'div', 'td'], class_=lambda x: x and 'time' in x.lower() if x else False)
                event['time'] = time_elem.get_text(strip=True) if time_elem else 'N/A'

                # Extract location
                location_elem = item.find(['span', 'div', 'td'], class_=lambda x: x and 'location' in x.lower() if x else False)
                event['location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'

                # Extract description
                desc_elem = item.find(['p', 'div', 'span'], class_=lambda x: x and ('desc' in x.lower() or 'detail' in x.lower()) if x else False)
                event['description'] = desc_elem.get_text(strip=True) if desc_elem else 'N/A'

                # Extract age range if available
                age_elem = item.find(text=lambda x: x and ('age' in x.lower() or 'year' in x.lower()))
                event['age_range'] = age_elem.strip() if age_elem else 'Not specified'

                events.append(event)

            except Exception as e:
                print(f"Error parsing event: {e}", file=sys.stderr)
                continue

        # Save raw HTML snippet for debugging
        with open('../data/samples/library_sample.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify()[:5000])  # First 5000 chars of formatted HTML

        # If no events found with structured parsing, try raw text extraction
        if not events or all(e['title'] == 'N/A' for e in events):
            print("No structured events found. Trying alternative parsing...", file=sys.stderr)
            # Alternative: look for table rows or list items
            alt_events = soup.select('tr.catAgendaRow, tr[class*="event"], li.event-item')
            print(f"Found {len(alt_events)} alternative event candidates", file=sys.stderr)

            if not alt_events:
                return {
                    'events': [],
                    'raw_html_saved': True,
                    'html_preview': soup.get_text()[:1000]
                }

        return {
            'source': 'Nevada County Library - Kids & Teens Calendar',
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'total_events': len(events),
            'events': events[:25]  # Limit to 25 events
        }

    except Exception as e:
        return {
            'error': str(e),
            'url': url
        }

if __name__ == '__main__':
    result = scrape_library_calendar()
    print(json.dumps(result, indent=2))
