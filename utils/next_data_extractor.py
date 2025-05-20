"""
Utility module for extracting pageProps data from Next.js pages.

This module provides a class to extract data from the __NEXT_DATA__ script tag
that is present in Next.js server-rendered pages using Selenium.
"""

import json
from typing import Dict, Optional, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
import time
import random

from utils.generic import save_data_to_json


class NextDataExtractor:
    """
    A class for extracting pageProps data from Next.js pages using Selenium.

    This class can be used as a context manager to ensure proper cleanup of resources:

    Example:
        ```python
        with NextDataExtractor(homepage_url) as extractor:
            page_props = extractor.extract_page_props(page_url)
        ```
    """

    # Default list of analytics and tracking domains to block
    DEFAULT_BLOCKED_DOMAINS = [
    "plausible.io",
    "google-analytics.com",
    "analytics.google.com",
    "googletagmanager.com",
    "hotjar.com",
    "mixpanel.com",
    "segment.io",
    "segment.com",
    "matomo.cloud",
    "matomo.org",
    "clarity.ms",
    "facebook.net",
    "facebook.com",
    "linkedin.com",
    "twitter.com",
    "amplitude.com",
    "heap.io",
    "fullstory.com",
    "logrocket.com",
    "mouseflow.com",
    "doubleclick.net",
    "quantserve.com",
    "scorecardresearch.com",
    "chartbeat.com",
    "kissmetrics.com",
    "clicky.com",
    "newrelic.com",
    "adobe.com",
    "crazyegg.com"
]


    def __init__(self, homepage_url: str, headless: bool = True, blocked_domains: Optional[List[str]] = None) -> None:
        """
        Initialize the NextDataExtractor with the homepage URL and browser settings.

        Args:
            homepage_url (str): The homepage URL of the website (used for cookie handling)
            headless (bool): Whether to run the browser in headless mode
            blocked_domains (List[str], optional): List of domains to block. If None, uses DEFAULT_BLOCKED_DOMAINS
        """
        self.homepage_url: str = homepage_url
        self.headless: bool = headless
        self.blocked_domains: List[str] = blocked_domains if blocked_domains is not None else self.DEFAULT_BLOCKED_DOMAINS
        self.driver: Optional[webdriver.Chrome] = None
        self.chrome_options: Options = self._configure_chrome_options()

    def __enter__(self) -> 'NextDataExtractor':
        """
        Enter the context manager.

        Returns:
            NextDataExtractor: The instance itself
        """
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """
        Exit the context manager and ensure the driver is closed.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self._close_driver()

    def _configure_chrome_options(self) -> Options:
        """
        Configure Chrome options for the WebDriver.

        Returns:
            Options: Configured Chrome options
        """
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")  # Use the new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Enhanced anti-bot detection measures
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Add realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

        # Add language preferences
        chrome_options.add_argument("--lang=nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7")

        # Set page load timeout
        chrome_options.page_load_strategy = "normal"

        # Block requests to analytics and tracking domains to prevent timeout errors
        if self.blocked_domains:
            # Join domains with comma for the Chrome host-blocking-patterns argument
            blocked_domains_str = ",".join(self.blocked_domains)
            chrome_options.add_argument(f"--host-blocking-patterns={blocked_domains_str}")

        return chrome_options

    def _initialize_driver(self) -> None:
        """
        Initialize the Selenium WebDriver.

        Raises:
            Exception: If the WebDriver initialization fails
        """
        exceptions: List[str] = []

        # On Windows, try multiple approaches
        if platform.system() == 'Windows':
            # Approach 1: Try to create a Chrome driver directly with Service object
            try:
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
                return
            except Exception as e:
                exceptions.append(f"Windows approach failed: {str(e)}")

        else:
            # Approach 2: On non-Windows platforms, use webdriver-manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
                return
            except Exception as e:
                exceptions.append(f"Non-Windows approach failed: {str(e)}")

        # If both approaches failed, raise an exception with details
        error_details: str = "\n".join(exceptions)
        raise Exception(f"Failed to create Chrome WebDriver after multiple attempts:\n{error_details}")

    def _close_driver(self) -> None:
        """
        Close the Selenium WebDriver if it exists.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    def extract_page_props(self, page_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract pageProps data from a Next.js page.

        Args:
            page_url (str): The URL of the Next.js page to extract data from

        Returns:
            dict: The pageProps data or None if not found
        """
        try:
            self._initialize_driver()

            # Set page load timeout
            self.driver.set_page_load_timeout(30)

            # Add cookies for the domain (if needed)
            self.driver.get(self.homepage_url)

            # Wait a bit to simulate human behavior
            time.sleep(random.uniform(2, 4))

            # Navigate to the actual URL
            self.driver.get(page_url)

            # Add random pauses to simulate human behavior
            time.sleep(random.uniform(3, 5))

            # Scroll down a bit to trigger any lazy-loading
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(random.uniform(1, 2))

            # Wait for the page to load completely
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait to ensure JavaScript has executed
            time.sleep(random.uniform(2, 3))

            # Find and extract data from the __NEXT_DATA__ script
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "__NEXT_DATA__")))
            next_data_script = self.driver.find_element(By.ID, "__NEXT_DATA__")
            script_text = next_data_script.get_attribute("textContent") or next_data_script.get_attribute("text") or ""

            # Validate that we have text content before trying to parse it
            if not script_text or script_text.strip() == "":
                raise ValueError("Empty __NEXT_DATA__ script content")

            # Debug information
            print(f"__NEXT_DATA__ script found with length: {len(script_text)}")
            if len(script_text) > 100:
                print(f"Sample of script content: {script_text[:100]}...")

            # Try to parse the JSON
            next_data = json.loads(script_text)

            # Validate the expected structure exists
            if 'props' in next_data and 'pageProps' in next_data['props']:
                return next_data['props']['pageProps']
            else:
                raise ValueError("Missing 'props.pageProps' in __NEXT_DATA__")

        except Exception as e:
            print(f"Error extracting data with Selenium: {e}")
            return None
        finally:
            self._close_driver()

    def extract_and_save(self, page_url: str) -> bool:
        """
        Extract pageProps data from a Next.js page and save it to a JSON file.

        Args:
            page_url (str): The URL of the Next.js page to extract data from

        Returns:
            bool: True if extraction and saving succeeded, False otherwise
        """
        print("Extracting pageProps with Selenium...")
        page_props = self.extract_page_props(page_url)

        if page_props:
            print("Successfully extracted pageProps with Selenium")
            # Save the data to a JSON file
            save_data_to_json(page_props, page_url)
            return True
        else:
            print("Failed to extract pageProps with Selenium")
            print("Try running with headless=False to see what's happening in the browser")
            print("Or check the error messages above for more details on what went wrong")
            return False


def extract_next_data(homepage_url: str, page_url: str, headless: bool = True, 
                  blocked_domains: Optional[List[str]] = None) -> bool:
    """
    Extract pageProps data from a Next.js page using Selenium and save it to a JSON file.
    This function maintains backward compatibility with the previous API.

    Args:
        homepage_url (str): The homepage URL of the website (used for cookie handling)
        page_url (str): The URL of the Next.js page to extract data from
        headless (bool): Whether to run the Selenium browser in headless mode
        blocked_domains (List[str], optional): List of domains to block. If None, uses DEFAULT_BLOCKED_DOMAINS

    Returns:
        bool: True if extraction and saving succeeded, False otherwise
    """
    extractor = NextDataExtractor(homepage_url, headless=headless, blocked_domains=blocked_domains)
    return extractor.extract_and_save(page_url)
