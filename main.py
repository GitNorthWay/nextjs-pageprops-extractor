
"""
Example script demonstrating how to use the next_data_extractor module
to extract pageProps data from Next.js pages and save them to JSON files.
"""

from utils.next_data_extractor import extract_next_data


if __name__ == "__main__":
    # Extract pageProps from a single page and save to a JSON file
    print("\n Extract pageProps from a single page and save to a JSON file")
    homepage_url = "https://www.example.com"
    single_page_url = "https://www.example.com/page1"

    # Extract data and save to a JSON file
    page_props = extract_next_data(homepage_url, single_page_url, True)

    if page_props:
        print(f"Successfully extracted and saved data from {single_page_url}")
    else:
        print(f"Failed to extract data from {single_page_url}")


