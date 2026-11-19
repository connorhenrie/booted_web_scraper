from logging import NullHandler
from urllib.parse import urlsplit, urljoin
from asyncio.timeouts import tasks
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import sys
import requests
import aiohttp
import asyncio


def normalize_url(url: str) -> str:
    split_url = urlsplit(url)
    normalized_url = f"{split_url.netloc}{split_url.path}"
    normalized_url = normalized_url.removesuffix("/")
    return normalized_url

def get_heading_from_html(html: str) -> str:
    # run Beautiful Soup on html input
    soup = BeautifulSoup(html, features="html.parser")
    h1_tag = soup.find("h1")
    h2_tag = soup.find("h2")
    if h1_tag:
        return h1_tag.get_text(strip=True) if isinstance(h1_tag, Tag) else ""
    elif h2_tag:
        return h2_tag.get_text(strip=True) if isinstance(h2_tag, Tag) else ""
    else:
        return ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main_tag = soup.find("main")
    if main_tag:
        main_p = main_tag.find("p")
    else:
        main_p = soup.find("p")
    return main_p.get_text(strip=True) if isinstance(main_p, Tag) else ""

def get_urls_from_html(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    urls = soup.find_all("a")
    abs_urls = []

    for link in urls:
        href = link.get("href")
        if not isinstance(href, str) or not href:
            continue
        try:
            absolute_url = urljoin(base_url, href)
        except ValueError as e:
            print(f"Error: {e}: {href}")
            continue

        abs_urls.append(absolute_url)
    return abs_urls

def get_images_from_html(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    img_urls = soup.find_all("img")
    abs_imgs = []
    for link in img_urls:
        src = link.get("src")
        if not isinstance(src, str) or not src:
            continue
        try:
            absolute_url = urljoin(base_url, src)
        except ValueError as e:
            print(f"Error: {e}: {src}")
            continue

        abs_imgs.append(absolute_url)
    return abs_imgs


# define PageData dictionary type hints
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def extract_page_data(html: str, page_url: str):
    page_data: PageData = {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
    return page_data


# def crawl_page(base_url, current_url=None, page_data=None):
#     if current_url is None:
#         current_url = base_url
#     if page_data is None:
#         page_data = {}
#     # check if current URL is in the same domain as the base url
#     # keeps function from crawling other sites
#     base_split = urlsplit(base_url)
#     current_split = urlsplit(current_url)
#     if base_split.netloc != current_split.netloc:
#         return page_data
#
#     # normalize the current URL, check if crawled
#     norm_url = normalize_url(current_url)
#     if norm_url in page_data:
#         return page_data
#
#     # get HTML from current URL
#     print(f"getting HTML from {current_url}")
#     webpage_html = get_html(current_url)
#     webpage_data = extract_page_data(webpage_html, current_url)
#     page_data[norm_url] = webpage_data
#     outgoing_links = webpage_data["outgoing_links"]
#     # recursive call
#     for link in outgoing_links:
#         crawl_page(base_url, link, page_data)

#    return page_data

class AsyncCrawler:
    def __init__(self, base_url, max_concurrenty, max_pages):
        self.base_url: str = base_url
        self.base_domain: str = urlsplit(base_url).netloc
        self.page_data: dict = {}
        self.visited: set = set()
        self.lock = asyncio.Lock()
        self.max_concurrency: int = max_concurrenty
        self.max_pages: int = max_pages
        self.should_stop: bool = False
        self.all_tasks: set = set()
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl")
                return False
            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)
                return True

    async def get_html(self, url) -> str:
        try:
            print(f"getting HTML from {url}")
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as resp:
                if resp.status > 399:
                    raise Exception(f"got HTTP error: {resp.status} {resp.reason}")
                content_type = resp.headers.get("content-type", "")
                if "text/html" not in content_type:
                    raise Exception(f"got non-HTML response: {content_type}")
                return await resp.text()
        except aiohttp.ClientError as e:
            raise Exception(f"network error while fetching {url}: {e}")


    async def crawl_page(self, current_url):
        if self.should_stop:
            return
        if current_url is None:
            return
        # check if current url is same domain as base domain
        if urlsplit(current_url).netloc != self.base_domain:
            return

        # add url to page_visit list to prevent crawling duplicates
        normalized_url = normalize_url(current_url)
        visit_result =  await self.add_page_visit(normalized_url)
        if not visit_result:
            return

        # extract html and data from a webpage
        async with self.semaphore:
            webpage_html = await self.get_html(current_url)
            if webpage_html is None:
                return
            webpage_data = extract_page_data(webpage_html, current_url)

        # add extracted page data to page_data class
        async with self.lock:
            self.page_data[normalized_url] = webpage_data

        # get outgoing links from webpage
        outgoing_links = webpage_data["outgoing_links"]

        # crawl all outgoing links in a page
        tasks = []
        for link in outgoing_links:
            try:
                task = asyncio.create_task(self.crawl_page(link))
                tasks.append(task)
                self.all_tasks.add(task)
            finally:
                self.all_tasks.remove(task)
        await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(url, concurrency, pages):
    async with AsyncCrawler(url, concurrency, pages) as crawler:
        await crawler.crawl()
        return crawler.page_data
