from bs4 import BeautifulSoup as bs4
import logging as log
import time
import pandas as pd
import asyncio
import aiohttp
from pydantic import BaseModel
import random


# ---- Basic ogging infra ----
log.basicConfig(
    level=log.INFO,
    format= "%(asctime)s %(levelname)s - %(message)s"
    )

BASE_URL = "https://books.toscrape.com/"

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }


class Book(BaseModel):
    title : str
    price : str
    stock : str
    desc  : str
    img   : str

async def fetch(session, url):
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                log.info("Successfully fetch {url}")
                return await response.text()
            else:
                log.error(f"Failed to fetch {url} with status code {response.status}")

    except Exception as e:
        log.error(f"Error fetching {url} : {e}")
    return None

async def extract_page_data(session, url):
    html_content = await fetch(session, url)
    if html_content :
        html = bs4(html_content, "html.parser")
        return extract_data(html)


async def extract_link_from_page(session, url):
    html_content = await fetch(session, url)
    if html_content:
        soup = bs4(html_content, "html.parser")
        raw_lists = soup.find_all("article", {"class": "product_pod"})
        links = [BASE_URL+ raw.find("a").get("href") for raw in raw_lists]
        return links
    return []


async def get_next_page(session, html):
    try:
        raw_next_page = html.find("li" , {'class' : "next"})
        if raw_next_page:
            next_page_link = BASE_URL+ raw_next_page.a.get("href")
            return next_page_link
    except Exception as e:
        log.info("Pagination ends here.")

    return None


def extract_data(html):
    try:
        title = html.find("h1").get_text()
        price = html.find("p", {"class": "price_color"}).get_text()
        stock = html.find("p", {"class" : "instock availability"}).get_text().replace("\n", "").replace("In stock", "")
        desc_link = html.find("div", {"id" : "product_description"})
        desc = desc_link.next_sibling.next_element.get_text()
        image = html.find("div", {"class" : "item active"}).img.get("src")

        return {
            "title" : title,
            "price" : price,
            "stock" : stock,
            "desc" : desc,
            "image" : image
        }

    except Exception as e:
        log.error(f"Error extracting data from page: {e}")

    return None


async def book_scraper():
    async with aiohttp.ClientSession() as session:
        page_url = BASE_URL

        all_books_data = []
        while page_url:
            log.info(f"Scraping page: {page_url}")
            links = await extract_link_from_page(session, page_url)
            tasks = [extract_page_data(session, link) for link in links]
            results = await asyncio.gather(*tasks)

            for data in results:
                if data:
                    all_books_data.append(data)


            # Find next page links
            html_content = await fetch(session, page_url)

            if html_content:
                html = bs4(html_content, "html.parser")

                page_url = await get_next_page(session, html)

            else:
                page_url = None

def main():
    start_time = time.time()

    loop = asyncio.get_event_loop()
    books_data = loop.run_until_complete(book_scraper())

    # Save to the dataframe

    df = pd.DataFrame(books_data)
    print(df)
    print(f"total listings {len(df)}" )
    print(f"elapsed time: {time.time() - start_time:.2f}s")



if __name__ == "__main__":
    main()
