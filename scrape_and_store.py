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

        elements = frame.query_selector_all("div.font-black")
        print(f"Found {len(elements)} elements with class 'font-black' inside iframe")

        selector = "div.flex.items-center.font-black.text-[24px].sm:text-[30px]"
        frame.wait_for_selector(selector, timeout=20000)
        div = frame.query_selector(selector)
        if not div:
            raise Exception("Bitcoin value div not found inside iframe")

        main_part = div.evaluate("el => el.childNodes[0].textContent.trim()")
        decimal_part = div.query_selector("span").text_content().strip()

        full_value_str = main_part + decimal_part
        full_value_str = full_value_str.replace(',', '')

        browser.close()
        return float(full_value_str)

if __name__ == "__main__":
    value = get_bitcoin_value()
    print("Bitcoin value:", value)


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
