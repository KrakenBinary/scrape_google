# TryloByte

```
 ████████╗██████╗ ██╗   ██╗██╗      ██████╗ ██████╗ ██╗   ██╗████████╗███████╗
 ╚══██╔══╝██╔══██╗╚██╗ ██╔╝██║     ██╔═══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝
    ██║   ██████╔╝ ╚████╔╝ ██║     ██║   ██║██████╔╝ ╚████╔╝    ██║   █████╗  
    ██║   ██╔══██╗  ╚██╔╝  ██║     ██║   ██║██╔══██╗  ╚██╔╝     ██║   ██╔══╝  
    ██║   ██║  ██║   ██║   ███████╗╚██████╔╝██████╔╝   ██║      ██║   ███████╗
    ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝
                                                                             
    [ Digital Reconnaissance System v1.0 ]
    [ Initiating cyber-infiltration sequence... ]
    [ Target: Google Maps | Status: ACTIVE ]
```

TryloByte is a retro-terminal themed Google Maps scraping tool with advanced proxy management, multithreading support, and human-like behavior simulation to avoid detection.

## Features

- **Retro Terminal Interface**: Experience a nostalgic hacker-style command-line interface
- **Advanced Proxy Management**: Automatically fetches, tests, and rotates free proxies
- **Error Handling**: Detects CAPTCHAs, rate limiting, and other blocking mechanisms
- **Multithreaded Operations**: Parallel processing for both proxy testing and scraping
- **Human-like Behavior**: Simulates realistic user interactions to avoid detection
- **Automatic Environment Setup**: One-click setup of virtual environment and dependencies

## Requirements

- Python 3.8+
- Chrome or Firefox browser
- Internet connection

## Installation

### Option 1: Using the built-in setup command
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/google-maps-scraper.git
   cd google-maps-scraper
   ```

2. Run the TryloByte setup command
   ```bash
   python3 tryloByte.py
   ```
   Then enter the `setup` command at the prompt

### Option 2: Manual Setup

#### For Debian/Ubuntu Systems
Install required packages using apt:
```bash
sudo apt-get install -y python3-selenium python3-bs4 python3-requests python3-urllib3 python3-fake-useragent python3-colorama python3-tqdm
```

Some packages may not be available in the standard repositories. For these, you can use pip with the `--break-system-packages` flag (use with caution):
```bash
sudo pip3 install webdriver-manager fake-useragent --break-system-packages
```

> **Note**: Using `--break-system-packages` is generally not recommended but may be necessary in externally managed environments. The better alternative is to use a virtual environment as described below.

#### For Other Systems
1. Create a virtual environment (optional but recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install selenium beautifulsoup4 requests urllib3 fake_useragent colorama tqdm webdriver-manager
   ```

### Installing Requirements

You can install the required Python packages in two ways:

1. **Automatic Setup** (Recommended):
   ```bash
   # TryloByte will set up everything automatically when you first run it
   python3 tryloByte.py
   
   # Or explicitly run the setup command
   python3 tryloByte.py --setup
   ```

2. **Manual Installation**:
   ```bash
   # Install all dependencies directly
   pip install -r requirements.txt
   
   # Or install colorama for the retro terminal experience
   pip install colorama
   ```

The tool requires the following key packages:
- selenium (browser automation)
- requests/beautifulsoup4 (web scraping)
- colorama (terminal colors)
- fake-useragent (browser fingerprint randomization)
- webdriver-manager (webdriver management)

## Quick Start

Just run the TryloByte script and it will guide you through the setup process:

```bash
python3 tryloByte.py
```

Alternatively, you can set up the environment directly:

```bash
python3 tryloByte.py --setup
```

## Usage

### Interactive Mode (Recommended)

1. Launch the TryloByte terminal:
   ```bash
   python3 tryloByte.py
   ```

2. Use the following commands:
   ```
   setup              - Set up the virtual environment and install dependencies
   set <option> <value> - Set a configuration option
   config/settings    - Show current configuration
   scrape "<query>"   - Scrape Google Maps for the given query
   clear              - Clear the terminal screen
   help               - Display help information
   exit/quit          - Exit the program
   ```

3. Examples:
   ```
   >> set headless true
   >> set max_results 0       # 0 means unlimited results
   >> scrape "coffee shops in Mandeville Louisiana"
   ```

### Command Line Mode

You can also run TryloByte in command line mode:

```bash
# Scrape a single query with unlimited results
python3 -m src.main "coffee shops in Mandeville Louisiana" --headless --max-results 0

# Scrape multiple queries from a file with 4 parallel threads
python3 -m src.main --queries-file queries.txt --headless --threads 4
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| headless | Run browser in headless mode | false |
| browser | Browser to use (chrome/firefox) | chrome |
| max_results | Maximum results to scrape per query (0 = unlimited) | 0 |
| listings_per_proxy | Listings to scrape before rotating proxy (0 = unlimited) | 0 |
| output_dir | Directory to save output data | data |
| target_proxy_count | Number of working proxies to find (0 = unlimited) | 10 |
| proxy_test_url | URL used to test proxy connectivity | http://httpbin.org/ip |

## Proxy Management

TryloByte automatically fetches and validates proxies to help avoid detection when scraping Google Maps. The application manages this process by:

1. Collecting proxy servers from multiple free sources
2. Testing each proxy for functionality, speed, and anonymity
3. Using a rotating proxy system to distribute requests
4. Blacklisting proxies that consistently fail

You can customize the proxy behavior:
- Set `target_proxy_count` to control how many working proxies the system finds before stopping
- Set `proxy_test_url` to use a different URL for testing proxy connections
- Set `listings_per_proxy` to control how frequently proxies are rotated

## Advanced Features

### Multithreaded Scraping

TryloByte supports multithreaded scraping for processing multiple queries in parallel:

```bash
python3 -m src.main --queries-file queries.txt --threads 4
```

### Data Output

All scraped data is saved in JSON format in the specified output directory (default: `data/`).

## License

This project is for educational purposes only. Use responsibly and in accordance with Google's terms of service.

## Acknowledgements

TryloByte was developed as an enhancement to the original Google Maps scraper with a focus on creating a unique retro terminal experience while improving functionality and performance.

## Disclaimer

Web scraping may be against the terms of service of some websites. Use this tool responsibly and at your own risk. The developers are not responsible for any misuse of this tool.
