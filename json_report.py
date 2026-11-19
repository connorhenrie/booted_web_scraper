import json

def write_json_report(page_data, filename="report.json"):
    # sort the pages by url
    pages = sorted(page_data.values(), key=lambda p: p["url"])

    # write to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
