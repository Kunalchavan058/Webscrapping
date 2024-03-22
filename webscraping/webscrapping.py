import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = 'https://www.aco.de'
response = requests.get(base_url)

#####################################################################################################
                        
'''  Links from the market segment are defined as original_url
     Market segment consist of three parts 
     Freiraum /GalBau, Infrastruktur / Tiefbau and Gebäude
'''
####################################################################################################### 

# Assuming 'response' is your HTTP response object and it has a status code of 200
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    dropdown_menus = soup.select('.nav-main__lvl-3__container')
    market_segment_dict = {}
    
    # Process only the first three elements
    for index, menu in enumerate(dropdown_menus):
        if index >= 3:  # Break the loop after processing the first three elements
            break

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
                        market_segment_dict[segment_key][url] = {}
    
                      
#####################################################################################################
                        
'''  Derived the links from the original links and called as Derived_url
'''
#######################################################################################################   

#list of keywords to filter out
filter_keywords = ["planungsinformationen", "catalog", "kontakt", "projectmanager", "informationen"]

for segment_key, urls_dict in market_segment_dict.items():
    for original_url in urls_dict.keys():
        try:
            response = requests.get(original_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Try finding 'tx-dkdcatalog' first, then 'content-main'
                primary_class = soup.find(class_='tx-dkdcatalog') or soup.find(class_='content-main')
                
                if primary_class:
                    li_elements = primary_class.find_all('li')
                    for li in li_elements:
                        a_elements = li.find_all('a', href=True)
                        for a in a_elements:
                            derived_url = a['href']
                            if not derived_url.startswith('http'):
                                derived_url = base_url + derived_url  # Make the link absolute
                            if not any(keyword in derived_url for keyword in filter_keywords):
                                if derived_url not in market_segment_dict[segment_key][original_url]:
                                    market_segment_dict[segment_key][original_url][derived_url] = []
                else:
                    print(f"No relevant class found in {original_url}")
            else:
                print(f"Failed to fetch {original_url}")
        except Exception as e:
            print(f"Error fetching {original_url}: {e}")

# Example of how you might print the results
print("Market Segment Dictionary with Derived URLs:")
for key, urls_dict in market_segment_dict.items():
    print(f"{key}:")
    for original_url, derived_urls in urls_dict.items():
        print(f"  Original URL: {original_url}")
        for url in derived_urls:
            print(f"    - Derived URL: {url}")

 
#####################################################################################################
                        
'''  Used Derived links to get the Product links 
'''
#######################################################################################################   


for segment, urls_dict in market_segment_dict.items():
    for original_url, derived_urls_dict in urls_dict.items():
        for derived_url, product_url_list in derived_urls_dict.items():
            try:
                response = requests.get(derived_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Adjusted to process <li> elements within 'tx-dkdcatalog' or 'content-main'
                    content_main = soup.find(class_='tx-dkdcatalog') or soup.find(class_='content-main')
                    if content_main:
                        li_elements = content_main.find_all('li')
                        for li in li_elements:
                            a_elements = li.find_all('a', href=True)
                            for a in a_elements:
                                product_url = a['href']
                                # Filter and skip undesired URLs
                                if not any(keyword in product_url for keyword in filter_keywords) and \
                                   'javascript' not in product_url and \
                                   not product_url.endswith('.png') and \
                                   'shop' not in product_url:
                                    if not product_url.startswith('http'):
                                        product_url = base_url + product_url
                                    if product_url not in product_url_list and 'shop' not in product_url:
                                        product_url_list.append(product_url)
                                       
            except Exception as e:
                print(f"Error fetching {derived_url}: {e}")



print("Market Segment Dictionary with Updated URLs:")
for segment, urls_dict in market_segment_dict.items():
    print(f"{segment}:")
    for original_url, derived_urls_dict in urls_dict.items():
        print(f"  Original URL: {original_url}")
        for derived_url, product_url_list in derived_urls_dict.items():
            print(f"    - Derived URL: {derived_url}")
            for product_url in product_url_list:
                print(f"      - Product URL: {product_url}")





