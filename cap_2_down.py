# -*- coding: utf-8 -*-
"""
@author: ncs
"""

import os
import pandas as pd
from sec_api import RenderApi
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SEC_API_KEY")

if not API_KEY:
    print("Error: SEC_API_KEY not found in environment variables.")
    exit(1)

try:
    renderApi = RenderApi(api_key=API_KEY)
except Exception as e:
    print(f"Error: Failed to initialize RenderApi: {e}")
    exit(1)

# Load metadata with error handling
try:
    metadata = pd.read_csv('metadata.csv')
except FileNotFoundError:
    print("Error: metadata.csv not found.")
    exit(1)
except pd.errors.EmptyDataError:
    print("Error: metadata.csv is empty.")
    exit(1)
except pd.errors.ParserError:
    print("Error: Error parsing metadata.csv. Check file format.")
    exit(1)
except Exception as e:
    print(f"Error: An unexpected error occured when loading metadata: {e}")
    exit(1)

def download_filing(row):
    """Downloads a filing from a given URL and saves it to a local folder."""
    ticker = row['ticker']
    filing_url = row['filingUrl'].replace('ix?doc=/', '')
    file_name = filing_url.split("/")[-1]
    new_folder = os.path.join("./filings", ticker)

    try:
        os.makedirs(new_folder, exist_ok=True)
        file_content = renderApi.get_filing(filing_url)

        with open(os.path.join(new_folder, file_name), "w", encoding="utf-8") as f:
            f.write(file_content)

        print(f"Downloaded {file_name} for {ticker}")

    except FileNotFoundError:
        print(f"Error: Filing URL not found: {filing_url}")
    except Exception as e:
        print(f"Error: Error downloading {file_name} for {ticker}: {e}")

try:
    metadata.apply(download_filing, axis=1)
except Exception as e:
    print(f"Error: An unexpected error occurred during download: {e}")
    exit(1)

print("Filing download process completed.")