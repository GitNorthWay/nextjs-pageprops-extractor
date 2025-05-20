
# Next.js PageProps Extractor

A utility for extracting `pageProps` data from Next.js server-rendered pages.

## Overview

This project provides tools to extract data from the `__NEXT_DATA__` script tag that is present in Next.js server-rendered pages using Selenium. The extractor automatically saves the extracted data to JSON files for further processing.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nextjs-pageprops-extractor.git
   cd nextjs-pageprops-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

The tool uses a JSON configuration file (`website_details.json`) to specify the URLs for extraction. This file should contain the homepage URL for cookie handling and the specific page URL for data extraction.

#### Configuration File

Create a `website_details.json` file in the root directory with the following structure:

```json
{
  "homepage_url": "https://www.example.com",
  "page_url": "https://www.example.com/some-next-js-page"
}
```

An example file (`website_details_example.json`) is provided in the repository.

#### Class-based approach

```python
from typing import Dict, Optional
from utils.generic import read_json_file
from utils.next_data_extractor import NextDataExtractor

# Load website details from JSON file
website_details: Optional[Dict[str, str]] = read_json_file("website_details.json")

if website_details is None:
    print("Failed to read website_details.json")
    exit(1)

# Extract URLs from the configuration
homepage_url: str = website_details["homepage_url"]
page_url: str = website_details["page_url"]

# Use the extractor as a context manager
with NextDataExtractor(homepage_url, headless=True) as extractor:
    # Extract data and save to a JSON file
    success: bool = extractor.extract_and_save(page_url)

    if success:
        print(f"Successfully extracted and saved data from {page_url}")
    else:
        print(f"Failed to extract data from {page_url}")
```

### Visible Browser for Debugging

For debugging purposes, you can run Selenium with a visible browser window by setting the `headless` parameter to `False`:

```python
# After loading website details from JSON file as shown above
with NextDataExtractor(homepage_url, headless=False) as extractor:
    success = extractor.extract_and_save(page_url)
```

## WebDriver Initialization Approaches

The module uses two different approaches for initializing the Chrome WebDriver, depending on the operating system:

### 1. Service Object Approach (Windows)

On Windows platforms, the code attempts to create a Chrome WebDriver directly with a Service object:

```python
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
```

This approach assumes ChromeDriver is already installed and available in your system PATH. It's simpler but requires manual installation and management of the ChromeDriver executable.

**Advantages:**
- Simpler implementation
- No additional dependencies
- Can be faster when ChromeDriver is already installed

**Disadvantages:**
- Requires manual installation of ChromeDriver
- Requires manual updates when Chrome browser updates
- Needs to be in the system PATH
- Potential version compatibility issues

### 2. WebDriver Manager Approach (Non-Windows)

On non-Windows platforms (Linux, macOS), the code uses the webdriver-manager package to automatically download and manage the appropriate ChromeDriver:

