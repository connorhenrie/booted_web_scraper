from urllib.parse import urlsplit

def normalize_url(url: str) -> str:
    split_url = urlsplit(url)
    normalized_url = f"{split_url.netloc}{split_url.path}"
    normalized_url = normalized_url.removesuffix("/")
    return normalized_url
