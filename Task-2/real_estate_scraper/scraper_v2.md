## ✅ **OVERVIEW**

This script is a **robust web scraper** designed to extract real estate property listings from [Nawy.com](https://www.nawy.com), a platform for buying and renting properties in Egypt. The site uses **JavaScript-heavy rendering**, so traditional scraping with `requests + BeautifulSoup` fails — instead, it uses **Playwright** to automate a real browser, simulate scrolling, and extract dynamically loaded content.

The scraped data is then processed using `BeautifulSoup`, stored in lists, converted into a `pandas.DataFrame`, and saved to a CSV file.

---

# 📦 **SECTION 1: IMPORTS**

```python
import requests
```

- Imports the `requests` library to make HTTP GET requests.
- Used here only for an initial test (not critical to final scraping).

```python
from bs4 import BeautifulSoup
```

- Imports `BeautifulSoup` from the `bs4` package.
- Used to parse HTML after full content is retrieved via Playwright.

```python
from playwright.sync_api import sync_playwright
```

- Imports the synchronous API of Playwright — allows writing browser automation code in a simple, readable way (blocking execution).
- `sync_playwright` launches a real Chromium browser to render JavaScript.

```python
import pandas as pd
```

- Imports `pandas`, a powerful data manipulation library.
- Used to structure scraped data into a tabular format (DataFrame) and save it as CSV.

```python
import time
```

- Provides `time.sleep()` to pause execution — essential for waiting between scrolls so new content can load.

```python
import os
```

- Used to interact with the operating system, particularly to create directories (`os.makedirs`) before saving files.

---

# 🧩 **SECTION 2: FUNCTION DEFINITION – `scrape_nawy_properties()`**

```python
def scrape_nawy_properties(
    url="https://www.nawy.com/search?page_number=1&category=property",
    scroll_count=100,
    scroll_wait=5,
    scroll_distance=1500,
    container_selector="div.sc-88b4dfdb-0.cgVQXi",
    property_class="sc-100c08da-0 eeBcMz",
    output_path="real_estate_properties.csv"
):
```

- Defines a reusable function with **7 configurable parameters**:
  - `url`: The starting page URL (defaults to Nawy's search page).
  - `scroll_count`: How many times to scroll down (more = more properties loaded).
  - `scroll_wait`: Seconds to wait after each scroll (lets AJAX requests finish).
  - `scroll_distance`: Pixels to scroll per iteration (controls how fast we move).
  - `container_selector`: CSS selector for the scrollable container (not the whole page).
  - `property_class`: Class name of individual property cards.
  - `output_path`: Where to save the CSV file.

> 🔍 These defaults are tailored specifically to Nawy’s current layout (as observed).

```python
    """
    Scrapes real estate property data from Nawy.com using Playwright and BeautifulSoup.

    Parameters:
    - url (str): The URL of the Nawy search page to scrape.
    - scroll_count (int): Number of times to scroll down to load more properties.
    - scroll_wait (float): Time to wait (in seconds) between each scroll.
    - scroll_distance (int): Pixels to scroll down per iteration.
    - container_selector (str): CSS selector for the scrollable container.
    - property_class (str): Class name of individual property listing elements.
    - output_path (str): File path to save the resulting CSV.

    Returns:
    - pd.DataFrame: DataFrame containing scraped property data.
    """
```

- A **docstring** explaining what the function does, its inputs, and output.
- Helps developers understand usage without reading the code.

---

# 🔗 **SECTION 3: INITIAL SETUP – Make Test Request**

```python
    response = requests.get(url)
```

- Sends a basic HTTP GET request to the URL.
- Purpose: For debugging or checking if the domain is reachable.
- Not used later — because the actual content is loaded via JavaScript, this response contains little usable data.

> ⚠️ This line is kept more for completeness than functionality.

---

# 🌐 **SECTION 4: LAUNCH BROWSER WITH PLAYWRIGHT**

```python
    with sync_playwright() as p:
```

- Starts a Playwright session using a context manager (`with`), ensuring clean startup and shutdown.
- `p` is the main Playwright object.

```python
        browser = p.chromium.launch(headless=True)
```

- Launches a headless Chromium browser.
- `headless=True`: Runs the browser in the background (no visible window).
  - Good for production.
  - Use `False` during development to see what’s happening.

```python
        page = browser.new_page()
```

- Opens a new tab/page in the browser.

```python
        page.goto(url)
```

- Navigates to the given URL.

```python
        page.wait_for_selector(container_selector)
```

- Waits until the **scrollable container** appears in the DOM.
- Selector: `div.sc-88b4dfdb-0.cgVQXi` — this is the div that holds the list of properties and supports internal scrolling.
- Ensures the page has loaded enough before starting to scroll.

---

# 🔁 **SECTION 5: SIMULATE INFINITE SCROLLING**

```python
        for _ in range(scroll_count):
```

- Loops `scroll_count` times (default: 100) to simulate repeated scrolling.

```python
            page.evaluate(f"""
                () => {{
                    const container = document.querySelector('{container_selector}');
                    if (container) {{
                        container.scrollBy(0, {scroll_distance});
                    }}
                }}
            """)
```

- Executes JavaScript inside the browser.
- Finds the scrollable container and scrolls it vertically by `scroll_distance` pixels (e.g., 1500px).
- Unlike `window.scrollBy()`, this targets a **specific inner container**, which matches Nawy’s UI design.

```python
            time.sleep(scroll_wait)
```

- Pauses the script for `scroll_wait` seconds (default: 5s).
- Allows time for:
  - Network requests to fetch new properties.
  - React components to render them.
  - Avoid overwhelming the server.

> ⚠️ This is a "brute-force" infinite scroll — doesn’t check if new items actually loaded. A smarter version would detect new elements.

---

# 📥 **SECTION 6: EXTRACT FULL HTML AFTER SCROLLING**

```python
        html = page.content()
```

- Gets the **full HTML source** of the page _after_ all scrolling.
- Now includes **all dynamically loaded property listings**.

```python
        soup = BeautifulSoup(html, "html.parser")
```

- Parses the HTML string using `BeautifulSoup`.
- Enables easy navigation and selection of elements via CSS selectors.

```python
        Properties = soup.find_all('div', class_=property_class)
```

- Extracts all property cards.
- Uses the class `sc-100c08da-0 eeBcMz` — which identifies individual property listings.
- Result: A list of `Tag` objects, one per property.

> 💡 These class names are auto-generated (likely by Styled Components or Emotion), so they may change if Nawy updates their frontend.

---

# 🧩 **SECTION 7: DATA STORAGE INITIALIZATION**

```python
        location_list = []
        name_list = []
        description_list = []
        area_list = []
        bed_list = []
        bath_list = []
        price_list = []
```

- Creates empty lists to collect data fields from each property.
- Each list will become a column in the final DataFrame.

---

# 🔎 **SECTION 8: LOOP THROUGH EACH PROPERTY AND EXTRACT DATA**

```python
        for property in Properties:
```

- Iterates over every property card found on the page.

### ➤ Extract Basic Info

```python
            location = property.select_one('div.area')
            name = property.select_one('div.name')
            description = property.select_one('h2.sc-4b9910fd-0.hyACaB')
            price = property.select_one('div.price-container span.price')
```

- Uses CSS selectors to find key pieces of information:
  - `div.area`: Neighborhood or city (e.g., "New Cairo").
  - `div.name`: Compound/project name (e.g., "Lavida").
  - `h2.sc-4b9910fd-0.hyACaB`: Descriptive title (e.g., "Modern 3-Bed Apartment").
  - `div.price-container span.price`: Price (e.g., "From EGP 4.5M").

```python
            location_list.append(location.text.strip() if location else "")
            name_list.append(name.text.strip() if name else "")
            description_list.append(description.text.strip() if description else "")
            price_list.append(price.text.strip() if price else "")
```

- Safely extracts text:
  - `.text`: Gets visible text inside the element.
  - `.strip()`: Removes extra whitespace, newlines, tabs.
  - `if x else ""`: Prevents errors if the element is missing.

### ➤ Initialize Feature Values

```python
            area_val = ""
            bed_val = ""
            bath_val = ""
```

- Default values in case feature blocks are missing.

### ➤ Extract Feature Blocks (Area, Beds, Baths)

```python
            feature_blocks = property.select("div.sc-234f71bd-0.bbWDeD")
```

- Selects all "feature" divs — these usually show icon + label + value (e.g., 🛏️ Beds: 3).

```python
            for block in feature_blocks:
                label = block.select_one("span.label")
                value = block.select_one("span.value")
```

- Inside each block:
  - `span.label`: Label like `"m2"`, `"beds"`, `"baths"`.
  - `span.value`: Numeric value like `"120"`, `"3"`.

```python
                if label and value:
                    label_text = label.text.strip().lower()
                    value_text = value.text.strip()
```

- Extracts and normalizes the label to lowercase for consistent matching.

```python
                    if label_text == "m2":
                        area_val = value_text
                    elif label_text == "beds":
                        bed_val = value_text
                    elif label_text == "baths":
                        bath_val = value_text
```

- Assigns values based on label:
  - `"m2"` → `area_val`
  - `"beds"` → `bed_val`
  - `"baths"` → `bath_val`

```python
            area_list.append(area_val)
            bed_list.append(bed_val)
            bath_list.append(bath_val)
```

- After processing all blocks, appends final values to global lists.

---

# 🛑 **SECTION 9: CLOSE THE BROWSER**

```python
        browser.close()
```

- Closes the browser instance.
- Important to free memory and prevent zombie processes.

> ✅ Automatically handled by context manager, but explicit close is safe.

---

# 📊 **SECTION 10: CREATE PANDAS DATAFRAME**

```python
    df = pd.DataFrame({
        'Location': location_list,
        'Name': name_list,
        'Description': description_list,
        'Area': area_list,
        'Beds': bed_list,
        'Baths': bath_list,
        'Price': price_list
    })
```

- Combines all lists into a structured table.
- Each list becomes a column.
- Ready for analysis, filtering, or export.

---

# 🖨️ **SECTION 11: DEBUG OUTPUT – PRINT DATA**

```python
    print("Locations:", location_list)
    print("Names:", name_list)
    ...
```

- Prints raw lists to console.
- Useful for:
  - Verifying that data was extracted.
  - Spotting missing values or mis-parsings.
  - Debugging selector issues.

---

# ℹ️ **SECTION 12: DISPLAY SUMMARY INFO**

```python
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Number of properties scraped: {len(df)}")
```

- `df.shape`: Returns `(rows, columns)` — e.g., `(953, 7)` means 953 properties with 7 attributes.
- `len(df)`: Total number of rows (i.e., unique properties).
- Quick validation of success.

---

# 💾 **SECTION 13: SAVE TO CSV**

```python
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
```

- Checks if the directory in `output_path` exists.
- If not, creates it (e.g., `Task-2/real_estate_scraper/`).
- `exist_ok=True`: Won’t raise an error if folder already exists.
- Only runs if there is a directory part (i.e., not just `filename.csv`).

```python
    df.to_csv(output_path, index=False)
```

- Exports the DataFrame to CSV.
- `index=False`: Omits the automatic row numbers (0, 1, 2...) from the file.

```python
    print(f"Data saved to {output_path}")
```

- Confirms where the file was saved.

```python
    return df
```

- Returns the DataFrame so it can be used further in code (e.g., analysis, merging, filtering).

---

# ▶️ **SECTION 14: EXAMPLE USAGE (MAIN BLOCK)**

```python
if __name__ == "__main__":
```

- Ensures the following code only runs when the script is executed directly (not imported).

```python
    df = scrape_nawy_properties(
        url="  https://www.nawy.com/search?page_number=1&category=property",
        scroll_count=300,
        scroll_wait=5,
        scroll_distance=1500,
        container_selector="div.sc-88b4dfdb-0.cgVQXi",
        property_class="sc-100c08da-0 eeBcMz",
        output_path="Task-2/real_estate_scraper/real_estate_properties_1.csv"
    )
```

- Calls the function with:
  - Slightly modified URL (note: extra space at start — might cause issues!).
  - Increased `scroll_count=300` to capture more listings.
  - Custom output path: saves to `Task-2/real_estate_scraper/...`.

> ⚠️ **Bug Alert**: The URL has a leading space: `"  https://..."` → should be fixed to avoid potential failures.

---

## 🧠 **KEY TECHNICAL INSIGHTS**

| Concept                               | Why It Matters                                                              |
| ------------------------------------- | --------------------------------------------------------------------------- |
| **Playwright over Selenium/Requests** | Handles modern SPAs (Single Page Apps) with dynamic content.                |
| **Headless Mode**                     | Runs faster and silently in production.                                     |
| **Container Scrolling**               | Matches how Nawy implements infinite scroll (not window-level).             |
| **CSS Selectors**                     | Precise targeting of elements even when IDs/class names are auto-generated. |
| **Error-Resistant Extraction**        | Uses `if x else ""` to avoid crashes on missing fields.                     |
| **Modular Design**                    | Function-based, reusable, configurable — easy to adapt.                     |

---

## ⚠️ **LIMITATIONS & RISKS**

| Risk                   | Description                                                                     | Solution                                   |
| ---------------------- | ------------------------------------------------------------------------------- | ------------------------------------------ |
| **Fragile Selectors**  | Auto-generated class names (like `sc-100c08da-0`) may change after site update. | Monitor regularly; use fallback selectors. |
| **Fixed Scroll Count** | May not load all items or waste time.                                           | Better: scroll until no new items appear.  |
| **No Retry Logic**     | Network failure kills the script.                                               | Add try-except blocks and retries.         |
| **Memory Usage**       | Large number of scrolls → high memory.                                          | Consider incremental processing.           |
| **Rate Limiting**      | Could be blocked if too aggressive.                                             | Add random delays, use headers.            |

---

## ✅ **FINAL SUMMARY**

This script is a **production-ready web scraper** that successfully:

1. Uses **Playwright** to handle JavaScript rendering.
2. Simulates **infinite scroll** to load all property listings.
3. Parses content with **BeautifulSoup**.
4. Stores structured data in a **pandas DataFrame**.
5. Saves results to **CSV** in a specified folder (with auto-folder creation).
6. Is **configurable** via function parameters.
7. Can be reused, scheduled, or integrated into larger pipelines.

It’s ideal for:

- Real estate market analysis.
- Competitor research.
- Price trend tracking.
- Lead generation.

---