```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

This approach is more reliable as it automatically handles ChromeDriver version compatibility with your installed Chrome browser.

**Advantages:**
- Automatically downloads the correct ChromeDriver version
- Handles updates when Chrome browser updates
- No need to manually manage ChromeDriver executables
- Better version compatibility
- No PATH configuration required

**Disadvantages:**
- Requires internet connection for first-time setup
- Slightly slower initialization (needs to check versions)
- Additional dependency on webdriver-manager package

## Chrome Options Explained

The module uses several Chrome options to improve stability, compatibility, and to bypass anti-bot detection.

### Basic Browser Configuration

```python
chrome_options.add_argument("--headless=new")  # Use the new headless mode
```
- `--headless=new`: Uses Chrome's newer headless implementation which provides better performance and compatibility than the older headless mode. This runs Chrome without a visible UI, which is useful for automated scripts.

```python
chrome_options.add_argument("--no-sandbox")
```
- `--no-sandbox`: Disables the Chrome sandbox, which can help avoid certain crashes and permission issues, especially in containerized environments.

```python
chrome_options.add_argument("--disable-dev-shm-usage")
```
- `--disable-dev-shm-usage`: Forces Chrome to use the /tmp directory instead of /dev/shm when the latter is too small. This helps prevent crashes in environments with limited shared memory.

```python
chrome_options.add_argument("--disable-gpu")
```
- `--disable-gpu`: Disables GPU hardware acceleration, which can help avoid graphics-related issues, especially in headless mode.

```python
chrome_options.add_argument("--window-size=1920,1080")
```
- `--window-size=1920,1080`: Sets the browser window size to 1920x1080 pixels, which is a common desktop resolution. This ensures consistent rendering and helps with element visibility.

### Anti-Bot Detection Measures

```python
chrome_options.add_argument("--disable-extensions")
```
- `--disable-extensions`: Disables browser extensions, which can interfere with automated browsing and make the browser fingerprint more unique and detectable.

```python
chrome_options.add_argument("--disable-popup-blocking")
```
- `--disable-popup-blocking`: Disables Chrome's built-in popup blocker, allowing the script to handle any popups that might appear during navigation.

```python
chrome_options.add_argument("--disable-infobars")
```
- `--disable-infobars`: Prevents Chrome from displaying informational bars (like "Chrome is being controlled by automated software"), which can interfere with element detection.

```python
chrome_options.add_argument("--disable-notifications")
```
- `--disable-notifications`: Blocks website notification requests, which can interrupt the automated browsing process.

```python
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
```
- `--disable-blink-features=AutomationControlled`: Disables the flag that indicates the browser is controlled by automation, making it harder for websites to detect that Selenium is being used.

```python
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
```
- These experimental options further help disguise the automated nature of the browser by removing automation-specific flags and disabling the automation extension.

### Browser Identity

```python
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
```
- Sets a specific user agent string that mimics a regular Chrome browser on Windows 10. This helps avoid detection as an automated browser.

```python
chrome_options.add_argument("--lang=nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7")
```
- Sets the browser's language preferences to Dutch (Netherlands) as primary, with fallbacks to Dutch, English (US), and English. This is useful for websites that serve different content based on language settings.

### Performance Settings

```python
chrome_options.page_load_strategy = "normal"
```
- Sets the page load strategy to "normal", which waits for the page to be fully loaded before proceeding. Other options include "eager" (faster but less complete) and "none" (minimal waiting).

### Blocking Analytics and Tracking Domains

```python
blocked_domains_str = ",".join(self.blocked_domains)
chrome_options.add_argument(f"--host-blocking-patterns={blocked_domains_str}")
```
- Blocks requests to analytics and tracking domains to prevent timeout errors and improve performance. The list of blocked domains is configurable and includes common analytics platforms by default.

## Additional Anti-Bot Techniques

Beyond Chrome options, the module implements several behavioral techniques to appear more human-like:

1. **Random timing delays**:
   ```python
   time.sleep(random.uniform(2, 4))  # Random delay between 2-4 seconds
   ```

2. **Scrolling behavior**:
   ```python
   driver.execute_script("window.scrollBy(0, 300);")  # Scroll down to trigger lazy-loading
   ```

3. **Cookie handling**:
   ```python
   driver.get(homepage_url)  # Visit homepage first to establish cookies
   ```

4. **Waiting for page load completion**:
   ```python
   WebDriverWait(driver, 30).until(
       lambda d: d.execute_script("return document.readyState") == "complete"
   )
   ```

## Expected PageProps Structure

The `pageProps` data is extracted from the `__NEXT_DATA__` script tag that is present in Next.js server-rendered pages. The structure of this data varies depending on the website, but generally follows this pattern:

```json
{
  "props": {
    "pageProps": {
      // Website-specific data here
    }
  }
}
```

The extractor specifically returns the contents of the `pageProps` object, which typically contains:

1. **Page-specific data**: Information about the current page, such as title, description, and metadata
2. **Content data**: The main content of the page, such as product information, articles, or listings
3. **Navigation data**: Information about site navigation, categories, or related pages
4. **User data**: If the page is personalized, it may contain user-specific information
5. **Internationalization data**: Translations and locale-specific content


## Troubleshooting

If you encounter issues with Selenium on Windows:

1. Make sure Google Chrome is installed on your system
2. Try running with `headless=False` to see if there are any visible browser errors
3. Check if your antivirus software is blocking the ChromeDriver
4. Try manually downloading the ChromeDriver that matches your Chrome version from the [official site](https://chromedriver.chromium.org/downloads) and placing it in your PATH
5. For 32-bit vs 64-bit issues, make sure you're using the correct version of Chrome for your system architecture

## Default Blocked Analytics Platforms

The NextDataExtractor class blocks requests to the following analytics and tracking domains by default:

- plausible.io
- google-analytics.com
- analytics.google.com
- googletagmanager.com
- hotjar.com
- mixpanel.com
- segment.io
- segment.com
- matomo.cloud
- matomo.org
- clarity.ms
- facebook.net
- facebook.com
- linkedin.com
- twitter.com
- amplitude.com
- heap.io
- fullstory.com
- logrocket.com
- mouseflow.com
- doubleclick.net
- quantserve.com
- scorecardresearch.com
- chartbeat.com
- kissmetrics.com
- clicky.com
- newrelic.com
- adobe.com
- crazyegg.com

You can customize this list by passing your own list of domains to block:

```python
# After loading website details from JSON file
website_details = read_json_file("website_details.json")
homepage_url = website_details["homepage_url"]
page_url = website_details["page_url"]

# Custom list of domains to block
my_blocked_domains = ["analytics.example.com", "tracker.example.com"]

# Use with the class-based approach
with NextDataExtractor(homepage_url, blocked_domains=my_blocked_domains) as extractor:
    success = extractor.extract_and_save(page_url)
```

## API Reference

### Class: `NextDataExtractor`

A class for extracting pageProps data from Next.js pages using Selenium.

#### Constructor

```python
NextDataExtractor(homepage_url, headless=True, blocked_domains=None)
```

**Parameters:**
- `homepage_url` (str): The homepage URL of the website (used for cookie handling)
- `headless` (bool): Whether to run the browser in headless mode (default: True)
- `blocked_domains` (List[str], optional): List of domains to block. If None, uses DEFAULT_BLOCKED_DOMAINS

#### Methods

##### `extract_page_props(page_url)`

Extract pageProps data from a Next.js page.

**Parameters:**
- `page_url` (str): The URL of the Next.js page to extract data from

**Returns:**
- `dict`: The pageProps data or None if not found

##### `extract_and_save(page_url)`

Extract pageProps data from a Next.js page and save it to a JSON file.

**Parameters:**
- `page_url` (str): The URL of the Next.js page to extract data from

**Returns:**
- `bool`: True if extraction and saving succeeded, False otherwise


### Function: `save_data_to_json(data, url, folder="data")`

Save the extracted data to a JSON file in the specified folder.

**Parameters:**
- `data` (dict): The data to save
- `url` (str): The URL of the page the data was extracted from
- `folder` (str): The folder to save the data to (default: "data")

**Returns:**
- `str`: The path to the saved file or None if saving failed
