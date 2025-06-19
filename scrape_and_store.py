import os
import boto3
from playwright.sync_api import sync_playwright

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

def get_bitcoin_value():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://app.bullz.games/")
        page.wait_for_selector("//div[contains(@class, 'font-black')]", timeout=10000)

        div = page.query_selector("//div[contains(@class, 'font-black')]")
        if not div:
            browser.close()
            raise ValueError("Bitcoin value div not found")

        main_part = div.text_content()
        decimal_span = div.query_selector("span")
        decimal_part = decimal_span.text_content() if decimal_span else ""

        main_only = main_part.replace(decimal_part, "").strip()
        full_value_str = (main_only + decimal_part).replace(',', '')
        browser.close()

        return float(full_value_str)

def store_value_in_dynamodb(value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE)
    from datetime import datetime
    now = datetime.utcnow().isoformat()

    response = table.put_item(
        Item={
            'timestamp': now,
            'bitcoin_value': value
        }
    )
    return response

if __name__ == "__main__":
    try:
        value = get_bitcoin_value()
        print(f"Bitcoin value: {value}")
        store_value_in_dynamodb(value)
        print("Stored value in DynamoDB.")
    except Exception as e:
        print(f"Error: {e}")
        raise
