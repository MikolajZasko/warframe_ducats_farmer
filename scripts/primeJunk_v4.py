"""primeJunk_v4.py

Gets all items found from itemIds.json and finds the best deals
"""

# imports
import threading 
import json
import sys
import requests
from pathlib import Path
import time

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import settings
from config import helper_functions

# variables
deals = []

#
# thread logic - claude
#

class RateLimiter:
    """Thread-safe rate limiter: allows `rate` calls per `per` seconds."""
    def __init__(self, rate=3, per=1.0):
        self.rate = rate
        self.per = per
        self.lock = threading.Lock()
        self.timestamps = []

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            # drop timestamps older than the window
            self.timestamps = [t for t in self.timestamps if now - t < self.per]

            if len(self.timestamps) >= self.rate:
                # need to wait until the oldest call exits the window
                sleep_time = self.per - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                now = time.monotonic()
                self.timestamps = [t for t in self.timestamps if now - t < self.per]

            self.timestamps.append(now)

# threading class
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

            rate_limiter.acquire()  # blocks until it's safe to make the request

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


                        if settings.debugging:
                            # Print the message to the console so it can be copied easily,
                            # include plat avg so we can find the best deals
                            print(f"[ \033[1m{ducat_avg}\033[0m ]",message)

                        # insert the deal to the right spot in the deals list
                        current_index = 0
                        obj_to_insert = {
                            "ducat_avg": ducat_avg, 
                            "message": message
                        }

                        insetred = False

                        if len(deals) == 0:
                            deals.append(obj_to_insert)
                        else:
                            while current_index != len(deals):
                                if ducat_avg >= deals[current_index]["ducat_avg"]:
                                    deals.insert(current_index, obj_to_insert)
                                    insetred = True
                                    break
                                else:
                                    current_index += 1

                        if not insetred:
                            deals.append(obj_to_insert)

                    else:
                        # OPTIONAL: 
                        # Open the file in write mode ("w")
                        if settings.save_desparate_deals:
                            with open(settings.deals_desperate_path, "a") as file:
                                # Write the variable to the file
                                file.write(message + "\n")

            # save the list to the json file - after all offers from the item
            helper_functions.save_json_atomic(settings.deals_json_path,deals)

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

# create ONE shared instance, used by all threads
rate_limiter = RateLimiter(rate=3, per=1.0)

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