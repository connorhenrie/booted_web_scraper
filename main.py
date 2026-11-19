import sys
from turtle import write
import requests
import asyncio
from crawl import crawl_site_async
from json_report import write_json_report

async def main():
    print("Hello from web-scraper!")
    if len(sys.argv) != 4:
        print("incorrect number of arguments. Requires URL | concurrency | max pages")
        sys.exit(1)
    else:
        base_url = sys.argv[1]
        max_concurrenty = int(sys.argv[2])
        max_pages = int(sys.argv[3])
        print(f"starting crawl of {base_url}")

    try:
        page_data = await crawl_site_async(base_url, max_concurrenty, max_pages)
    except Exception as e:
        print(f"Error fetching HTML from {base_url}: {str(e)}")
        sys.exit(1)

    print(f"found {len(page_data)} pages")
    write_json_report(page_data)

if __name__ == "__main__":
    asyncio.run(main())
