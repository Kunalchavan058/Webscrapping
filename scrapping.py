import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# Initialize an empty list to store full URLs and another for specific links
full_urls = []
specific_links = []  # For links containing "freiraum-galabau"
meta_data_list = []

base_url = 'https://www.aco.de'
response = requests.get(base_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    nav_main = soup.find('ul', class_='navbar-nav nav-main me-auto')
    if not nav_main:
        print("The page structure has changed and the required element was not found.")
        exit()
    dropdown_menu = nav_main.find('div', class_='dropdown-menu nav-main__lvl-2__container navbar--columns')
    if not dropdown_menu:
        print("The dropdown menu was not found in the page structure.")
        exit()
    links_containers = dropdown_menu.find_all('div', class_='nav-main__lvl-3__container')
    for container in links_containers[0:3]:
        links = container.find_all('a')
        for link in links:
            full_url = urljoin(base_url, link.get('href', ''))
            full_urls.append(full_url)
            if 'freiraum-galabau' in link.get('href', ''):
                specific_links.append(full_url)




def get_all_links_from_page(url, full_urls, specific_links, include_substring='infrastruktur-tiefbau', exclude_substring='planungsinformationen'):
    all_links = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                full_link = urljoin(url, link['href'])
                if (full_link not in all_links and
                    full_link not in full_urls and
                    full_link not in specific_links and
                    exclude_substring not in full_link and
                    include_substring in full_link):
                    all_links.append(full_link)
    except Exception as e:
        print(f"Error fetching or parsing {url}: {e}")
    return all_links

def find_specific_links(full_urls, keyword, exclude_keyword):
    found_links = []  
    for page_url in full_urls[:]:
        try:
            response = requests.get(page_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_link = urljoin(page_url, href)
                    if keyword in href in href and exclude_keyword not in href and full_link not in full_urls:
                        if full_link not in found_links:
                            found_links.append(full_link)
        except Exception as e:
            print(f"Error fetching or parsing {page_url}: {e}")

    print(f"Number of links found: {len(found_links)}")
    return found_links

keyword = 'infrastruktur-tiefbau'
exclude_keyword = 'planungsinformationen'
specific_links = find_specific_links(full_urls, keyword, exclude_keyword)


for link in specific_links:
    print(f"Fetching links from {link}:")
    all_links = get_all_links_from_page(link, full_urls, specific_links)
    for l in all_links:
        print(l)
        market_segment = l.split("/produkte/")[1].split("/")[0]
        product= l.split("/produkte/")[1].split("/")[1]
        page_data = {'page_url': l, 'absolute_link': link, 'market_segment': market_segment, 'product':product }
        meta_data_list.append(page_data)
        
print(meta_data_list)

