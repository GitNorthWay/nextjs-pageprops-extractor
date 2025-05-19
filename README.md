
# Next.js PageProps Extractor

A utility for extracting `pageProps` data from Next.js server-rendered pages.

## Overview

This project provides tools to extract data from the `__NEXT_DATA__` script tag that is present in Next.js server-rendered pages using Selenium. The extractor automatically saves the extracted data to JSON files for further processing.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/checkyourdeals.git
   cd checkyourdeals
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

In main.py add the homepage URL for cookie handling and the page URL for the page you want to extract data from. You will get a message whether the extraction was successful or not.

```python
from utils.next_data_extractor import extract_next_data

# URLs for the website
homepage_url = "https://example.com"  # Homepage URL for cookie handling
page_url = "https://example.com/some-next-js-page"  # Specific page to extract data from

# Extract the pageProps data and save to a JSON file in the 'data' folder
page_props = extract_next_data(homepage_url, page_url)

if page_props:
   print("Successfully extracted pageProps and saved to the 'data' folder")
else:
   print("Failed to extract pageProps from the page")
```

### Visible Browser for Debugging

For debugging purposes, you can run Selenium with a visible browser window:

```python
page_props = extract_next_data(homepage_url, page_url, headless=False)
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

## Appliction References

### `extract_next_data(homepage_url, page_url, headless=True)`

Main function that extracts pageProps data from a Next.js page using Selenium and saves it to a JSON file.

**Parameters:**
- `homepage_url` (str): The homepage URL of the website (used for cookie handling)
- `page_url` (str): The URL of the Next.js page to extract data from
- `headless` (bool): Whether to run the Selenium browser in headless mode (default: True)

**Returns:**
- `bool`: True if extraction was successful, None if it failed

### `extract_next_data_with_selenium(homepage_url, page_url, headless=True)`

Extract pageProps data using Selenium.

**Parameters:**
- `homepage_url` (str): The homepage URL of the website (used for cookie handling)
- `page_url` (str): The URL of the Next.js page to extract data from
- `headless` (bool): Whether to run the browser in headless mode (default: True)

**Returns:**
- `dict`: The pageProps data or None if not found

### `save_data_to_json(data, url, folder="data")`

Save the extracted data to a JSON file in the specified folder.

**Parameters:**
- `data` (dict): The data to save
- `url` (str): The URL of the page the data was extracted from
- `folder` (str): The folder to save the data to (default: "data")

**Returns:**
- `str`: The path to the saved file or None if saving failed