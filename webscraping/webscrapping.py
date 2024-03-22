import requests
from bs4 import BeautifulSoup

base_url = 'https://www.aco.de'
response = requests.get(base_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    dropdown_menus = soup.select('.dropdown-menu.nav-main__lvl-2__container.navbar--columns')
    market_segment_dict = {}
    for menu in dropdown_menus:
        for link in menu.find_all('a', href=True):
            # Construct the absolute URL
            url = link['href']
            if not url.startswith('http'):
                url = base_url + url
            
            # Process only URLs that contain 'produkte'
            if 'produkte' in url:
                # Split the URL to find the market segment key
                parts = url.split('/produkte/')[1].split('/')
                segment_key = parts[0]  # The first element after 'produkte'
                if segment_key:
                    if segment_key not in market_segment_dict:
                        market_segment_dict[segment_key] = {}
                
                    if url not in market_segment_dict[segment_key]:
                        market_segment_dict[segment_key][url] = []
    
    for segment_key, urls_dict in market_segment_dict.items():
        for original_url in urls_dict.keys():
            try:
                response = requests.get(original_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    content_main = soup.find(class_='content-main')
                    if content_main:
                        links = content_main.find_all('a', href=True)
                        for link in links:
                            derived_url = link['href']
                            if not derived_url.startswith('http'):
                                derived_url = base_url + derived_url
                            # Append each new scraped link to the list for its original URL
                            if derived_url not in market_segment_dict[segment_key][original_url]:
                                market_segment_dict[segment_key][original_url].append(derived_url)
                    else:
                        print(f"No 'content-main' class found in {original_url}")
                else:
                    print(f"Failed to fetch {original_url}")
            except Exception as e:
                print(f"Error fetching {original_url}: {e}")

# Print the updated market segment dictionary
print("Updated Market Segment Dictionary:")
for segment_key, urls_dict in market_segment_dict.items():
    print(f"{segment_key}:")
    for original_url, derived_urls in urls_dict.items():
        print(f"  Original URL: {original_url}")
        for derived_url in derived_urls:
            print(f"    - Derived URL: {derived_url}")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

