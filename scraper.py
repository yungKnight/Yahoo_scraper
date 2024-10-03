import pytest
import asyncio
from playwright.async_api import async_playwright
import scrapy
from scrapy.http import HtmlResponse

@pytest.mark.asyncio
async def test_map():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        async def handle_request(route, request):
            if request.resource_type in ['image', 'iframe']:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", handle_request)

        url = 'https://finance.yahoo.com/quote/USDEUR=X/history/?guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAKoogbZXzWpA28dwXvlZl02wHykj3TfTUJXXKb35msyXwsqki9A76ktjJhuv_eWci1q-e-KCAlLk08Z7dvBRutV-WXFjA3BNAqwHTN3ET1KNrEWXrw6inRs-FknCzX_WVP9Pau6fYHw7mV7rWLa8OwcEkw4wr56jkayYD_bCLTb_&guccounter=2&period1=1569885924&period2=1727738620'
        print('Navigating to yahoo! finance EURUSD historical data prices')
        await page.goto(url, timeout=60000)

        print('confirming page has navigated successfully')
        await page.wait_for_selector('article.gridLayout > div.container')
        print('page has been navigated to successfully')

        print('confirming the table container to extract needed elements')
        await page.query_selector('div.container > div.table-container')
        print('table container holding needed elements confirmed')

        await asyncio.sleep(2)

        html_content = await page.content()

        response = HtmlResponse(url=page.url, body=html_content.encode(), encoding='utf-8')

        headers = response.css('table thead tr th::text').getall()
        headers = [header.strip() for header in headers]

        # date_header = headers[0] if 'Date' in headers else None
        # close_header = headers[4] if 'Close' in headers else None

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

        print('grabbing all rows containing historical data')
        rows = response.css('table.table.yf-ewueuo > tbody tr')
        print('All rows selected')

        start_date = 'Sep 30, 2024'
        end_date = 'Sep 29, 2023'

        price_data = []
        capturing = False

        for row in rows:
            date = row.css('td:nth-child(1)::text').get().strip()
            close_price = row.css('td:nth-child(5)::text').get()

            if date == start_date:
                capturing = True

            if capturing:
                price_data.append((date, close_price))
            
            if date == end_date:
                break

        for data in price_data:
            print(f"Date: {data[0]}, Close Price: {data[1]}")

        await page.close()
