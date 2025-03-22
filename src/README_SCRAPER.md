# Google Maps Visible Browser Scraper

This tool allows you to scrape business information from Google Maps using a visible Chrome browser with Selenium. It performs searches, scrolls through results, and extracts business data including names, addresses, phone numbers, websites, and opening hours.

## Features

- **Visible Browser Interaction**: Watch the scraper navigate Google Maps in real-time
- **Proxy Integration**: Optional use of proxies from the ProxyHarvester for anonymity
- **Smart Scrolling**: Automatically scrolls to load all available results
- **Business Data Extraction**: Extracts key business information
- **User-Agent Rotation**: Changes browser fingerprints to avoid detection

## Usage

### Basic Usage

To run a Google Maps search with a visible browser:

```bash
python run_scraper.py "coffee shops" --location "New York"
```

This will:
1. Open a Chrome browser window
2. Navigate to Google Maps
3. Search for "coffee shops" in "New York"
4. Scroll through the results to load all items
5. Extract data from each business listing
6. Save the results to a JSON file in the data directory

### Using with Proxies

You can use the integrated proxy support to run the scraper with a random elite proxy:

```bash
python run_scraper.py "coffee shops" --location "New York" --use-proxy
```

This will:
1. First run the ProxyHarvester to find working proxies
2. Select an optimal proxy based on speed and anonymity
3. Run the Google Maps scraper using the selected proxy

### Command Line Options

```
positional arguments:
  query                 Search query for Google Maps

options:
  -h, --help            show this help message and exit
  --location LOCATION, -l LOCATION
                        Location for the search
  --output OUTPUT, -o OUTPUT
                        Output directory for scraped data
  --headless            Run browser in headless mode
  --max-results MAX_RESULTS, -m MAX_RESULTS
                        Maximum number of results to scrape
  --use-proxy, -p       Use a proxy from the proxy harvester
  --proxy-file PROXY_FILE
                        Load proxies from this file instead of harvesting new ones
  --proxy-type {elite,anonymous,all}
                        Type of proxy to use (elite, anonymous, all)
  --harvest-only        Only harvest proxies, do not run scraper
  --country-filter COUNTRY_FILTER
                        Country filter for proxy harvesting
```

## Examples

### Search for restaurants in Chicago with a maximum of 50 results:

```bash
python run_scraper.py "restaurants" --location "Chicago" --max-results 50
```

### Use an existing proxy file and only use elite proxies:

```bash
python run_scraper.py "hotels" --location "Miami" --use-proxy --proxy-file "../data/proxies.json" --proxy-type elite
```

### Only harvest proxies without running the scraper:

```bash
python run_scraper.py "anything" --harvest-only --country-filter US
```

## Output

The scraper creates JSON files in the data directory with this structure:

```json
{
  "search_query": "coffee shops New York",
  "timestamp": "20250322_151234",
  "count": 42,
  "businesses": [
    {
      "name": "Starbucks",
      "category": "Coffee shop",
      "address": "123 Main St, New York, NY 10001",
      "website": "starbucks.com",
      "phone": "(212) 555-1234",
      "hours": "Monday: 6:00 AM–8:00 PM\nTuesday: 6:00 AM–8:00 PM\n...",
      "timestamp": "2025-03-22 15:12:45"
    },
    // More businesses...
  ]
}
```
