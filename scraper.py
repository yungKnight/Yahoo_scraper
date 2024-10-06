import pytest
import asyncio
from playwright.async_api import async_playwright
import scrapy
from scrapy.http import HtmlResponse
import csv
import os
from datetime import datetime

@pytest.mark.asyncio
async def test_map():
    currency_pair = input("Enter the currency pair (e.g., USDEUR, GBPUSD): ").upper()

    today = datetime.today()
    min_end_date = datetime(2020, 1, 1)

    def get_valid_date(prompt, max_date=None, min_date=None):
        while True:
            try:
                date_str = input(prompt)
                date = datetime.strptime(date_str, '%b %d, %Y')
                if max_date and date > max_date:
                    print(f"Date cannot be later than {max_date.strftime('%b %d, %Y')}.")
                elif min_date and date < min_date:
                    print(f"Date cannot be earlier than {min_date.strftime('%b %d, %Y')}.")
                else:
                    return date
            except ValueError:
                print("Invalid date format. Please use 'MMM DD, YYYY' format (e.g., 'Sep 30, 2024').")

    start_date = get_valid_date("Enter the start date (e.g., Sep 30, 2024): ", max_date=today)
    end_date = get_valid_date("Enter the end date (e.g., Jan 01, 2020): ", min_date=min_end_date)

    if start_date < end_date:
        print("Error: Start date cannot be earlier than the end date.")
        return

    print(f"Validated Start Date: {start_date.strftime('%b %d, %Y')}")
    print(f"Validated End Date: {end_date.strftime('%b %d, %Y')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        async def handle_request(route, request):
            if request.resource_type in ['image', 'iframe']:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", handle_request)

        url = f'https://finance.yahoo.com/quote/{currency_pair}=X/history/?guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAKoogbZXzWpA28dwXvlZl02wHykj3TfTUJXXKb35msyXwsqki9A76ktjJhuv_eWci1q-e-KCAlLk08Z7dvBRutV-WXFjA3BNAqwHTN3ET1KNrEWXrw6inRs-FknCzX_WVP9Pau6fYHw7mV7rWLa8OwcEkw4wr56jkayYD_bCLTb_&guccounter=2&period1=1569885924&period2=1727738620'
        print(f'Navigating to Yahoo! Finance {currency_pair} historical data prices')
        await page.goto(url, timeout=0)

        print('Confirming page has navigated successfully')
        await page.wait_for_selector('article.gridLayout > div.container')
        print('Page has been navigated to successfully')

        print('Confirming the table container to extract needed elements')
        await page.query_selector('div.container > div.table-container')
        print('Table container holding needed elements confirmed')

        await asyncio.sleep(2)

        html_content = await page.content()

        response = HtmlResponse(url=page.url, body=html_content.encode(), encoding='utf-8')

        headers = response.css('table thead tr th::text').getall()
        headers = [header.strip() for header in headers]

        date_header = None
        close_header = None

        for header in headers:
            if header == 'Date':
                date_header = header
            elif header == 'Close':
                close_header = header

            if date_header and close_header:
                break

        print(f"Extracted headers: {headers}")
        print(f"Date header: {date_header}")
        print(f"Close header: {close_header}")

        print('Grabbing all rows containing historical data')
        rows = response.css('table.table.yf-ewueuo > tbody tr')
        print('All rows selected')

        price_data = []
        capturing = False

        for row in rows:
            date = row.css('td:nth-child(1)::text').get().strip()
            close_price = row.css('td:nth-child(5)::text').get()

            if date == start_date.strftime('%b %d, %Y'):
                capturing = True

            if capturing:
                price_data.append((date, close_price))

            if date == end_date.strftime('%b %d, %Y'):
                break

        for data in price_data:
            print(f"Date: {data[0]}, Close Price: {data[1]}")

        file_name = f'{currency_pair}_historical_data.csv'
        file_exists = os.path.isfile(file_name)

        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([date_header, close_header])

            for data in price_data:
                writer.writerow([data[0], data[1]])

        print(f"Data saved to {file_name}")

        await asyncio.sleep(2)

        await page.close()
