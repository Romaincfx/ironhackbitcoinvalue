import requests
from bs4 import BeautifulSoup
import boto3
from datetime import datetime

# DynamoDB setup (replace 'your-region' and 'your-table-name')
dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
table = dynamodb.Table('romainbitcoinprice')

def get_bitcoin_value():
    url = "https://app.bullz.games/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find("div", class_="flex items-center font-black text-[24px] sm:text-[30px]")
    if not div:
        raise ValueError("Bitcoin value div not found")

    main_part = div.contents[0].strip()  # e.g. "104,795."
    decimal_part = div.find("span").text.strip()  # e.g. "86"
    full_value_str = main_part + decimal_part
    full_value_str = full_value_str.replace(',', '')  # e.g. "104795.86"

    return float(full_value_str)

def save_to_dynamodb(bitcoin_value):
    timestamp = datetime.utcnow().isoformat()
    response = table.put_item(
        Item={
            'timestamp': timestamp,
            'bitcoin_value': bitcoin_value
        }
    )
    print(f"Saved to DynamoDB at {timestamp}: {bitcoin_value}")

if __name__ == "__main__":
    value = get_bitcoin_value()
    print("Bitcoin value:", value)
    save_to_dynamodb(value)