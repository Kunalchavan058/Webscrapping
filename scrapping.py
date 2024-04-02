from bs4 import BeautifulSoup
import requests

base_url = 'https://www.aco.de'

#%%

def extract_market_segments_and_product_family(base_url):

    """
    Extracts market segments and their URLs from a webpage's for produkte part of the website. 
    It constructs a dictionary mapping each  product segment to its produckt family URLs
    
    Parameters:
    - base_url: The website base URL for  extracting the product family URLs.
    
    Returns:
    - A dictionary with market segments as keys and Product family URLs as values(which are keys for Product group). Returns an empty dictionary if the response is not 200.
    """
    response = response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        dropdown_menus = soup.select('.nav-main__lvl-3__container')
        market_segment_dict = {}
        
        for index, menu in enumerate(dropdown_menus):
            if index >= 1:  
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

        return market_segment_dict
    else:
        return {}
    

#%%

def market_segment_dict_with_product_group(market_segment_dict, base_url, filter_keywords, max_original_urls=1):
    """
    Expands a market segment dictionary by adding product group URLs under each product family URL, using specified filtering criteria.

    Parameters:
    - market_segment_dict: Dictionary with market segments and corresponding product family URLs.
    - base_url: Base URL for resolving relative links.
    - filter_keywords: Keywords to filter out certain URLs.

    Returns:
    - An updated dictionary, where each market segment key maps to a nested dictionary of product group URLs.
    """
    market_segment_dict_with_product_group = market_segment_dict.copy()

    for segment_key, urls_dict in market_segment_dict_with_product_group.items():
        urls_to_process = list(urls_dict.keys())[:max_original_urls] if max_original_urls is not None else list(urls_dict.keys())
        for original_url in urls_to_process:
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
                                if 'house-garden' in derived_url and not any(keyword in derived_url for keyword in filter_keywords) and not original_url.startswith(derived_url):
                                    market_segment_dict_with_product_group[segment_key][original_url].setdefault(derived_url, [])
                    else:
                        print(f"No relevant class found in {original_url}")
                else:
                    print(f"Failed to fetch {original_url}")
            except Exception as e:
                print(f"Error fetching {original_url}: {e}")

    return market_segment_dict_with_product_group
#%%

def market_segment_dict_with_product_urls(market_segment_dict_with_product_group, base_url, filter_keywords):
    """
    Further expands the market_segment_dict with URLs of products, filtering based on specified keywords, and returns the updated dictionary.
    
    Parameters:
    - market_segment_dict: The dictionary of market segments with nested dictionaries of product group URLs.
    - base_url: The base URL to get final product url by concatinating to the found url
    - filter_keywords: A list of keywords to exclude certain URLs.
    
    Returns:
    - An updated dictionary with market segments as keys and nested dictionaries of product family URLs, which themselves contain lists of product URLs as values.
    """
    for segment, urls_dict in market_segment_dict_with_product_group.items():
        for original_url, derived_urls_dict in urls_dict.items():
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
                                    # Apply filters
                                    if not any(keyword in product_url for keyword in filter_keywords) and \
                                       'javascript' not in product_url and \
                                       not product_url.endswith('.png') and \
                                       'shop' not in product_url and \
                                       not (original_url.startswith(product_url) or derived_url.startswith(product_url)):
                                            if product_url not in product_url_list:
                                                product_url_list.append(product_url)
                except Exception as e:
                    print(f"Error fetching {derived_url}: {e}")
    return market_segment_dict_with_product_group

#%%

def generate_product_key_info(market_segment_dict_with_product_urls):
    """
    Generate the Metadata, for each product url get the information about market segments it belongs to 
    
    Parameters:
    - market_segment_dict_with_product_urls: The fully expanded dictionary of market segments with product URLs.
    
    Returns:
    - A dictionary with product keys as keys and information about segments,
      original URLs, derived URLs, product URLs, and now also includes product name as values.
    """
    product_key_info = {}

    for segment, urls_dict in market_segment_dict_with_product_urls.items():
        for original_url, derived_urls_dict in urls_dict.items():
            for derived_url, product_urls in derived_urls_dict.items():
                for product_url in product_urls:
                    parts = product_url.rsplit('/', 3)
                    if len(parts) >= 4:
                        product_key = parts[-3] + '/' + parts[-2] + '/' + parts[-1]
                    else:
                        continue
                    product_name = product_url.split('/')[-1]
                    product_family = product_url.split('/')[-5]
                    product_group = product_url.split('/')[-4]

                    if product_key in product_key_info:
                        if segment not in product_key_info[product_key]['segments']:
                            product_key_info[product_key]['segments'].append(segment)
                            
                        if original_url not in product_key_info[product_key]['original_url']:
                            product_key_info[product_key]['original_url'].append(original_url)

                        if derived_url not in product_key_info[product_key]['derived_url']:
                            product_key_info[product_key]['derived_url'].append(derived_url)

                        if product_url not in product_key_info[product_key]['product_url']:
                            product_key_info[product_key]['product_url'].append(product_url)
                        
                        # Ensure 'product_name' is not overwritten if it already exists
                        if 'product_name' not in product_key_info[product_key]:
                            product_key_info[product_key]['product_name'] = product_name
                    else:
                        product_key_info[product_key] = {
                            'segments': [segment],
                            'original_url': [original_url], 
                            'derived_url': [derived_url],
                            'product_url': [product_url],
                            'product_name': product_name,
                            'product_group': product_group,
                            'product_family': product_family 
                        }
    
    return product_key_info
#%%

filter_keywords = ["planungsinformationen", "catalog", "kontakt", "projectmanager", "informationen"]

market_segment_dict = extract_market_segments_and_product_family(base_url)


market_segment_dict_with_product_group_ = market_segment_dict_with_product_group(market_segment_dict, base_url, filter_keywords)

market_segment_dict_with_product_urls_ = market_segment_dict_with_product_urls(market_segment_dict_with_product_group_, base_url, filter_keywords)

for segment, urls_dict in market_segment_dict_with_product_urls_.items():
    print(f"{segment}:")
    for original_url, derived_urls_dict in urls_dict.items():
        for derived_url, product_url_list in derived_urls_dict.items():
           for product_url in product_url_list:
              print(f"      - Product URL: {product_url}")


product_key_info = generate_product_key_info(market_segment_dict_with_product_urls_) 
print(product_key_info)

# counter = 0  # Initialize counter
# for product_key, info in product_key_info.items():
#     if counter >= 20:
#         break
#     print(f"Product Key: {product_key}")
#     print("  Segments:")
#     for segment in info['segments']:
#         print(f"    - {segment}")
#     print("  Original URLs:")
#     for original_url in info['original_url']:
#         print(f"    - {original_url}")
#     print("  Derived URLs:")
#     for derived_url in info['derived_url']:
#         print(f"    - {derived_url}")
#     print("  Product URLs:")
#     for product_url in info['product_url']:
#         print(f"    - {product_url}")
#     # Print the product name
#     print("  Product Name:")
#     print(f"    - {info['product_name']}")
#     # Now also print the product family and product group
#     print("  Product Family:")
#     print(f"    - {info['product_family']}")
#     print("  Product Group:")
#     print(f"    - {info['product_group']}")
#     print("\n")
    
#     counter += 1

