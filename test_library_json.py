#!/usr/bin/env python3
"""Test library scraper and output JSON"""
import json
from src.scrapers.library import LibraryScraper

scraper = LibraryScraper()
events = scraper.fetch()

output = {
    'total_events': len(events),
    'sample_events': events[:5]
}

# Write to file with UTF-8 encoding
with open('data/debug/library_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Scraped {len(events)} events")
print("Results written to: data/debug/library_test_results.json")
