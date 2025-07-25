import os
import boto3
from playwright.sync_api import sync_playwright

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

from playwright.sync_api import sync_playwright

def get_bitcoin_value():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://app.bullz.games/")

        # Wait for iframe element to load
        iframe_element = page.wait_for_selector("iframe#reactIframe", timeout=20000)

        # Get iframe's frame object
        frame = iframe_element.content_frame()
        if frame is None:
            raise Exception("Iframe content frame not found")

        # Wait for the target div inside the iframe
        selector = r"div.flex.items-center.font-black.text-\[24px\].sm\:text-\[30px\]"
        frame.wait_for_selector(selector, timeout=20000, state="attached")  # wait for presence, not visibility
        div = frame.query_selector(selector)
        if not div:
            raise Exception("Bitcoin value div not found inside iframe")

        # get text content anyway
        main_part = div.evaluate("el => el.childNodes[0].textContent.trim()")
        decimal_part = div.query_selector("span").text_content().strip()

        full_value_str = main_part + decimal_part
        full_value_str = full_value_str.replace(',', '')
        # Remove commas for float conversion

        browser.close()
        return float(full_value_str)

if __name__ == "__main__":
    value = get_bitcoin_value()
    print("Bitcoin value:", value)

from decimal import Decimal
from datetime import datetime

def store_value_in_dynamodb(value):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(DYNAMODB_TABLE)

    now = datetime.utcnow().isoformat()  # string for timestamp partition key
    price_str = str(value)  # convert price to string for sort key

    response = table.put_item(
        Item={
            'timestamp': now,  # partition key (string)
            'price': price_str,  # sort key (string)
            # Add other attributes here if needed
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
