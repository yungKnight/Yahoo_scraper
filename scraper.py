import pytest
import asyncio
from playwright.async_api import async_playwright
import scrapy
from scrapy.http import HtmlResponse
import csv
import os
import re
from datetime import datetime
from utils import get_valid_date as validate_date, date_to_unix as to_unix
from utils import parse_date_string

@pytest.mark.asyncio
async def test_map():
    print(f"Welcome to the forex extraction tool")
    currency_pair = input("Enter the currency pair (e.g., USDEUR, GBPUSD): ").upper()

    today = datetime.today()
    min_end_date = datetime(2005, 1, 1)

    start_date = validate_date("Enter the start date (e.g., Sep 30, 2024): ", max_date=today)
    end_date = validate_date("Enter the end date (e.g., Jan 01, 2020): ", min_date=min_end_date)

    start_date_secs = to_unix(start_date)
    end_date_secs = to_unix(end_date)

    if start_date < end_date:
        print("Error: Start date cannot be earlier than the end date.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def handle_request(route, request):
            if request.resource_type in ['image', 'iframe']:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", handle_request)

        url = f'https://finance.yahoo.com/quote/{currency_pair}=X/history/?period1={end_date_secs}&period2={start_date_secs}'
        print(f'Navigating to Yahoo! Finance {currency_pair} historical data prices')
        await page.goto(url, timeout=0)

        await page.wait_for_selector('section.gridLayout > div.container')
        print('Page has been navigated to successfully')

        await page.query_selector('div.container > div.table-container')
        print('Table container holding needed elements confirmed')

        await asyncio.sleep(5)

        html_content = await page.content()
        if html_content is not None:
            print("retrieved html content")
        else:
            print("nothing here really")

        response = HtmlResponse(url=page.url, body=html_content.encode(), encoding='utf-8')

        headers = response.css('table thead tr th::text').getall()
        headers = [header.strip() for header in headers if header.strip()]  # Remove empty headers
        print(f"Extracted headers: {headers}")

        date_header = None
        close_header = None

        for header in headers:
            if header == 'Date':
                date_header = header
            elif header == 'Close':
                close_header = header

            if date_header and close_header:
                break

        print('Grabbing all rows containing historical data')
        rows = response.css('div.table-container > table.table > tbody tr')
        print('All rows selected')

        price_data = []

        for row in rows:
            date_text = row.css('td:nth-child(1)::text').get()
            close_price = row.css('td:nth-child(5)::text').get()
            
            if not date_text or not close_price:
                continue
                
            date_text = date_text.strip()
            close_price = close_price.strip()
            
            print(f"{currency_pair} closed at {close_price} on {date_text}")

            row_date = parse_date_string(date_text)
            if row_date is None:
                continue

            if row_date <= start_date and row_date >= end_date:
                price_data.append((date_text, close_price))

        print(f"Total data points collected: {len(price_data)}")
        
        price_data.sort(key=lambda x: parse_date_string(x[0]))

        file_name = f'{currency_pair}_historical_data.csv'
        file_exists = os.path.isfile(file_name)

        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([date_header or 'Date', close_header or 'Close'])

            for data in price_data:
                writer.writerow([data[0], data[1]])

        print(f"Data saved to {file_name}")
        print(f"Total rows written: {len(price_data)}")

        await asyncio.sleep(2)
        await page.close()
        await browser.close()