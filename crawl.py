from posix import wait
from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import sys
import requests



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


def get_html(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if response.status_code > 399:
        raise Exception(f"got HTTP error: {response.status_code} {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"got non-HTML response: {content_type}")

    return response.text

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}
    # check if current URL is in the same domain as the base url
    # keeps function from crawling other sites
    base_split = urlsplit(base_url)
    current_split = urlsplit(current_url)
    if base_split.netloc != current_split.netloc:
        return

    # normalize the current URL, check if crawled
    norm_url = normalize_url(current_url)
    if norm_url in page_data:
        return

    # get HTML from current URL
    print(f"getting HTML from {current_url}")
    webpage_html = get_html(current_url)
    webpage_data = extract_page_data(webpage_html, current_url)
    page_data[norm_url] = webpage_data
    #print(page_data)
    outgoing_links = webpage_data["outgoing_links"]
    # recursive call
    for link in outgoing_links:
        crawl_page(base_url, link, page_data)

    return page_data
