import requests
from bs4 import BeautifulSoup
import re
import csv

# ---------- Step 1: Read URLs from CSV ----------
def get_urls_from_csv(file_path):
    """
    Reads URLs from a CSV file and detects the correct column (website or url).
    """
    urls = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in row:  # Check all column headers dynamically
                if key.lower() in ['website', 'url']:  # Match against common names
                    if row[key]:  # Ensure the value is not empty
                        urls.append(row[key].strip())
                    break  # Stop once a valid column is found
    return urls


# ---------- Step 2: Fetch Website Content ----------
def get_website(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url  # Default to HTTPS

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


# ---------- Step 3: Find Contact Pages ----------
def find_pages(html, base_url):
    """
    Find all links related to contact pages, team pages, about pages, etc.
    """
    soup = BeautifulSoup(html, 'lxml')
    links = set()  # Use a set to avoid duplicates
    keywords = [
        'contact', 'contact-us', 'support', 'help', 'get-in-touch', 'reach-us', 'customer-service',
        'assistance', 'connect', 'feedback', 'team', 'our-team', 'staff', 'people', 'leadership',
        'executives', 'founders', 'bios', 'meet-the-team', 'who-we-are', 'about', 'about-us',
        'our-story', 'company', 'mission', 'values', 'culture', 'overview', 'what-we-do', 'history',
        'location', 'locations', 'office', 'offices', 'find-us', 'visit', 'where-to-find-us',
        'map', 'headquarters', 'directions', 'directory', 'staff-directory', 'employee-directory',
        'partners', 'affiliates', 'advisors', 'network', 'contacts', 'list', 'profiles'
    ]

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if any(keyword in href.lower() for keyword in keywords):
            full_url = href if href.startswith("http") else base_url.rstrip('/') + href
            links.add(full_url)

    return list(links)  # Convert back to list for compatibility


# ---------- Step 4: Extract Phone Numbers and Emails ----------
def extract_numbers(html):
    """
    Extracts all phone numbers and emails from a webpage's HTML.
    """
    soup = BeautifulSoup(html, 'lxml')

    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s*(?:Ext\.?|x)\s*\d{1,5})?'
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    text_content = soup.get_text(separator=" ", strip=True)
    phone_numbers = set(re.findall(phone_pattern, text_content))
    email_addresses = set(re.findall(email_pattern, text_content))

    return {'phone_numbers': list(phone_numbers), 'email_addresses': list(email_addresses)}


# ---------- Step 5: Scrape Website Data ----------
def scrape_website(base_url):
    """
    Scrapes multiple "contact-related" pages from a website and extracts phone numbers & emails.
    """
    html = get_website(base_url)
    if not html:
        print("Failed to fetch the base URL.")
        return []

    links = find_pages(html, base_url)
    if not links:
        print("No relevant links found.")
        return []

    all_data = []

    for i in links:
        print(f'Visiting: {i}')
        page_html = get_website(i)
        if not page_html:
            continue

        data = extract_numbers(page_html)
        all_data.append(data)

    return all_data


# ---------- Main Execution ----------
input_csv = "/Users/matthewmakh/Desktop/Numbers_to_send_copy.csv"  # CSV input file path
urls = get_urls_from_csv(input_csv)

unique_numbers = set()
unique_emails = set()

for url in urls:
    results = scrape_website(url)

    for result in results:
        unique_numbers.update(result['phone_numbers'])
        unique_emails.update(result['email_addresses'])

# ---------- Save Results to CSV ----------
output_file = "unique_contacts.csv"  # Output file path

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Phone Numbers', 'Email Addresses'])  # Header

    # Convert sets to lists
    phone_list = list(unique_numbers)
    email_list = list(unique_emails)

    # Determine the max number of rows needed (whichever list is longer)
    max_length = max(len(phone_list), len(email_list))

    # Pad the shorter list with empty strings so both columns align
    phone_list += [''] * (max_length - len(phone_list))
    email_list += [''] * (max_length - len(email_list))

    # Write rows with phone numbers in one column and emails in the other
    for phone, email in zip(phone_list, email_list):
        writer.writerow([phone, email])

print(f"Extracted phone numbers and emails have been saved to {output_file}")
