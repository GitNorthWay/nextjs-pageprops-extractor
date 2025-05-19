import os
import json

def read_saved_data(filepath):
    """
    Read data from a saved JSON file.

    Args:
        filepath (str): Path to the JSON file

    Returns:
        dict: The data from the JSON file or None if reading failed
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading data from {filepath}: {e}")
        return None

def save_data_to_json(data, url, folder="data"):
    """
    Save the extracted data to a JSON file in the specified folder.

    Args:
        data (dict): The data to save
        url (str): The URL of the page the data was extracted from
        folder (str): The folder to save the data to (default: "data")

    Returns:
        str: The path to the saved file or None if saving failed
    """
    try:
        # Create the folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Create a filename based on the URL
        # Replace non-alphanumeric characters with underscores
        # Remove protocol (http:// or https://)
        clean_url = url.replace("http://", "").replace("https://", "")
        # Replace special characters with underscores
        filename = "".join(c if c.isalnum() else "_" for c in clean_url)
        # Limit filename length and add .json extension
        filename = filename[:100] + ".json"
        filepath = os.path.join(folder, filename)

        # Save the data to a JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving data to JSON: {e}")
        return None