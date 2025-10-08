# Nevada County Kids Events - Scraping Engine

Event aggregation and delivery system for Nevada County family-friendly events.

## Setup Instructions

### Prerequisites
- Python 3.11+ (tested with 3.12.10)
- Supabase account with Postgres database

### Installation

1. **Clone the repository** (if applicable)

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

6. **Verify installation**
   ```bash
   python -m src --help
   ```

## Project Structure

```
nevada-county-kids-events/
├── src/
│   ├── config.py           # Configuration management
│   ├── orchestrator.py     # Main orchestration logic
│   ├── scrapers/           # Source-specific scrapers
│   ├── processors/         # Data normalization
│   ├── storage/            # Database and caching
│   └── delivery/           # Output mechanisms
├── tests/                  # Test suite
├── data/samples/           # Sample data for testing
└── requirements.txt        # Python dependencies
```

## Development

### Running Tests
```bash
python -m pytest
```

### Running the Scraper
```bash
python -m src.orchestrator --source knco
```

## License

TBD
