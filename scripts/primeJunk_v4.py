"""primeJunk_v3.py

Gets all items found from itemIds.json and finds the best deals
"""

# imports
from selenium.webdriver.common.by import By
import threading 
import json
import sys
import requests
from pathlib import Path

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import settings
from config import helper_functions

class ScrapeThread(threading.Thread): 
    """class for threading - 1 thread = 1 item

    Args:
        threading (Thread): Thread class
    """

    def __init__(self, item): 
        """initiates the class with url provided as str

        Args:
            url (str): the destination url
        """
        
        threading.Thread.__init__(self) 
        self.id = item["id"]
        self.slug = item["slug"]
        self.ducats = item["ducats"]
        self.name = item["name"]

        self.driver = None
        self.page_source = None
        self.data = None
  
    def run(self): 
        """starts the process of gathering information stored under self.id
        """

        if settings.debugging:
            print()
            print("new prime part")
            print()

        # check if it has defined ducat price
        if self.ducats is not None:

            # get ALL orders with a given id
            response = requests.get( f"https://api.warframe.market/v2/orders/itemId/{self.id}" )

            data = response.json()

            orders = data["data"]

            for order in orders:

                if order["type"] == "sell":

                    plat_price = order["platinum"]

                    ducat_avg = self.ducats / plat_price

                    if ducat_avg >= 22.5:

                        # compose a message
                        seller_nickname = order["user"]["ingameName"]

                        message = f"/w {seller_nickname} Hi! I want to buy: \"{self.name}\" for {plat_price} platinum. (warframe.market)"

                        # Print the message to the console so it can be copied easily,
                        # include plat avg so we can find the best deals
                        print(f"[ \033[1m{ducat_avg}\033[0m ]",message)

                        # OPTIONAL: 
                        # Open the file in write mode ("w")
                        if settings.save_deals_to_file:
                            with open(settings.deals_path, "a") as file:
                                # Write the variable to the file
                                file.write(message + "\n")
                    else:
                        # OPTIONAL: 
                        # Open the file in write mode ("w")
                        if settings.save_desparate_deals:
                            with open(settings.deals_desperate_path, "a") as file:
                                # Write the variable to the file
                                file.write(message + "\n")

# gets ids from the json file
ids = []

with open(settings.item_ids_path, "r", encoding="utf-8") as f:
    ids = json.load(f)

# load the info from item_info_path
items_info = {}

with open(settings.item_info_path, "r", encoding="utf-8") as f:
    items_info = json.load(f)

# converts item_info to a list then
# divides all item_info into smaller batches (2 by default)
items_list = list(items_info.values())
batches = [items_list[i:i+settings.simultaneousThreads] for i in range(0, len(items_list), settings.simultaneousThreads)]

# starts the process of scraping in batches
for sublist in batches:
    threads = []

    for item in sublist: 
        t = ScrapeThread(item) 
        t.start() 
        threads.append(t) 
    
    for t in threads: 
        t.join()

# wait for user to press "enter"
helper_functions.wait_for_enter_and_quit()