"""Base scraper interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse events from the source.

        Returns:
            List of event dictionaries with raw data
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw data into structured event dictionaries.

        Args:
            raw_data: Raw data from the source

        Returns:
            List of parsed event dictionaries
        """
        pass
