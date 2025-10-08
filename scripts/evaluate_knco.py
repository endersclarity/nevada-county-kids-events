#!/usr/bin/env python3
"""
KNCO RSS Feed Evaluation Script
Story: E1.1 - Evaluate KNCO RSS Feed

Quick-and-dirty script to fetch, parse, and analyze KNCO Trumba RSS feed.
"""

import feedparser
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any
import random

# KNCO RSS Feed URL
KNCO_RSS_URL = "https://www.trumba.com/calendars/KNCO.rss"


def fetch_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch RSS feed from URL."""
    print(f"Fetching RSS feed from: {url}")
    feed = feedparser.parse(url)
    if feed.bozo:
        print(f"Warning: Feed has parsing issues: {feed.bozo_exception}")
    return feed


def extract_guid_id(guid: str) -> str:
    """Extract numeric ID from Trumba GUID format.

    Example: http://uid.trumba.com/event/177609910 → 177609910
    """
    match = re.search(r'event/(\d+)', guid)
    return match.group(1) if match else guid


def extract_metadata_from_description(description: str) -> Dict[str, Any]:
    """Extract structured metadata from HTML-formatted description.

    Handles both &nbsp; and &amp;nbsp; entity variations.
    """
    metadata = {
        'city_area': None,
        'age_range': None,
        'venue': None,
        'price': None,
        'category': None
    }

    # Parse HTML
    soup = BeautifulSoup(description, 'html.parser')

    # Define patterns for both entity encodings
    patterns = {
        'city_area': [
            re.compile(r'<b>City/Area</b>:\s*(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>City/Area</b>:&nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>City/Area</b>:&amp;nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
        ],
        'age_range': [
            re.compile(r'<b>Age</b>:\s*(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Age</b>:&nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Age</b>:&amp;nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
        ],
        'venue': [
            re.compile(r'<b>Venue</b>:\s*(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Venue</b>:&nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Venue</b>:&amp;nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
        ],
        'price': [
            re.compile(r'<b>Price</b>:\s*(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Price</b>:&nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Price</b>:&amp;nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
        ],
        'category': [
            re.compile(r'<b>Category</b>:\s*(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Category</b>:&nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
            re.compile(r'<b>Category</b>:&amp;nbsp;(.+?)(?:<br|$)', re.IGNORECASE),
        ]
    }

    # Try each pattern
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = pattern.search(description)
            if match:
                value = match.group(1).strip()
                # Clean up HTML tags and entities
                value = BeautifulSoup(value, 'html.parser').get_text()
                # Remove any remaining non-breaking spaces
                value = value.replace('\xa0', '').replace('&nbsp;', '').strip()
                metadata[field] = value if value else None
                break

    return metadata


def parse_event(entry: Any) -> Dict[str, Any]:
    """Parse a single RSS feed entry into structured event data."""
    event = {
        'title': entry.get('title', ''),
        'description': entry.get('description', ''),
        'event_date': entry.get('published', ''),
        'link': entry.get('link', ''),
        'guid': entry.get('id', ''),
        'source_event_id': None,
        'summary': entry.get('summary', ''),
    }

    # Extract GUID ID
    if event['guid']:
        event['source_event_id'] = extract_guid_id(event['guid'])

    # Extract metadata from description
    if event['description']:
        metadata = extract_metadata_from_description(event['description'])
        event.update(metadata)

    return event


def analyze_completeness(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate metadata completeness statistics."""
    total = len(events)
    if total == 0:
        return {}

    fields = ['title', 'description', 'event_date', 'link', 'guid',
              'city_area', 'age_range', 'venue', 'price', 'category']

    stats = {}
    for field in fields:
        non_null_count = sum(1 for e in events if e.get(field))
        stats[field] = {
            'count': non_null_count,
            'percentage': round((non_null_count / total) * 100, 1)
        }

    return stats


