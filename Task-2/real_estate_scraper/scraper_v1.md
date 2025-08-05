### 📦 **Section 1: Import Statements**

```python
# ================================
# IMPORTS
# ================================
# Import required libraries for web scraping, browser automation, and data handling
import requests
```

- `requests`: A Python library used to send HTTP requests. Here it's used to make an initial GET request to the website (though not used in final scraping due to JavaScript rendering).

```python
from bs4 import BeautifulSoup
```

- `BeautifulSoup`: A library for parsing HTML and XML documents. It’s used later to parse the full HTML retrieved by Playwright.

```python
from playwright.sync_api import sync_playwright
```

- `playwright`: A powerful browser automation tool that can control a real Chromium browser. The `sync_playwright` allows synchronous (blocking) execution — easier to read and debug.

```python
import pandas as pd
```

- `pandas`: A data analysis and manipulation library. Used here to store scraped data in a structured DataFrame and save it as CSV.

```python
import time
```

- `time`: Provides time-related functions. Used here with `time.sleep()` to pause between scrolls so the page has time to load dynamically loaded content.

---

### 🔗 **Section 2: Define Target URL and Initial Request**

```python
# ================================
# INITIAL SETUP
# ================================
# Define the target URL for the Nawy property search page (page 1)
url = "https://www.nawy.com/search?page_number=1&category=property"
```

- Sets the base URL for the Nawy property search.
- `page_number=1` indicates page 1; the site may load more results via infinite scroll.
- `category=property` filters results to real estate listings.

```python
# Make an initial GET request to the website (not used in final scraping but kept for reference)
response = requests.get(url)
```

- Sends an HTTP GET request to fetch the raw HTML of the page.
- However, since Nawy uses **client-side rendering (JavaScript)**, this response will likely contain minimal actual content — just placeholders or loading skeletons.
- This step is kept for debugging or initial inspection but is **not used** in the final data extraction.

---

### 🚫 **Section 3: Commented-Out BeautifulSoup Attempt**

```python
# ================================
# COMMENTED OUT BEAUTIFULSOUP ATTEMPT
# ================================
# The following lines were used for initial HTML inspection using requests and BeautifulSoup
# However, the site is heavily JavaScript-dependent, so this approach only retrieves minimal content
# soup = BeautifulSoup(response.text, "html.parser")
# print(soup.prettify())
```

- Tries to parse the HTML from the `requests.get()` response using BeautifulSoup.
- `soup.prettify()` would print formatted HTML — useful for debugging.
- But because the content is loaded via JavaScript after the page loads, this method fails to retrieve property listings.

```python
# Example of finding property elements (not used due to dynamic content)
# Properties = soup.find_all('div', class_='sc-40627e41-0 bZoDMX')
# print(Properties)
```

- This shows an attempt to locate property containers using a specific CSS class.
- But again, these elements are not present in the initial HTML fetched by `requests`, so nothing useful is found.

> ✅ Conclusion: `requests + BeautifulSoup` alone cannot scrape this site — we need a **browser automation tool** like Playwright.

---

### 🌐 **Section 4: Launch Browser with Playwright**

```python
# ================================
# LAUNCH BROWSER WITH PLAYWRIGHT
# ================================
# Use Playwright to launch a Chromium browser instance for full JavaScript rendering
with sync_playwright() as p:
```

- Starts a Playwright session using context manager (`with`), ensuring clean shutdown.
- `p` is the Playwright object providing access to browsers.

```python
    # Launch the browser in non-headless mode (visible window)
    browser = p.chromium.launch(headless=False)
```

- Launches a real Chromium browser (like Chrome).
- `headless=False` means the browser window is visible — useful for debugging and seeing what’s being loaded.

```python
    # Open a new browser page
    page = browser.new_page()
```

- Creates a new tab/page in the browser where navigation and interaction will happen.

```python
    # Navigate to the target URL
    page.goto(url)
```

- Loads the specified URL (`https://www.nawy.com/search?...`) in the browser.

```python
    # Wait until the scrollable container (which holds the property listings) is loaded
    page.wait_for_selector("div.sc-88b4dfdb-0.cgVQXi")
```

- Waits until a specific element appears on the page — the scrollable container that holds the list of properties.
- This ensures the page has finished loading at least the first batch of listings before scrolling begins.
- Uses a **CSS selector** based on the unique class name of that container.

---

### 🔁 **Section 5: Simulate Infinite Scroll**

```python
    # ================================
    # INFINITE SCROLL SIMULATION
    # ================================
    # Scroll down inside the scrollable container multiple times to load all properties
    for _ in range(100):  # Repeat scroll action up to 100 times
```

- Loops 100 times to simulate scrolling many times, attempting to load all available properties.
- The number 100 is arbitrary — high enough to load most or all listings if they load incrementally.

```python
        page.evaluate("""
            () => {
                const container = document.querySelector('div.sc-88b4dfdb-0.cgVQXi');
                if (container) {
                    container.scrollBy(0, 1500);  // Scroll down by 1500px each time
                }
            }
        """)
```

