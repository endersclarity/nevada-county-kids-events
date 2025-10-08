"""Supabase Postgres storage client"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from ..config import Config
from ..processors.normalizer import NormalizedEvent

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase Postgres database"""

    def __init__(self):
        """Initialize database connection"""
        self.connection_string = self._build_connection_string()
        self.conn = None
        self._connect()

    def _build_connection_string(self) -> str:
        """Build Postgres connection string from Supabase credentials"""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

        # Extract project ref from URL
        # Format: https://[project-ref].supabase.co
        project_ref = Config.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')

        # Supabase Postgres connection format
        # Using pooler connection for better performance
        conn_str = f"postgresql://postgres.{project_ref}:{Config.SUPABASE_KEY}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

        return conn_str

    def _connect(self):
        """Establish database connection with error handling"""
        try:
            logger.info("Connecting to Supabase Postgres...")
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Successfully connected to Supabase")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise ConnectionError(f"Could not connect to Supabase: {e}")

    def upsert_events(self, events: List[NormalizedEvent]) -> int:
        """
        Insert or update events in the database.

        Uses ON CONFLICT to handle duplicates based on (source_name, source_event_id).

        Args:
            events: List of NormalizedEvent objects

        Returns:
            Number of events upserted
        """
        if not events:
            logger.warning("No events to upsert")
            return 0

        try:
            with self.conn.cursor() as cur:
                # Prepare data for batch insert
                values = []
                for event in events:
                    values.append((
                        event.title,
                        event.description,
                        event.event_date,
                        event.venue,
                        event.city_area,
                        event.source_name,
                        event.source_url,
                        event.source_event_id,
                        event.content_hash,
                        event.age_range,
                        event.price,
                        event.is_free,
                        event.quality_score,
                    ))

                # UPSERT query
                query = """
                    INSERT INTO events (
                        title, description, event_date, venue, city_area,
                        source_name, source_url, source_event_id, content_hash,
                        age_range, price, is_free, quality_score, scraped_at
                    ) VALUES %s
                    ON CONFLICT (source_name, source_event_id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        event_date = EXCLUDED.event_date,
                        venue = EXCLUDED.venue,
                        city_area = EXCLUDED.city_area,
                        age_range = EXCLUDED.age_range,
                        price = EXCLUDED.price,
                        is_free = EXCLUDED.is_free,
                        quality_score = EXCLUDED.quality_score,
                        scraped_at = NOW()
                """

                # Use execute_values for efficient batch insert
                execute_values(
                    cur,
                    query,
                    values,
                    template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
                )

                self.conn.commit()
                logger.info(f"Successfully upserted {len(events)} events")

                return len(events)

        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Error upserting events: {e}")
            raise

    def get_cached_events(
        self,
        source_name: str,
        ttl_hours: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get cached events from database within TTL.

        Args:
            source_name: Source to query (e.g., 'knco')
            ttl_hours: Time-to-live in hours (default 6)

        Returns:
            List of event dictionaries
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                    SELECT
                        id, title, description, event_date, venue, city_area,
                        source_name, source_url, source_event_id, content_hash,
                        age_range, price, is_free, quality_score, scraped_at
                    FROM events
                    WHERE source_name = %s
                      AND scraped_at > NOW() - INTERVAL '%s hours'
                    ORDER BY event_date ASC
                """

                cur.execute(query, (source_name, ttl_hours))
                rows = cur.fetchall()

                # Convert to list of dicts
                events = []
                for row in rows:
                    events.append({
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'event_date': row[3],
                        'venue': row[4],
                        'city_area': row[5],
                        'source_name': row[6],
                        'source_url': row[7],
                        'source_event_id': row[8],
                        'content_hash': row[9],
                        'age_range': row[10],
                        'price': row[11],
                        'is_free': row[12],
                        'quality_score': row[13],
                        'scraped_at': row[14],
                    })

                logger.info(f"Retrieved {len(events)} cached events for {source_name}")
                return events

        except psycopg2.Error as e:
            logger.error(f"Error retrieving cached events: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
