# Supabase Database Setup

The `events` table has been successfully created in your Telegram Supabase project!

## Database Connection

To connect to the database from Python, you need to add your database password to the `.env` file.

### Getting Your Database Password

1. Go to your Supabase project: https://supabase.com/dashboard/project/uzgvldniipdsbqupsvqy
2. Click **Database** in the left sidebar
3. Click **Database Settings**
4. Look for **Database password** section
5. Copy the password (or reset it if needed)

### Update .env File

Add this line to your `.env` file:

```bash
SUPABASE_DB_PASSWORD=your-database-password-here
```

Your complete `.env` should look like:

```bash
# Supabase Configuration
SUPABASE_URL=https://uzgvldniipdsbqupsvqy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=your-database-password-here

# Cache Configuration
CACHE_TTL_HOURS=6

# Request Settings
REQUEST_TIMEOUT=30
SCRAPER_TIMEOUT=30

# Quality Settings
MIN_QUALITY_SCORE=0
```

## Table Schema

The `events` table was created with the following schema:

- **id**: BIGSERIAL PRIMARY KEY
- **title**: TEXT NOT NULL
- **description**: TEXT
- **event_date**: TIMESTAMP WITH TIME ZONE
- **venue**: TEXT
- **city_area**: TEXT
- **source_name**: TEXT NOT NULL
- **source_url**: TEXT
- **source_event_id**: TEXT
- **scraped_at**: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- **content_hash**: TEXT
- **event_types**: TEXT[]
- **age_range**: TEXT
- **price**: TEXT
- **is_free**: BOOLEAN
- **kid_friendly_score**: INTEGER
- **quality_score**: INTEGER
- **created_at**: TIMESTAMP WITH TIME ZONE DEFAULT NOW()

### Indexes

- Unique index on `(source_name, source_event_id)` prevents duplicate events from same source
- Indexes on `event_date`, `source_name`, `content_hash`, and `scraped_at` for query performance

## Testing the Connection

Once you've added the password to `.env`, test the connection:

```bash
python -m src.orchestrator --sources knco
```

This will attempt to scrape events and store them in the database.
