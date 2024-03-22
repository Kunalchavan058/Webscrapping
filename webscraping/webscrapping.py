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
                        market_segment_dict[segment_key][url] = {}
    
                      
#####################################################################################################
                        
'''  Derived the links from the original links and called as Derived_url
'''
#######################################################################################################   

#list of keywords to filter out
filter_keywords = ["planungsinformationen", "catalog", "kontakt", "projectmanager"]

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
                            # Check if the derived_url contains any of the filter_keywords
                            if not any(keyword in derived_url for keyword in filter_keywords):
                                if derived_url not in market_segment_dict[segment_key][original_url]:
                                    #print(derived_url)
                                    market_segment_dict[segment_key][original_url][derived_url] = []
                else:
                    print(f"No 'content-main' class found in {original_url}")
            else:
                print(f"Failed to fetch {original_url}")
        except Exception as e:
            print(f"Error fetching {original_url}: {e}")

# Example output structure
# print("Market Segment Dictionary with Derived URLs:")
# for key, urls_dict in market_segment_dict.items():
#     print(f"{key}:")
#     for original_url, derived_urls in urls_dict.items():
#         print(f"  Original URL: {original_url}")
#         for url in derived_urls:
#             print(f"    - Derived URL: {url}")

 
#####################################################################################################
                        
'''  Used Derived links to get the Product links 
'''
#######################################################################################################   

for segment, urls_dict in market_segment_dict.items():
    for original_url, derived_urls_dict in urls_dict.items():
         for derived_url, derived_url_list in derived_urls_dict.items():
            try:
                response = requests.get(derived_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    content_main = soup.find(class_='tx-dkdcatalog')
                    if content_main:
                        links = content_main.find_all('a', href=True)
                        for link in links:
                            product_url = link['href']
                            # Skip undesired URLs before any processing
                            if 'javascript:void(0)' in product_url or product_url.endswith('.png') or 'shop' in product_url:
                                continue

                            if not product_url.startswith('http'):
                                product_url = base_url + product_url

                            # Check if the product URL is already processed or contains 'shop'
                            if product_url not in market_segment_dict[segment_key][original_url][derived_url] and 'shop' not in product_url:
                                print(product_url)
                                market_segment_dict[segment_key][original_url][derived_url].append(product_url)
                                print(f"derived_url: {derived_url} and derived_url_list: {derived_url_list}" )
                            
                            else:
                                print(f"Failed to fetch {derived_url}")

            except Exception as e:
              print(f"Error fetching {derived_url}: {e}")
            
                                    
            
                            





