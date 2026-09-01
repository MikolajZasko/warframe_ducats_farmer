"""primeJunk_v3.py

Scrapes the links provided by primeJunk_get_links.py
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
        self.url = item["url"]
        self.slug = item["slug"]
        self.driver = None
        self.page_source = None
        self.data = None
  
    def run(self): 
        """starts the process of gathering information stored under self.url
        """

        if settings.debugging:
            print()
            print("new prime part")
            print()

        # get top orders
        response = requests.get( f"https://api.warframe.market/v2/orders/item/{self.slug}/top" )

        data = response.json()

        sell_orders = data["data"]["sell"]

        # get the ducat price and in-game name for the prime part
        ducats = items_info[self.slug]["ducats"]
        in_game_name =  items_info[self.slug]["name"]

        for sell_order in sell_orders:

            # check if ducats exist
            if ducats is not None:
                plat_price = sell_order["platinum"]

                ducat_avg = ducats / plat_price

                if ducat_avg >= 22.5:

                    # compose a message
                    seller_nickname = sell_order["user"]["ingameName"]

                    message = f"/w {seller_nickname} Hi! I want to buy: \"{in_game_name}\" for {plat_price} platinum. (warframe.market)"

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

# gets links from the json file
links = []

with open(settings.item_links_path, "r", encoding="utf-8") as f:
    links = json.load(f)

# divides all links into smaller batches (2 by default)
batches = [links[i:i+settings.simultaneousThreads] for i in range(0, len(links), settings.simultaneousThreads)]

# load the info from item_info_path
items_info = []

with open(settings.item_info_path, "r", encoding="utf-8") as f:
    items_info = json.load(f)

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