# -*- coding: utf-8 -*-
"""
@author: ncs
"""

import requests
import csv
import pandas as pd
from sec_api import QueryApi
import os
from dotenv import load_dotenv

load_dotenv()

def download_sp500_holdings(url, output_filename='s-p500.csv'):
    """Downloads S&P 500 holdings from a given URL and saves it to a CSV."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded S&P 500 holdings to {output_filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading holdings: {e}")
        return None
    return output_filename

def clean_sp500_csv(input_filename, output_filename='s-p500_clean.csv'):
    """Cleans the downloaded S&P 500 CSV by removing empty rows."""
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        empty_row_indices = [i for i, row in enumerate(rows) if not row or any('\xa0' in cell for cell in row)]

        if len(empty_row_indices) < 2:
            print("Error: Could not find expected empty rows. Cleaning failed.")
            return None

        start = empty_row_indices[0] + 1
        end = empty_row_indices[1]
        cleaned_rows = rows[start:end]

        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_rows)
        print(f"Cleaned S&P 500 CSV to {output_filename}")
        return output_filename
    except FileNotFoundError:
        print(f"Error: Input file {input_filename} not found.")
        return None
    except Exception as e:
        print(f"An error occurred during CSV cleaning: {e}")
        return None

def create_ticker_batches(tickers, max_batch_size=50):
    """Creates batches of tickers with a maximum size."""
    batches = []
    for i in range(0, len(tickers), max_batch_size):
        batches.append(tickers[i:i + max_batch_size])
    return batches

def download_10k_metadata(api_key, start_year, end_year, holdings_csv='s-p500_clean.csv', output_csv='metadata.csv'):
    """Downloads 10-K metadata for a list of tickers within a year range."""
    try:
        holdings = pd.read_csv(holdings_csv)
        tickers = holdings['Ticker'].tolist()
    except FileNotFoundError:
        print(f"Error: Holdings CSV {holdings_csv} not found.")
        return None
    except KeyError:
        print("Error: 'Ticker' column not found in holdings CSV.")
        return None
    except Exception as e:
        print(f"An error occurred reading the holdings CSV: {e}")
        return None

    query_api = QueryApi(api_key=api_key)
    all_metadata = []

    for year in range(start_year, end_year + 1):
        ticker_batches = create_ticker_batches(tickers)
        for batch in ticker_batches:
            tickers_joined = ', '.join(batch)
            query_string = (
                f'ticker:({tickers_joined}) AND '
                f'filedAt:[{year}-01-01 TO {year}-12-31] AND '
                'formType:"10-K" AND NOT formType:"10-K/A" AND NOT formType:NT'
            )

            query = {
                "query": query_string,
                "from": "0",
                "size": "50",
                "sort": [{"filedAt": {"order": "desc"}}]
            }

            try:
                response = query_api.get_filings(query)
                filings = response['filings']
                metadata = [
                    {
                        'ticker': f['ticker'],
                        'cik': f['cik'],
                        'formType': f['formType'],
                        'filedAt': f['filedAt'],
                        'filingUrl': f['linkToFilingDetails'],
                    }
                    for f in filings
                ]
                all_metadata.extend(metadata)
            except Exception as e:
                print(f"Error querying SEC API for year {year} and batch {batch}: {e}")

    if all_metadata:
        df = pd.DataFrame(all_metadata)
        df.to_csv(output_csv, index=False)
        print(f"Downloaded 10-K metadata to {output_csv}")
        return df
    else:
        print("No metadata downloaded.")
        return None

def main():
    """Main function to orchestrate the data gathering process."""
    API_KEY = os.environ.get("SEC_API_KEY")
    if not API_KEY:
        print("Error: SEC_API_KEY not found in environment variables.")
        return

    START_YEAR = 2020
    END_YEAR = 2020
    HOLDINGS_URL = 'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund'

    holdings_file = download_sp500_holdings(HOLDINGS_URL)
    if holdings_file:
        cleaned_file = clean_sp500_csv(holdings_file)
        if cleaned_file:
            download_10k_metadata(API_KEY, START_YEAR, END_YEAR, cleaned_file)
            
if __name__ == "__main__":
    main()