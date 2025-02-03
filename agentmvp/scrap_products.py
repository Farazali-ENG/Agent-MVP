import json
from scrapegraphai.graphs import SmartScraperMultiGraph


def process_scraped_data(products_data):
    products_list = []
    
    if isinstance(products_data, list):
        # Handle case where it's a list of dictionaries with 'products' key
        if all('products' in item for item in products_data):
            for item in products_data:
                products_list.extend(item['products'])
        else:
            products_list = products_data
    elif isinstance(products_data, dict):
        # Handle case where it's a single dictionary with 'products' key
        if 'products' in products_data:
            products_list = products_data['products']
        else:
            products_list = [products_data]
    else:
        raise ValueError("Unexpected data format from scraper")
    
    processed_products = []
    for product in products_list:
        processed_product = {}
        # Handle case where product name is in 'product' key
        if 'product' in product:
            processed_product['name'] = product['product']
        else:
            processed_product['name'] = product.get('name', '')
            
        processed_product['price'] = None if product.get('price') == 'NA' else product.get('price')
        processed_product['discount_percentage'] = None if product.get('discount_per') == 'NA' else product.get('discount_per')
        processed_products.append(processed_product)
    
    return processed_products


def product_scrapper(api_key, source_links):
    
    # Define the configuration for the scraping pipeline
    graph_config = {
        "llm": {
            "api_key": api_key,
            "model": "openai/gpt-4o-mini",
        },
        "verbose": True,
        "headless": True,
    }
    
    # Create the SmartScraperGraph instance
    smart_scraper_multi_graph = SmartScraperMultiGraph(
        prompt="Extract me all the products, prices (Keep as 'NA' if price is not available) and discount_per (discount rate for each product, keep as NA if no discount) from these website.",
        source=source_links,
        config=graph_config
    )
    
    # Run the pipeline
    result = smart_scraper_multi_graph.run()
    
    # Process the scraped data
    processed_result = process_scraped_data(result)
    
    result_json = json.dumps(processed_result, indent=4)

    return result_json
