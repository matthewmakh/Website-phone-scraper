# Website-phone-scraper
given a list of url's this program will go through the website and look for specific keyword links. it will then follow those links and look for phone numbers.

This project is designed to scrape websites for "Contact Us", "Team", or similar pages to extract phone numbers and relevant contact details. It uses:
- `requests` to fetch web pages.
- `BeautifulSoup` to parse and extract HTML elements.
- `re` (regular expressions) to identify and clean phone numbers.
- `csv` to store extracted phone numbers in a structured format.

Features included in this commit:
- Fetching website content while ensuring proper URL formatting.
- Searching for relevant contact-related pages within a site.
- Extracting and cleaning phone numbers.
- Avoiding duplicates and appending new numbers to an existing CSV file.


