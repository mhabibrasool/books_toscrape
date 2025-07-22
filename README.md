# books_toscrape

A Python-based web scraper for extracting book data from the website [Books to Scrape](https://books.toscrape.com/).

##  Features

- Scrapes book details like title, price, stock, description, and image URL.
- Efficient concurrent scraping using `aiohttp` and `asyncio` for faster page fetching.
- Handles pagination automatically, fetching data across multiple pages.
- Saves the extracted data into a Pandas DataFrame for easy analysis.
- Basic error handling for network issues and HTML parsing.


## Requirements

- Python 3.7+
- Install dependencies using `pip`:

```bash
pip install requests beautifulsoup4 pandas aiohttp


