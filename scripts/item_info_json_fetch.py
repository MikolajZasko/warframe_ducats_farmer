"""item_info_json_fetch.py

Makes a request to https://api.warframe.market/v2/items
and creates itemInfo.json
and itemIds.json
"""

# imports
import requests
from pathlib import Path
import sys
import json

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import settings

#
# script
#

response = requests.get(settings.item_info_link)

data = response.json()

# go deeper in the api structure
data = data["data"]

# prep a dict and a list for the info we need
items = {}
ids = []

for item in data:

    # get just the interesting data
    slug = item.get("slug")

    items[slug] = {
        "id": item.get("id"),
        "ducats": item.get("ducats"), 
        "tradingTax": item.get("tradingTax"),
        "name": item.get("i18n").get("en").get("name")
    }

    ids.append(item.get("id"))

# dump the info to the json file
with open(settings.item_info_path, "w", encoding="utf-8") as file:
    json.dump(items, file, indent=4)

with open(settings.item_ids_path, "w", encoding="utf-8") as file:
    json.dump(ids, file, indent=4)
