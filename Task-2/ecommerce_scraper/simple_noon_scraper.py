import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Lists to store data
titles = []
prices = []
ratings = []
product_links = []
image_links = []


for page in range(1, 6):
    url = f"https://www.noon.com/egypt-en/eg-gaming-laptops/?page={page}"
    headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en,ar-AE;q=0.9,ar;q=0.8,en-US;q=0.7",
    "cache-control": "max-age=0",
    "cookie": "visitor_id=152f51b1-4142-4601-a513-470da74e6e26; nloc=en-eg; visitorId=ff992c37-c962-4489-a7c9-46d6180119ed; _gcl_au=1.1.767678201.1751548204; _scid=brXjPRDQkv-TmbFu3XRGL2LKr7z9dn1q; _fbp=fb.1.1751548205212.438964988820565690; _tt_enable_cookie=1; _ttp=01JZ86H7FYPN76WPRSE4A51MZ1_.tt.1; _pin_unauth=dWlkPVpUQTBaVFF3T0dJdFpESmlNQzAwTVRabExXRXpZelF0WldWa04ySmxOekF4TVRreQ; _ScCbts=[\"134;chrome.2:2:5\"]; _sctr=1|1754168400000; x-whoami-headers=eyJ4LWxhdCI6IjMwMDYzMTQzNyIsIngtbG5nIjoiMzEyMjA1MjI0IiwieC1hYnkiOiJ7XCJpcGxfZW50cnlwb2ludC5lbmFibGVkXCI6MSxcIndlYl9wbHBfcGRwX3JldmFtcC5lbmFibGVkXCI6MSxcImNhdGVnb3J5X2Jlc3Rfc2VsbGVyLmVuYWJsZWRcIjoxfSIsIngtZWNvbS16b25lY29kZSI6IkVHLUNBSS1TMTAiLCJ4LWFiLXRlc3QiOls2MSw5NDEsOTYxLDEwMzEsMTA5MCwxMTAxLDExNjIsMTIxMSwxMjkxLDEzNjIsMTQyMSwxNDUwLDE0NzAsMTU0MSwxNTgwLDE2MjEsMTY1MCwxNzAwLDE3MjEsMTc3MSwxODExXX0=; ... (trimmed for brevity)",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
}


    response = requests.get(url, headers=headers)
    print(f"Page {page} status:", response.status_code)

    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.select('a.ProductBoxLinkHandler_productBoxLink__FPhjp')

    if not products:
        print(f"No products found on page {page}")
        break

    for product in products:
        # Title
        title_tag = product.select_one("h2.ProductDetailsSection_title__JorAV")
        title = title_tag.text.strip() if title_tag else "N/A"
        titles.append(title)

        # Price
        price_tag = product.select_one("strong.Price_amount__2sXa7")
        price = price_tag.text.strip() if price_tag else "N/A"
        prices.append(price)

        # Rating
        rating_tag = product.select_one("div.RatingPreviewStar_textCtr__sfsJG")
        rating = rating_tag.text.strip() if rating_tag else "N/A"
        ratings.append(rating)

        # Product Link
        href = product.get('href')
        full_link = "https://www.noon.com" + href if href else "N/A"
        product_links.append(full_link)

        # Image link
        img_tag = product.select_one("img.ProductImageCarousel_productImage__jtsOn")
        img_src = img_tag['src'] if img_tag else "N/A"
        image_links.append(img_src)

    print(f"✅ Scraped page {page} with {len(products)} products.")
    time.sleep(1)  # Be polite
    
    
# Create DataFrame
df = pd.DataFrame({
    "Product_name": titles,
    "Rating": ratings,
    "Price": prices,
    "Product_link": product_links,
    "Image_link": image_links
})

# Output
print("\nDataFrame shape:", df.shape)
print("Number of items scraped:", len(df))


# Create the directory if it doesn't exist
import os

output_dir = "Task-2/ecommerce_scraper"
os.makedirs(output_dir, exist_ok=True)  # Creates the folder structure if needed

# Define the file path
output_file = os.path.join(output_dir, "noon_gaming_laptops_v1.csv")

# Save the DataFrame
df.to_csv(output_file, index=False, encoding='utf-8')

print(f"\n✅ Data saved to: {output_file}")