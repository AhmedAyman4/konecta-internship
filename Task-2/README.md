**Web Scraping Task – E-Commerce Product Data Collection**

**Objective**  
Your task is to build a Python-based web scraper using BeautifulSoup that collects structured product data from an e-commerce website of your choice (e.g., Jumia, Amazon, Newegg, etc.). The final goal is to compile the extracted data into a clean CSV file or Pandas DataFrame for further analysis.

**Requirements**  
Your scraper should extract the following details for at least 100 products in a specific category (e.g., laptops, shoes, books):

- Product Name / Title
- Price
- Product Rating (if available)
- Number of Reviews (if available)
- Product URL
- Image URL
- Brand (if available)

**Tips and Guidelines**

- Use the browser's developer tools (Inspect Element) to examine the HTML structure of the page.
- Right-click an item (e.g., product name or price) → “Inspect” to find its tag, class, or ID.
- Use Ctrl+F inside the HTML inspector to search for repeated tags (like `<div class="product-name">`).
- Identify patterns in the HTML that can help you loop through product cards.
- Start with one page. Once it works, implement logic to navigate through multiple pages if the site uses pagination (e.g., “Next” button or page numbers).
- Use headers in your requests to mimic a browser (to avoid bot detection).
- Respect the website's robots.txt policy. You can check it by visiting `www.website.com/robots.txt`.
- If the site loads content with JavaScript (content not visible in page source), BeautifulSoup might not work well — skip such sites for now or switch to a simpler one.
