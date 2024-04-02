import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

base_url = 'https://www.aco.de'
response = requests.get(base_url)

#####################################################################################################
                        
'''  Links from the market segment are defined as original_url
     Market segment consist of three parts 
     Freiraum /GalaBau, Infrastruktur / Tiefbau and Gebäude
'''
####################################################################################################### 

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    dropdown_menus = soup.select('.nav-main__lvl-3__container')
    market_segment_dict = {}
    
    
    for index, menu in enumerate(dropdown_menus):
        if index >= 2:  
            break

        for link in menu.find_all('a', href=True):
            
            url = link['href']
            if not url.startswith('http'):
                url = base_url + url
            
            
            if 'produkte' in url:
                
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
                
                primary_class = soup.find(class_='tx-dkdcatalog') or soup.find(class_='content-main')
                
                if primary_class:
                    li_elements = primary_class.find_all('li')
                    for li in li_elements:
                        a_elements = li.find_all('a', href=True)
                        for a in a_elements:
                            derived_url = a['href']
                            if not derived_url.startswith('http'):
                                derived_url = base_url + derived_url  # Make the link absolute
                            if not any(keyword in derived_url for keyword in filter_keywords) and not original_url.startswith(derived_url):
                                if derived_url not in market_segment_dict[segment_key][original_url]:
                                    market_segment_dict[segment_key][original_url][derived_url] = []
                else:
                    print(f"No relevant class found in {original_url}")
            else:
                print(f"Failed to fetch {original_url}")
        except Exception as e:
            print(f"Error fetching {original_url}: {e}")

# 
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
    for original_url, derived_urls_dict in tqdm(urls_dict.items()):
        for derived_url, product_url_list in derived_urls_dict.items():
            try:
                response = requests.get(derived_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    content_main = soup.find(class_='tx-dkdcatalog') or soup.find(class_='content-main')
                    if content_main:
                        li_elements = content_main.find_all('li')
                        for li in li_elements:
                            a_elements = li.find_all('a', href=True)
                            for a in a_elements:
                                product_url = a['href']
                                # Normalize URL
                                if not product_url.startswith('http'):
                                    product_url = base_url + product_url
                                # Exclude product URLs that are base parts of original or derived URLs
                                if not any(keyword in product_url for keyword in filter_keywords) and \
                                   'javascript' not in product_url and \
                                   not product_url.endswith('.png') and \
                                   'shop' not in product_url and \
                                   not (original_url.startswith(product_url) or derived_url.startswith(product_url)):
                                        if product_url not in product_url_list:
                                            product_url_list.append(product_url)
            except Exception as e:
                print(f"Error fetching {derived_url}: {e}")



# for segment, urls_dict in market_segment_dict.items():
#     print(f"{segment}:")
#     for original_url, derived_urls_dict in urls_dict.items():
#         print(f"  Original URL: {original_url}")
#         for derived_url, product_url_list in derived_urls_dict.items():
#             print(f"    - Derived URL: {derived_url}")
#             for product_url in product_url_list:
#                 print(f"      - Product URL: {product_url}")


# 
##############################################################################################################
'''Inverted'''
##############################################################################################################
product_key_info = {}

for segment, urls_dict in market_segment_dict.items():
    for original_url, derived_urls_dict in urls_dict.items():
        for derived_url, product_urls in derived_urls_dict.items():
            for product_url in product_urls:
                # Split the URL by '/' to get segments
                parts = product_url.rsplit('/', 3)  
                if len(parts) >= 4:  
                    product_key = parts[-3] + '/' + parts[-2] + '/' + parts[-1]
                else:
                    continue  

                if product_key in product_key_info:
                    product_key_info[product_key]['count'] += 1
                    if segment not in product_key_info[product_key]['segments']:
                        product_key_info[product_key]['segments'].append(segment)
                        
                    if original_url not in product_key_info[product_key]['original_url']:
                        product_key_info[product_key]['original_url'].append(original_url)

                    if derived_url not in product_key_info[product_key]['derived_url']:
                        product_key_info[product_key]['derived_url'].append(derived_url)

                    if product_url not in product_key_info[product_key]['product_url']:
                        product_key_info[product_key]['product_url'].append(product_url)
                else:
                    product_key_info[product_key] = {'count': 1, 'segments': [segment],'original_url':[original_url], 'derived_url':[derived_url],'product_url':[product_url]}

counter = 0  # Initialize counter

for product_key, info in product_key_info.items():
    if counter >= 20:  
        break 
    print(f"Product Key: {product_key}")
    print(f"  Count: {info['count']}")
    
    print("  Segments:")
    for segment in info['segments']:
        print(f"    - {segment}")
    print("  Original URLs:")
    for original_url in info['original_url']:
        print(f"    - {original_url}")
    print("  Derived URLs:")
    for derived_url in info['derived_url']:
        print(f"    - {derived_url}")
        
    print("  Product URLs:")
    for product_url in info['product_url']:
        print(f"    - {product_url}")
    print("\n")  
    
    counter += 1  
