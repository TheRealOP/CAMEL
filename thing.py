import csv
import time
import requests
from datetime import datetime

# Configuration
CRYPTO_SYMBOL = 'bitcoin'  # Change this to the desired cryptocurrency
FIAT_CURRENCY = 'usd'
CSV_FILE = 'crypto_data.csv'
INTERVAL = 60  # Interval in seconds


# Function to fetch the latest data from CoinGecko API
def fetch_latest_data(crypto_symbol, fiat_currency):
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_symbol}&vs_currencies={fiat_currency}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[crypto_symbol][fiat_currency]
    except requests.RequestException as e:
        print(f"HTTP error: {e}")
    except KeyError as e:
        print(f"Parsing error: {e}")
    return None


# Function to append data to CSV file
def append_to_csv(timestamp, price, count):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, price, count])
    print(f'Appended data to CSV: {timestamp}, {price}')


# Function to reset the CSV file
def reset_csv_file():
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'price', 'count'])
    print(f'CSV file {CSV_FILE} created/reset.')


# Main function to start data collection
def start_data_collection():
    count = 0
    reset_csv_file()
    while True:
        count+=1
        timestamp = datetime.now().isoformat()
        price = fetch_latest_data(CRYPTO_SYMBOL, FIAT_CURRENCY)
        if price is not None:
            append_to_csv(timestamp, price, count)
        else:
            print("Error fetching data")
        time.sleep(INTERVAL)


if __name__ == '__main__':
    start_data_collection()
