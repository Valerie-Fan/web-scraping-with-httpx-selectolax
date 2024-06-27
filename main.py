import httpx
from selectolax.parser import HTMLParser
import time
from urllib.parse import urljoin
from dataclasses import dataclass, asdict, fields
import json
import csv 

@dataclass
class Item:
    name: str or None
    item_num: str or None
    price: str or None
    rating: float or None

def get_html(url, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
    }

    if kwargs.get("page"):
        resp = httpx.get(url + str(kwargs.get("page")), headers=headers, follow_redirects=True)
    else:
        resp = httpx.get(url, headers=headers, follow_redirects=True)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.", "Page Limit Exceed.")
        return False
    html = HTMLParser(resp.text)


    return html


def extract_data(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None

def parse_page(html):
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")

    for product in products:
        yield urljoin("https://www.rei.com", product.css_first("a").attributes["href"])

def parse_item_page(html):
    item = Item(
            name=extract_data(html, "h1#product-page-title"),
            item_num=extract_data(html, "span#product-item-number"),
            price=extract_data(html, "span#buy-box-product-price"),
            rating=extract_data(html, "span.cdr-rating__number_15-0-0")
            )
    return asdict(item)

def export_to_json(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved to json.")

def export_to_csv(products):
    field_names = [field.name for field in fields(Item)]
    with open("products.csv", "w") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerows(products)
    print("Saved to csv.")

def append_to_csv(products):
    field_names = [field.name for field in fields(Item)]
    with open("products.csv", "a") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writerow(products)
    print("Append to csv.")


def main():
#   products = []
   url = "https://www.rei.com/c/camping-and-hiking/f/scd-deals?page="
   for x in range(1, 2):
       print(f"Gathering Page: {x}")
       html = get_html(url, page=x)
       if html == False:
           break
       product_urls = parse_page(html)
       for url in product_urls:
           html = get_html(url)
           append_to_csv(parse_item_page)
           time.sleep(0.5)
#   export_to_json(products)
#   export_to_csv(products)

if __name__ == "__main__":
    main()
