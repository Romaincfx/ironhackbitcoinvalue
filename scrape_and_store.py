import os
import boto3
from playwright.sync_api import sync_playwright

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

def get_bitcoin_value():
    url = "https://app.bullz.games/"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("div.font-black", timeout=20000)

        # Now select the element
        div = page.query_selector("div.font-black")
        if not div:
            raise ValueError("Bitcoin value div not found")

        main_part = div.text_content().strip()
        # You might need to refine extraction depending on actual HTML here
        browser.close()
        return main_part

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
