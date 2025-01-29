import requests
from bs4 import BeautifulSoup
import re
import csv


def get_website(url):
    # Ensure the URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url  # Default to HTTPS

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def find_page(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    links = []
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

        # Look for keywords in href
        if any(keyword in href.lower() for keyword in keywords):
            if href.startswith('http'):  # Absolute URL
                full_url = href
            elif href.startswith('/'):  # Relative URL
                full_url = base_url.rstrip('/') + href
            else:
                continue  # Skip malformed or unrelated links

            if full_url not in links:  # Avoid duplicates
                links.append(full_url)

    return links


def extract_numbers(html):
    soup = BeautifulSoup(html, 'lxml')

    # Regex for phone numbers
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s*(?:Ext\.?|x)\s*\d{1,5})?'

    # Extract text and phone numbers
    text_content = soup.get_text(separator=" ", strip=True)
    phone_numbers = set(re.findall(phone_pattern, text_content))

    # Extract names from headers
    names = [tag.text.strip() for tag in soup.find_all(['h1', 'h2', 'h3']) if tag.text.strip()]

    return {'phone_numbers': list(phone_numbers)}


def scrape_website(base_url):
    html = get_website(base_url)
    if not html:
        print("Failed to fetch the base URL.")
        return []

    links = find_page(html, base_url)
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


url = ['https://veritasmanagement.com/', 'http://www.ruddrealty.com/', 'http://crtl.com/contact.aspx']




unique_numbers = set()

for i in url:
    results = scrape_website(i)

    for j in results:
        unique_numbers.update(j['phone_numbers'])

#print(list(unique_numbers))

unique_numbers = sorted(unique_numbers)

output_file = "unique_phone_numbers.csv"

with open(output_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Phone Numbers'])

    for number in unique_numbers:
        writer.writerow([number])

print(f"Unique phone numbers have been saved to {output_file}")
