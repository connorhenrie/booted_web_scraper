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