- Executes JavaScript inside the browser.
- Finds the scrollable container (`div.sc-88b4dfdb-0.cgVQXi`) and scrolls it down by 1500 pixels vertically.
- Unlike `window.scrollBy()`, this scrolls **inside the container**, which is how the site implements infinite scroll.

```python
        time.sleep(5)  # Wait 5 seconds between scrolls to allow content to load
```

- Pauses the script for 5 seconds after each scroll.
- Gives time for:
  - New property cards to be fetched from the server.
  - Rendered into the DOM.
  - Avoid overwhelming the network or missing content.

> ⚠️ Note: This is a simple wait — not optimal, but effective. Better approaches use `page.wait_for_load_state()` or wait for new elements.

---

### 📥 **Section 6: Extract Full HTML After Scrolling**

```python
    # ================================
    # EXTRACT FULL PAGE HTML AFTER SCROLLING
    # ================================
    # After scrolling, retrieve the complete page HTML (now includes dynamically loaded content)
    html = page.content()
```

- Gets the **entire current HTML** of the page after all scrolling.
- Now includes all property listings that were loaded during the scroll simulation.

```python
    # Parse the HTML using BeautifulSoup for easier data extraction
    soup = BeautifulSoup(html, "html.parser")
```

- Passes the full HTML to `BeautifulSoup` for easy parsing using familiar methods like `.find_all()` and `.select()`.

```python
    # Find all property listing elements using the specific class name
    Properties = soup.find_all('div', class_='sc-100c08da-0 eeBcMz')
```

- Locates all individual property cards on the page.
- Each card is a `<div>` with classes `sc-100c08da-0 eeBcMz` — likely assigned via a React-style CSS-in-JS framework.

> 🔍 These class names are auto-generated (e.g., by Styled Components), so they change over time — this makes the scraper fragile unless updated.

---

### 🧩 **Section 7: Initialize Data Storage Lists**

```python
    # ================================
    # DATA STORAGE INITIALIZATION
    # ================================
    # Initialize empty lists to store extracted property data
    location_list = []
    name_list = []
    description_list = []
    area_list = []
    bed_list = []
    bath_list = []
    price_list = []
```

- Creates empty Python lists to collect data from each property.
- One list per field (Location, Name, Description, etc.).
- Will later be combined into a Pandas DataFrame.

---

### 🔎 **Section 8: Loop Through Each Property and Extract Data**

```python
    # ================================
    # EXTRACT DATA FROM EACH PROPERTY
    # ================================
    # Loop through each property element found on the page
    for property in Properties:
```

- Iterates over every property card found on the page.

#### ➤ Extract Basic Info

```python
        # Extract basic textual information using CSS selectors
        location = property.select_one('div.area')                    # Location of the property
        name = property.select_one('div.name')                       # Name/title of the property
        description = property.select_one('h2.sc-4b9910fd-0.hyACaB') # Description headline
        price = property.select_one('div.price-container span.price') # Price of the property
```

- Uses `select_one()` (from BeautifulSoup) with CSS selectors to find key elements inside each card:
  - `div.area`: The area or neighborhood (e.g., "New Cairo").
  - `div.name`: The project/compound name.
  - `h2.sc-4b9910fd-0.hyACaB`: The descriptive title (e.g., "Modern Villa with Pool").
  - `div.price-container span.price`: The displayed price (could be "From EGP 5M").

```python
        # Append text content if element exists; otherwise, append empty string
        location_list.append(location.text.strip() if location else "")
        name_list.append(name.text.strip() if name else "")
        description_list.append(description.text.strip() if description else "")
        price_list.append(price.text.strip() if price else "")
```

- Safely extracts `.text` from each element.
- `.strip()` removes extra whitespace, newlines, or tabs.
- Uses conditional expressions (`if location else ""`) to avoid errors when an element is missing.

#### ➤ Initialize Feature Values

```python
        # Initialize default values for area, beds, and baths
        area_val = ""
        bed_val = ""
        bath_val = ""
```

- Sets default values in case feature blocks are missing or incomplete.

#### ➤ Extract Feature Blocks (Area, Beds, Baths)

```python
        # ================================
        # EXTRACT FEATURE BLOCKS (AREA, BEDS, BATHS)
        # ================================
        # Some properties display additional details in labeled feature blocks
        feature_blocks = property.select("div.sc-234f71bd-0.bbWDeD")  # Select all feature blocks
```

- Selects all "feature" divs inside the property card — these usually show icons + labels like "120 m²", "3 Beds", "2 Baths".
- Class name `sc-234f71bd-0.bbWDeD` appears to be consistent across such blocks.

```python
        # Loop through each feature block (e.g., "m2", "beds", "baths")
        for block in feature_blocks:
            label = block.select_one("span.label")   # Label (e.g., "m2", "beds")
            value = block.select_one("span.value")   # Value (e.g., "120", "3")

            # If both label and value exist, process them
            if label and value:
                label_text = label.text.strip().lower()  # Normalize label to lowercase
                value_text = value.text.strip()

                # Match label to appropriate field and assign value
                if label_text == "m2":
                    area_val = value_text
                elif label_text == "beds":
                    bed_val = value_text
                elif label_text == "baths":
                    bath_val = value_text
```

