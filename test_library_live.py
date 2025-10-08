#!/usr/bin/env python3
"""
Quick test script for library scraper with live data
"""
import sys
import logging
from src.scrapers.library import LibraryScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("Testing Library Scraper with live data...")
    print(f"Target URL: {LibraryScraper.EVENTS_URL}")
    print("-" * 60)

    scraper = LibraryScraper()
    events = scraper.fetch()

    print(f"\nSuccessfully scraped {len(events)} events")
    print("-" * 60)

    if events:
        print("\nFirst 3 events:")
        for i, event in enumerate(events[:3], 1):
            print(f"\n{i}. {event.get('title', 'No title')}")
            print(f"   Date: {event.get('event_date', 'N/A')}")
            print(f"   Time: {event.get('time_range', 'N/A')}")
            print(f"   Venue: {event.get('venue', 'N/A')}")
            print(f"   Age: {event.get('age_range', 'N/A')}")
            print(f"   URL: {event.get('source_url', 'N/A')}")
    else:
        print("\n⚠ No events found!")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
