## 🧩 **Overview of the Script**

This script scrapes product data (title, price, rating, link, image) for **gaming laptops** from `noon.com` (Egypt version), across **5 pages** of search results. Since `noon.com` uses **JavaScript to load content dynamically**, it uses **Playwright** to render the full page (like a real browser), then **BeautifulSoup** to parse the HTML and extract data. Finally, it saves the results into a **CSV file** using **Pandas**.

---

## ✅ **Step-by-Step Explanation**

### 1. **Import Required Libraries**

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
```

- `playwright.sync_api.sync_playwright`: Controls a real browser (Chromium) to load JavaScript-heavy pages.
- `BeautifulSoup`: Parses HTML and extracts data using CSS selectors.
- `pandas`: Handles data in a tabular format (DataFrame) and exports to CSV.
- `time`: Adds delays between requests to avoid overwhelming the server.

---

### 2. **Initialize Empty Lists to Store Data**

```python
titles = []
prices = []
ratings = []
product_links = []
image_links = []
```

These lists will store scraped data for each product. Each list corresponds to one column in the final CSV.

---

### 3. **Define the Base URL with Page Placeholder**

```python
base_url = "https://www.noon.com/egypt-en/eg-gaming-laptops/?page={page}"
```

- This is the URL pattern for the search results.
- `{page}` is a placeholder that will be replaced with numbers 1–5.
- Example: When `page=1`, the full URL becomes:
  ```
  https://www.noon.com/egypt-en/eg-gaming-laptops/?page=1
  ```

> 🔍 Note: The path `/eg-gaming-laptops/` may not be accurate. It's better to verify this manually on the site.

---

### 4. **Start Playwright Context (Browser Automation)**

```python
with sync_playwright() as p:
```

- Starts the Playwright session.
- The `with` statement ensures proper cleanup (browser closes even if an error occurs).

---

### 5. **Launch Chromium Browser**

```python
browser = p.chromium.launch(headless=False, timeout=60000)
```

- Launches a real Chromium browser.
- `headless=False`: Shows the browser window (useful for debugging).
  - Set to `True` later for faster, invisible scraping.
- `timeout=60000`: Wait up to 60 seconds for the browser to launch.

---

### 6. **Create a Browser Context with Custom Settings**

```python
page_context = browser.new_context(
    viewport={"width": 1920, "height": 1080},
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
)
```

- `new_context()`: Creates an isolated browsing session (like a private window).
- `viewport`: Sets the browser window size to simulate a real user.
- `user_agent`: Spoofs the request to look like a real Chrome browser (avoids bot detection).

---

### 7. **Open a New Page (Tab)**

```python
page = page_context.new_page()
```

- Opens a new tab where we'll navigate and scrape.

---

### 8. **Loop Through 5 Pages of Results**

```python
for current_page in range(1, 6):
    url = base_url.format(page=current_page)
    print(f"Scraping page {current_page}: {url}")
