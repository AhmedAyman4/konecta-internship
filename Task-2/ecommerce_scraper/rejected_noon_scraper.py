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
        "User-Agent": "Mozilla/5.0"
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