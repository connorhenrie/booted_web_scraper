import sys
import requests
import asyncio
from crawl import crawl_site_async

async def main():
    print("Hello from web-scraper!")
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        base_url = sys.argv[1]
        print(f"starting crawl of {base_url}")

    try:
        page_data = await crawl_site_async(base_url)
    except Exception as e:
        print(f"Error fetching HTML from {base_url}: {str(e)}")
        sys.exit(1)

    print(f"found {len(page_data)} pages")
    for value in page_data.values():
        print(value)

if __name__ == "__main__":
    asyncio.run(main())