```

- Loops from page 1 to 5.
- Formats the URL with the current page number.
- Prints which page is being scraped.

---

### 9. **Navigate to the Page and Wait for Content**

```python
page.goto(url, timeout=60000, wait_until="networkidle")
```

- Loads the URL in the browser.
- `timeout=60000`: Wait up to 60 seconds.
- `wait_until="networkidle"`: Wait until **no network requests** are made for 500ms — ensures all products are loaded.

> 💡 This is crucial for JavaScript-heavy sites like noon.com.

---

### 10. **Wait for Product Elements to Appear**

```python
page.wait_for_selector("div.ProductBoxLinkHandler_linkWrapper__b0qZ9", timeout=10000)
```

- Waits for at least one product container to appear.
- Prevents parsing before content loads.
- If not found within 10 seconds, raises an error (caught in `try-except`).

---

### 11. **Get Full Page HTML After JS Loads**

```python
html = page.content()
soup = BeautifulSoup(html, "html.parser")
```

- `page.content()` gets the **fully rendered HTML** (after JavaScript executed).
- `BeautifulSoup` parses this HTML for easy data extraction.

> 🔁 This is the key advantage: **Playwright renders**, **BeautifulSoup extracts**.

---

### 12. **Find All Product Containers**

```python
products = soup.find_all("div", class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")
```

- Finds all product boxes on the page.
- Uses the class name that wraps each product listing.

> ⚠️ Warning: Class names like `ProductBoxLinkHandler_linkWrapper__b0qZ9` are auto-generated and may change. They are **fragile**.

---

### 13. **Handle Case When No Products Are Found**

```python
if not products:
    print(f"No products found on page {current_page}")
    continue
```

- Skips to the next page if no products are detected.

---

### 14. **Loop Through Each Product and Extract Data**

#### 🔹 **Title**

```python
title_tag = product.select_one("h2.ProductDetailsSection_title__JorAV")
title = title_tag.get_text(strip=True) if title_tag else "N/A"
titles.append(title)
```

- Finds the `<h2>` with the product name.
- `.get_text(strip=True)` removes extra whitespace.
- Appends to `titles` list.

#### 🔹 **Price**

```python
price_tag = product.select_one("strong.Price_amount__2sXa7")
price = price_tag.get_text(strip=True) if price_tag else "N/A"
prices.append(price)
```

- Gets the price from `<strong>` tag.
- Common pattern on e-commerce sites.

#### 🔹 **Rating**

```python
rating_tag = product.select_one("span.RatingPreviewStar_textCtr__sfsJG")
rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
ratings.append(rating)
```

- Extracts the star rating (e.g., "4.5").
- May not appear if no reviews exist.

#### 🔹 **Product Link**

```python
link_tag = product.select_one('a.ProductBoxLinkHandler_productBoxLink__FPhjp')
if link_tag and 'href' in link_tag.attrs:
    product_link = "  https://www.noon.com  " + link_tag['href']
else:
    product_link = "N/A"
product_links.append(product_link)
```

- ❌ **Bug**: Extra spaces in URL: `"  https://www.noon.com  "`
- ✅ Should be: `"https://www.noon.com"`
- Also, `href` may already be absolute (check manually).

> ✅ **Fix**:
>
> ```python
> product_link = "https://www.noon.com" + link_tag['href']
> ```

#### 🔹 **Image Link**

```python
img_tag = product.select_one('img.ProductImageCarousel_productImage__jtsOn')
if img_tag:
    image_link = img_tag.get('src') or img_tag.get('data-src', 'N/A')
else:
    image_link = "N/A"
image_links.append(image_link)
```

- Gets image URL.
- Uses `src` first, falls back to `data-src` (used in lazy loading).
- Good practice!

---

### 15. **Add Delay Between Requests**

```python
time.sleep(2)
```

- Waits 2 seconds between pages.
- Prevents overwhelming the server (good etiquette).
- Helps avoid IP blocking.

---

### 16. **Close the Browser**

```python
browser.close()
```

- Closes the browser after scraping.
- Important to free up system resources.

---

### 17. **Create a Pandas DataFrame**

```python
df = pd.DataFrame({
    "Product_name": titles,
    "Rating": ratings,
    "Price": prices,
    "Product_link": product_links,
    "Image_link": image_links
})
```

- Combines all lists into a structured table.
- Each list becomes a column.

---

### 18. **Print Summary Information**

```python
print("\nDataFrame shape:", df.shape)
print("Number of items scraped:", len(df))
```

- `.shape` shows (rows, columns) — e.g., `(50, 5)` means 50 products.
- Confirms how much data was collected.

---

### 19. **Save Data to CSV**

```python
try:
    df.to_csv("Task-2/ecommerce_scraper/noon_gaming_laptops.csv", index=False)
    print("\n✅ CSV file saved as 'noon_gaming_laptops.csv'")
except Exception as e:
    print(f"❌ Error saving CSV: {e}")
```

- Saves the DataFrame to a CSV file.
- `index=False`: Don’t include row numbers.
- Uses `try-except` to handle file path errors (e.g., folder doesn't exist).

> ⚠️ Make sure the folder `Task-2/ecommerce_scraper/` exists, or it will fail.

> ✅ Alternative (safer):
>
> ```python
> df.to_csv("noon_gaming_laptops.csv", index=False)
> ```

---

## 🛠️ **Potential Issues & Fixes**

| Issue                   | Fix                                                                        |
| ----------------------- | -------------------------------------------------------------------------- |
| **Wrong or broken URL** | Manually verify the correct URL for gaming laptops on `noon.com/egypt-en`  |
| **Dynamic class names** | Use more stable selectors like `[data-test="..."]` if available            |
| **Spaces in URL**       | Remove extra spaces: `"https://www.noon.com"` not `"  https://...  "`      |
| **Missing folder**      | Create `Task-2/ecommerce_scraper/` or save to current directory            |
| **Blocking**            | Add random delays, rotate user agents, or use proxies if scraping at scale |

---

## ✅ **Best Practices Used**

- ✅ Uses **Playwright** for JavaScript rendering.
- ✅ Uses **BeautifulSoup** for easy parsing.
- ✅ Handles errors with `try-except`.
- ✅ Waits for content to load (`wait_for_selector`, `networkidle`).
- ✅ Respects server with `time.sleep()`.
- ✅ Saves structured data in CSV.

---

## 📌 Final Thoughts

This script is **well-structured** and effective for scraping dynamic websites like `noon.com`. With minor fixes (URL, class names, image links), it should work reliably.

---
