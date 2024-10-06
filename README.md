# Yahoo_scraper
This project hosts a scraping script used in scraping financial historical data from Yahoo Finance. Script scrapes dynamically enabling scrapes of different currencies with ease and different timeframes too so you can extract as much as possible spanning over 4 years

## Installation

To set up this project, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Yahoo_scraper.git
   ```
2. **Check into directory:**
	```sh
   cd Yahoo_scraper
   ```

3. **Create a virtual environment:**
	```sh
	python -m venv venv
	```

4. **Activate virtual environment: (On windows)**
	```sh
	source venv\Scripts\activate
	```
## USAGE

1. To run the google maps scraper, run this command rom your terminal:
```sh
	pytest scraper.py
```

2. When you run the script, it will prompt you to enter the currency pair whose daily historical data you are looking to scrape (e.g USDGBP).

3. A few seconds after your first input, you will be prompted to specify what date ranges you are looking to garner info within

4. After successful scrape, your file is stored on same level as my scraper file with your scraped currency pair being the title
