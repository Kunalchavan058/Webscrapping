import requests
from bs4 import BeautifulSoup

# URL of the webpage you want to scrape
base_url = 'https://www.aco.de/produkte/freiraum-galabau/linienentwaesserung-freiraum'

# Send a HTTP request to the URL
response = requests.get(base_url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find the container with the class 'content-main'
content_main = soup.find(class_='content-main')

# If the 'content-main' container exists, find all <li> elements within it
if content_main:
    li_elements = content_main.find_all('li')

    # Loop through each <li> element
    for li in li_elements:
        a_elements = li.find_all('a')
        for a in a_elements:
            href = a.get('href')
            if 'planungsinformationen' not in href:
                if not href.startswith('http'):
                    href = base_url + href  # Make the link absolute
                link_text = a.get_text()
                print(f"Text: {link_text}, Link: {href}")
else:
    print("The 'content-main' class was not found in the HTML.")