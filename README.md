# BevoFit Scrapers

A collection of Python web scrapers that collect recreational sports data from the UT Recreational Sports website and store it in a Supabase database.

## Scrapers

### 1. intramuralsScraper.py

Scrapes intramural sports data from the UT Rec Sports intramurals page.

**What it scrapes:**
- Activity names and categories
- Registration dates
- Event start dates
- Participation fees

**Categories processed:**
- Team Sport Leagues
- Singles and Doubles Leagues
- One-Day Tournaments
- Special Events

**Database table:** `intramurals`

### 2. infoScraper.py

One-time scraper that extracts detailed facility information.

**What it scrapes:**
- Facility addresses
- General facility information
- Activities available at each facility
- Facility features and amenities

**How it works:**
- Queries facility URLs from the database
- Scrapes each facility's detail page
- Updates the facilities table with scraped data

**Database table:** `facilities`

### 3. hoursScraper.py

Daily scraper designed to run on AWS Lambda with EventBridge scheduling.

**What it scrapes:**
- Weekly operating hours (Monday through Sunday)
- Special holiday hours
- Open/closed status

**Features:**
- Normalizes time formats (converts "6a" to "6:00 AM", "Noon" to "12:00 PM")
- Handles facility name variations (hyphenated vs space-separated)
- Extracts special dates from holiday banners
- Clears stale special date information when updating regular hours

**Database table:** `facility_hours`

## Libraries Used

- **requests** - Makes HTTP requests to fetch webpages
- **BeautifulSoup (bs4)** - Parses HTML and extracts data
- **lxml** - HTML parser used by BeautifulSoup
- **supabase-py** - Connects to and interacts with Supabase database
- **python-dotenv** - Loads environment variables from .env file
- **re** - Regular expressions for text parsing and normalization

## Setup

Create a `.env` file with your Supabase credentials:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_key
```

## Usage

Run each scraper independently:

```bash
python intramuralsScraper.py
python infoScraper.py
python hoursScraper.py
```

## AWS Lambda

**hoursScraper.py** has been implemented as an EventBridge Cron Job in AWS Lambda, running every day at 5:00 AM CST.

## AWS Lambda

**hoursScraper.py** has been implemented as an EventBridge Cron Job in AWS Lambda, running every day at 5:00 AM CST.

**Deployment:**
- Runtime: Python 3.x
- Handler: hoursScraper.lambda_handler (if using a handler function)
- Dependencies packaged in Lambda layer or deployment zip

**Environment Variables (Lambda Configuration):**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SECRET_KEY` - Your Supabase service role key

**EventBridge Schedule:**
- Cron expression: `cron(0 5 * * ? *)`
- Target: hoursScraper Lambda function