def assess_kid_relevance(events: List[Dict[str, Any]], sample_size: int = 20) -> Dict[str, Any]:
    """Manually review random sample for kid-relevance.

    For automation, we'll use keyword-based heuristics:
    - Age range mentions kids/children/family
    - Categories like 'Kids', 'Family', 'Children'
    - Titles/descriptions mentioning kids/children/family
    """
    sample = random.sample(events, min(sample_size, len(events)))

    kid_keywords = [
        'kid', 'kids', 'child', 'children', 'family', 'toddler',
        'preschool', 'elementary', 'youth', 'teen', 'baby', 'babies',
        'age 0', 'age 1', 'age 2', 'age 3', 'age 4', 'age 5',
        'under 12', 'under 18', 'all ages'
    ]

    relevant_count = 0
    maybe_count = 0
    sample_details = []

    for event in sample:
        text = f"{event['title']} {event.get('description', '')} {event.get('age_range', '')} {event.get('category', '')}".lower()

        # Count keyword matches
        matches = sum(1 for kw in kid_keywords if kw in text)

        if matches >= 2:
            verdict = 'yes'
            relevant_count += 1
        elif matches == 1:
            verdict = 'maybe'
            maybe_count += 1
        else:
            verdict = 'no'

        sample_details.append({
            'title': event['title'],
            'age_range': event.get('age_range'),
            'category': event.get('category'),
            'verdict': verdict
        })

    return {
        'sample_size': len(sample),
        'relevant': relevant_count,
        'maybe': maybe_count,
        'not_relevant': len(sample) - relevant_count - maybe_count,
        'relevance_ratio': round((relevant_count / len(sample)) * 100, 1),
        'sample_details': sample_details
    }


def rate_scraping_difficulty() -> Dict[str, Any]:
    """Rate scraping difficulty on 1-5 scale with justification."""
    return {
        'score': 2,
        'scale': '1 (easiest) to 5 (hardest)',
        'justification': [
            'RSS format is well-structured and stable',
            'Standard feedparser library handles parsing reliably',
            'HTML entity encoding variations require extra handling (&nbsp; vs &amp;nbsp;)',
            'Metadata extraction from HTML description requires regex patterns',
            'GUID extraction is straightforward with simple regex',
            'Overall: Low difficulty, suitable for production scraper'
        ],
        'challenges': [
            'HTML entity encoding inconsistencies',
            'Metadata embedded in description HTML rather than separate fields',
            'Need to handle missing optional fields gracefully'
        ]
    }


def main():
    """Main execution flow."""
    print("=" * 60)
    print("KNCO RSS Feed Evaluation - Story E1.1")
    print("=" * 60)
    print()

    # 1. Fetch feed
    feed = fetch_feed(KNCO_RSS_URL)

    print(f"Feed title: {feed.feed.get('title', 'N/A')}")
    print(f"Feed link: {feed.feed.get('link', 'N/A')}")
    print(f"Total entries: {len(feed.entries)}")
    print()

    # 2. Parse events
    print("Parsing events...")
    events = [parse_event(entry) for entry in feed.entries]
    print(f"Parsed {len(events)} events")
    print()

    # 3. Analyze completeness
    print("Analyzing metadata completeness...")
    completeness = analyze_completeness(events)
    print("\nField Completeness:")
    for field, stats in completeness.items():
        print(f"  {field:20s}: {stats['count']:3d}/{len(events):3d} ({stats['percentage']:5.1f}%)")
    print()

    # 4. Assess kid-relevance
    print("Assessing kid-relevance (automated heuristic)...")
    relevance = assess_kid_relevance(events, sample_size=20)
    print(f"  Sample size: {relevance['sample_size']}")
    print(f"  Relevant: {relevance['relevant']} ({relevance['relevance_ratio']}%)")
    print(f"  Maybe: {relevance['maybe']}")
    print(f"  Not relevant: {relevance['not_relevant']}")
    print()

    # 5. Rate difficulty
    difficulty = rate_scraping_difficulty()
    print(f"Scraping Difficulty: {difficulty['score']}/5")
    print(f"Justification:")
    for point in difficulty['justification']:
        print(f"  - {point}")
    print()

    # 6. Save results
    results = {
        'evaluation_date': datetime.now().isoformat(),
        'feed_url': KNCO_RSS_URL,
        'feed_info': {
            'title': feed.feed.get('title', 'N/A'),
            'link': feed.feed.get('link', 'N/A'),
        },
        'event_count': len(events),
        'completeness': completeness,
        'kid_relevance': relevance,
        'scraping_difficulty': difficulty,
        'sample_events': events[:5]  # Include first 5 events as examples
    }

    # Save JSON results
    results_file = 'data/knco_evaluation_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {results_file}")

    # Save raw sample XML
    sample_xml_file = 'data/samples/knco_sample.xml'
    with open(sample_xml_file, 'w', encoding='utf-8') as f:
        # Get raw RSS content
        import requests
        response = requests.get(KNCO_RSS_URL)
        f.write(response.text)
    print(f"Raw RSS sample saved to: {sample_xml_file}")

    print()
    print("=" * 60)
    print("Evaluation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
