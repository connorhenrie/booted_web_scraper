from urllib.parse import urlsplit
from bs4 import BeautifulSoup, Tag

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
    soup = BeautifulSoup(html)
    main_tag = soup.find("main")
    if main_tag:
        main_p = main_tag.find("p")
    else:
        main_p = soup.find("p")
    return main_p.get_text(strip=True) if isinstance(main_p, Tag) else ""
