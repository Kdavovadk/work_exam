"""This module collects data about availabe products in Metro store"""

import json
import requests

from typing import Dict, List

# Constants
API_URL = 'https://api.metro-cc.ru/products-api/graph'
BASE_URL = 'https://online.metro-cc.ru'
MSK_STORE_ID = 11
SPB_STORE_ID = 15
# Query template
QUERY = '''\nquery Query($storeId: Int!, $from: Int!, $slug: String!, $size: Int!, $eshopAvailability: Boolean!) {
  category(storeId: $storeId, slug: $slug, eshopAvailability: $eshopAvailability) {
    products(from: $from, size: $size) {
      id
      name
      url
      stocks {
        prices_per_unit {
          old_price
          price
          is_promo
        }
      }
      manufacturer {
        name
      }
    }
  }
}'''


def get_region_products_list(storeId: int) -> List[Dict[str, int]]:
    """Gets products by category in specified store.

    Args:
        storeId (int): store identifier
    
    Returns:
        Specified store products list

    """

    request_data = {
        'query': QUERY,
        'variables': { # Query variables
            'storeId': storeId,
            'from': 0,
            'slug': 'chay', # Category
            'size': 1000,
            'eshopAvailability': True,
        }
    }


    # Init and send POST-request
    response = requests.post(API_URL, json=request_data)
    if response.status_code == 200:
        response_json = response.json()
    else:
        print(response.status_code)
        exit(1)

    # Convert response data into a convenient output format
    products_list = []
    for product in response_json['data']['category']['products']:
        product_price_info = product['stocks'][0]['prices_per_unit']
        products_list.append({
                'id': product['id'],
                'name': product['name'],
                'url': BASE_URL + product['url'],
                'regular_price': product_price_info['old_price'] if product_price_info['is_promo'] else product_price_info['price'],
                'promo_price': product_price_info['price'] if product_price_info['is_promo'] else product_price_info['old_price'],
                'brand': product['manufacturer']['name'],
            }
        )

    return products_list


# Output data assembly
result = {
    'fields_names': {
        'city': ['ID', 'Наименование', 'Ссылка', 'Регулярная цена', 'Промо цена', 'Бренд']
    },
    'products': {}
}
result['products']['spb'] = get_region_products_list(SPB_STORE_ID)
result['products']['msk'] = get_region_products_list(SPB_STORE_ID)

# Write result to json file
with open('products.json', 'w', encoding='utf-8') as result_json:
  json.dump(result, result_json, ensure_ascii=False, indent=3)
