"""Configuration management for Nevada County Kids Events"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Cache settings
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "6"))

    # Scraper settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    SAMPLES_DIR = DATA_DIR / "samples"
