from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time

# Lists to store data
titles = []
prices = []
ratings = []
product_links = []
image_links = []

# URL base
base_url = "https://www.noon.com/egypt-en/eg-gaming-laptops/?page={page}"

# Start Playwright with Chromium
with sync_playwright() as p:
    # Launch browser (set headless=False if you want to see the browser)
    browser = p.chromium.launch(headless=False, timeout=60000)
    page_context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    )
    page = page_context.new_page()

    for current_page in range(1, 6):
        url = base_url.format(page=current_page)
        print(f"Scraping page {current_page}: {url}")

        try:
            # Navigate to the page
            page.goto(url, timeout=60000, wait_until="networkidle")  # Wait until network is idle

            # Optional: Wait for product containers to load
            page.wait_for_selector("div.ProductBoxLinkHandler_linkWrapper__b0qZ9", timeout=10000)

            # Get the HTML content after JS loads
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Find product containers
            products = soup.find_all("div", class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")

            if not products:
                print(f"No products found on page {current_page}")
                continue

            for product in products:
                # Title
                title_tag = product.select_one("h2.ProductDetailsSection_title__JorAV")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                titles.append(title)

                # Price
                price_tag = product.select_one("strong.Price_amount__2sXa7")
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                prices.append(price)

                # Rating
                rating_tag = product.select_one("span.RatingPreviewStar_textCtr__sfsJG")
                rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
                ratings.append(rating)

                # Product Link
                link_tag = product.select_one('a.ProductBoxLinkHandler_productBoxLink__FPhjp')
                if link_tag and 'href' in link_tag.attrs:
                    product_link = "https://www.noon.com" + link_tag['href']
                else:
                    product_link = "N/A"
                product_links.append(product_link)

                # Image Link (check src or data-src)
                img_tag = product.select_one('img.ProductImageCarousel_productImage__jtsOn')
                if img_tag:
                    image_link = img_tag.get('src') or img_tag.get('data-src', 'N/A')
                else:
                    image_link = "N/A"
                image_links.append(image_link)

            print(f"✅ Scraped page {current_page} with {len(products)} products.")

        except Exception as e:
            print(f"❌ Error on page {current_page}: {e}")
            continue

        time.sleep(2)  # Be respectful to the server

    # Close browser
    browser.close()

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

# Save to CSV
try:
    df.to_csv("Task-2/ecommerce_scraper/noon_gaming_laptops.csv", index=False)
    print("\n✅ CSV file saved as 'noon_gaming_laptops.csv'")
except Exception as e:
    print(f"❌ Error saving CSV: {e}")