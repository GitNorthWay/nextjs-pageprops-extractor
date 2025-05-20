
"""
Example script demonstrating how to use the NextDataExtractor class
to extract pageProps data from Next.js pages and save them to JSON files.
"""
from typing import Dict, Any, Optional
from utils.generic import read_json_file
from utils.next_data_extractor import NextDataExtractor


if __name__ == "__main__":
    # Extract pageProps from a single page and save to a JSON file
    print("\n Extract pageProps from a single page and save to a JSON file")
    website_details: Optional[Dict[str, str]] = read_json_file("website_details.json")

    if website_details is None:
        print("Failed to read website_details.json")
        exit(1)

    homepage_url: str = website_details["homepage_url"]
    single_page_url: str = website_details["page_url"]

    # Use the extractor as a context manager
    with NextDataExtractor(homepage_url, headless=True) as extractor:
        # Extract data and save to a JSON file
        success: bool = extractor.extract_and_save(single_page_url)

        if success:
            print(f"Successfully extracted and saved data from {single_page_url}")
        else:
            print(f"Failed to extract data from {single_page_url}")
