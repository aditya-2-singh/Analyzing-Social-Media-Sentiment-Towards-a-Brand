import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
with open('config.json', 'r') as file:
    config = json.load(file)

proxy_username=config['PROXY_USERNAME']
proxy_password=config['PROXY_PASSWORD']

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "cookie": "<PASTE YOUR COOKIE STRING HERE>",  # Important!
    "host": "www.flipkart.com",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-full-version": '"134.0.6998.178"',
    "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.178", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.178"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"10.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
proxies={
        "http": f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80/",
        "https": f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80/"
    }

session = requests.Session()
session.headers.update(headers)


from urllib.parse import urlparse, parse_qs

def convert_to_review_url(product_url):
    parsed = urlparse(product_url)
    query = parse_qs(parsed.query)
    pid = query.get("pid", [""])[0]
    lid = query.get("lid", ["LST" + pid + "XXXXXX"])[0]


    # Extract product ID from path
    path_parts = parsed.path.split("/")
    try:
        product_id = path_parts[path_parts.index("p") + 1]
    except (ValueError, IndexError):
        return "Invalid URL"

    # Base review URL
    base = f"https://www.flipkart.com{parsed.path.replace('/p/', '/product-reviews/')}"
    review_url = f"{base}?pid={pid}"

    if lid:
        review_url += f"&lid={lid}"
    review_url += "&marketplace=FLIPKART"

    return review_url
print("Enter Product Url:")
url=input()
url=convert_to_review_url(url)
print(url)

ratings=[]
comments=[]
try:
    for i in range(1,11):
        url=url+f"page={i}"
        response=session.get(url,proxies=proxies,timeout=10)
        print(f"page {i}th reviews----------------------------------------------------------------")
        soup = BeautifulSoup(response.text, "html.parser")
        reviews = soup.find_all("div", class_="cPHDOP col-12-12")

        for review in reviews:
            rating_tag = review.select_one("div.XQDdHH")
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

            comment_tag = review.select_one("div.ZmyHeo div div")
            comment = comment_tag.get_text(separator=" ", strip=True) if comment_tag else "N/A"
            if rating and comment and rating!='N/A' and comment!='N/A':
                ratings.append(rating)
                comments.append(comment)
            # print(f"⭐️ Rating: {rating}")
            # print(f"💬 Comment: {comment}")
            # print("-" * 50)


    
# Convert to DataFrame
    df = pd.DataFrame({
    'score': ratings,
    'text': comments
})

    df.to_csv("flipkart_reviews.csv", index=False)
    print("✅ Saved to flipkart_reviews.csv")
except Exception as e:
    print(e)
