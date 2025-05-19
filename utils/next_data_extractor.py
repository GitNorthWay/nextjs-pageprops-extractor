"""
Utility module for extracting pageProps data from Next.js pages.

This module provides a function to extract data from the __NEXT_DATA__ script tag
that is present in Next.js server-rendered pages using Selenium.
"""

import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
import platform
import time
import random

from utils.generic import save_data_to_json


def extract_next_data_with_selenium(homepage_url, page_url, headless=True):
    """
    Extract pageProps data from a Next.js page using Selenium.

    Args:
        url (str): The URL of the Next.js page
        headless (bool): Whether to run the browser in headless mode

    Returns:
        dict: The pageProps data or None if not found
    """
    try:


        # Set up Chrome options
        chrome_options = Options()
        if headless:
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

        # Set up the webdriver
        driver = None
        exceptions = []

        # On Windows, try multiple approaches
        if platform.system() == 'Windows':
            # Approach 1: Try to create a Chrome driver directly with Service object
            try:
                service = Service()
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                exceptions.append(f"Windows approach failed: {str(e)}")

        else:
            # Approach 2: On non-Windows platforms, use webdriver-manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                exceptions.append(f"Non-Windows approach failed: {str(e)}")

        # If both approaches failed, raise an exception with details
        if driver is None:
            error_details = "\n".join(exceptions)
            raise Exception(f"Failed to create Chrome WebDriver after multiple attempts:\n{error_details}")

        try:
            # Set page load timeout
            driver.set_page_load_timeout(30)

            # Add cookies for the domain (if needed)
            driver.get(homepage_url)

            # Wait a bit to simulate human behavior
            time.sleep(random.uniform(2, 4))

            # Navigate to the actual URL
            driver.get(page_url)

            # Add random pauses to simulate human behavior
            time.sleep(random.uniform(3, 5))

            # Scroll down a bit to trigger any lazy-loading
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(random.uniform(1, 2))

            # Wait for the page to load completely
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait to ensure JavaScript has executed
            time.sleep(random.uniform(2, 3))

            try:
                # Find and extract data from the __NEXT_DATA__ script
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__NEXT_DATA__")))
                next_data_script = driver.find_element(By.ID, "__NEXT_DATA__")
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
            except Exception as element_error:
                print(f"Error finding or parsing Next.js data: {element_error}")
                raise
        finally:
            # Close the webdriver
            driver.quit()
    except Exception as e:
        print(f"Error extracting data with Selenium: {e}")
        return None





def extract_next_data(homepage_url, page_url, headless=True):
    """
    Extract pageProps data from a Next.js page using Selenium and save it to a JSON file.

    Args:
        homepage_url (str): The homepage URL of the website (used for cookie handling)
        page_url (str): The URL of the Next.js page to extract data from
        headless (bool): Whether to run the Selenium browser in headless mode

    Returns:
        dict: The pageProps data or None if not found
    """
    print("Extracting pageProps with Selenium...")
    page_props = extract_next_data_with_selenium(homepage_url, page_url, headless=headless)

    if page_props:
        print("Successfully extracted pageProps with Selenium")
        # Save the data to a JSON file
        save_data_to_json(page_props, page_url)
        return True
    else:
        print("Failed to extract pageProps with Selenium")
        print("Try running with headless=False to see what's happening in the browser")
        print("Or check the error messages above for more details on what went wrong")

    return None