- Loops through each feature block.
- Extracts:
  - `label`: The type of info (e.g., `"m2"`, `"beds"`).
  - `value`: The numeric or textual value (e.g., `"150"`, `"4"`).
- Normalizes the label to lowercase for reliable matching.
- Assigns the value to the correct variable (`area_val`, `bed_val`, `bath_val`) based on the label.

```python
        # Append extracted feature values to their respective lists
        area_list.append(area_val)
        bed_list.append(bed_val)
        bath_list.append(bath_val)
```

- After processing all blocks, appends the final values to the global lists.

---

### 🛑 **Section 9: Close the Browser**

```python
    # ================================
    # CLOSE BROWSER
    # ================================
    # Close the browser after scraping is complete
    browser.close()
```

- Closes the Chromium browser.
- Important to prevent zombie browser processes.
- Automatically handled by context manager (`with`), but explicit close is good practice.

---

### 🖨️ **Section 10: Debug Output – Print Scraped Data**

```python
# ================================
# DEBUG OUTPUT: PRINT SCRAPED DATA
# ================================
# Print all collected data to verify successful scraping
print("Locations:", location_list)
print("Names:", name_list)
print("Descriptions:", description_list)
print("Prices:", price_list)
print("Areas:", area_list)
print("Beds:", bed_list)
print("Baths:", bath_list)
```

- Prints all the collected lists to the console.
- Useful for:
  - Verifying that data was extracted.
  - Checking for missing or malformed entries.
  - Debugging selector issues.

---

### 📊 **Section 11: Create Pandas DataFrame**

```python
# ================================
# CREATE PANDAS DATAFRAME
# ================================
# Combine all data lists into a structured DataFrame
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

- Converts the seven lists into a tabular format using `pd.DataFrame`.
- Each list becomes a column.
- Makes data easy to analyze, filter, export, or visualize.

---

### ℹ️ **Section 12: Display DataFrame Info**

```python
# ================================
# DISPLAY DATAFRAME INFO
# ================================
# Print basic information about the scraped dataset
print(f"\nDataFrame shape: {df.shape}")
print(f"Number of properties scraped: {len(df)}")
```

- `df.shape`: Returns tuple `(rows, columns)` — e.g., `(953, 7)` meaning 953 properties scraped.
- `len(df)`: Number of rows (i.e., total properties).
- Helps verify the scale and success of the scrape.

---

### 💾 **Section 13: Save Data to CSV File**

```python
# ================================
# SAVE DATA TO CSV FILE
# ================================
# Save the DataFrame to a CSV file without the index column
df.to_csv('Task-2/real_estate_scraper/real_estate_properties.csv', index=False)
```

- Exports the DataFrame to a CSV file.
- Path: `Task-2/real_estate_scraper/real_estate_properties.csv`
- `index=False`: Prevents Pandas from writing row numbers (0, 1, 2...) as a column.
- Ensures data can be reloaded easily or used in other tools (Excel, Power BI, etc.).

> 🔒 If the folder doesn’t exist, this will raise an error. (To fix, use `os.makedirs()` as shown earlier.)

---

### ✅ **Section 14: Final Comment**

```python
# ================================
# END OF SCRIPT
# ================================
# The script has now scraped property data from Nawy, saved it to a CSV, and printed summary info.
```

- Summary comment indicating the script has completed its purpose:
  1. Opened a real browser.
  2. Scrolled to load all listings.
  3. Extracted structured data.
  4. Stored it in a clean CSV.

---

## 🧠 Summary of Key Concepts Used

| Concept                               | Purpose                                                                  |
| ------------------------------------- | ------------------------------------------------------------------------ |
| **Playwright**                        | To render JavaScript-heavy pages and simulate user behavior (scrolling). |
| **BeautifulSoup**                     | For fast, readable HTML parsing after full content is loaded.            |
| **Infinite Scroll Simulation**        | To trigger lazy-loaded content that doesn’t appear in initial HTML.      |
| **CSS Selectors**                     | To precisely target elements in the DOM.                                 |
| **Error Handling via `if x else ""`** | To prevent crashes when optional elements are missing.                   |
| **Pandas**                            | For structured data storage, analysis, and export.                       |

---

## ⚠️ Limitations & Risks

| Issue                  | Description                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| **Fragile Selectors**  | Auto-generated class names (like `sc-100c08da-0`) may change after site updates — breaking the scraper. |
| **Fixed Scroll Count** | Using `range(100)` may not load all items or waste time. Better: scroll until no new items appear.      |
| **No Error Handling**  | Script crashes if something fails (e.g., network issue, selector change).                               |
| **Hardcoded Paths**    | Output path assumes directory exists. Should create it programmatically.                                |

---

## ✅ Final Thoughts

This script is a **robust solution** for scraping a **JavaScript-rendered real estate site** like Nawy. It combines:

- Real browser automation (Playwright),
- Smart scrolling,
- Careful data extraction,
- Clean output.

It successfully bypasses the limitations of simple HTTP requests and delivers structured, exportable data — ideal for market analysis, price tracking, or lead generation.
