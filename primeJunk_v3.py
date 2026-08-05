# imports
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading 
import json
import os

# modules
from config import settings
from config import helper_functions

class ScrapeThread(threading.Thread): 
    """class for threading - 1 thread = 1 item

    Args:
        threading (Thread): Thread class
    """

    def __init__(self, url:str): 
        """initiates the class with url provided as str

        Args:
            url (str): the destination url
        """
        
        threading.Thread.__init__(self) 
        self.url = url
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

        # initiate a selenium driver and get the url
        driver = webdriver.Chrome(options=settings.chromeOptions) 
        driver.get(self.url)  

        # find ducats price for this item
        ducats_price = helper_functions.get_ducats_price(driver)

        # get the item name
        item_name = helper_functions.get_item_name(self.url)

        # get all rows
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'order-row--Alcph')]") 

        for row in rows:

            # get the price and message
            price_in_plat, message = helper_functions.parse_row(row, item_name)

            ducatAvg = int(ducats_price)/int(price_in_plat)

            if settings.debugging:
                print(message)

            if (ducatAvg >= 22.5):

                # Print the message to the console so it can be copied easily,
                # include plat avg so we can find the best deals
                print(f"[ \033[1m{ducatAvg}\033[0m ]",message)
                
                # Open the file in write mode ("w")
                with open(settings.deals_path, "a") as file:
                    # Write the variable to the file
                    file.write(message + "\n")
            else:
                # Optional - save the desparate plat price into a file
                if settings.save_desparate_deals:
                    with open(settings.deals_desperate_path, "a") as file:
                        # Write the variable to the file
                        file.write(message + "\n")

                break

        driver.quit()

# gets links from the json file
links = []

with open(settings.item_links_path, "r", encoding="utf-8") as f:
    links = json.load(f)

# divides all links into smaller batches (2 by default)
batches = [links[i:i+settings.simultaneousThreads] for i in range(0, len(links), settings.simultaneousThreads)]

# starts the process of scraping in batches
for sublist in batches:
    threads = []

    for url in sublist: 
        t = ScrapeThread(url) 
        t.start() 
        threads.append(t) 
    
    for t in threads: 
        t.join()

# wait for user to press "enter"
helper_functions.wait_for_enter_and_quit()