# imports
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading 
import json
import sys
from selenium import webdriver
from pathlib import Path

# gemini's way to get modules "up" in a directory
# 1. Get the path of the current file, go UP one directory to the root ('project/')
parent_dir = Path(__file__).resolve().parent.parent

# 2. Add that parent directory to Python's path list
sys.path.append(str(parent_dir))


# modules
from config import settings
from config import helper_functions

class TestThread(threading.Thread): 
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

        helper_functions.check_if_loaded(driver)

        # find ducats price for this item
        ducats_price = helper_functions.get_ducats_price(driver)

        # get the item name
        item_name = helper_functions.get_item_name(self.url)

        # get all rows
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'order-row--Alcph')]") 

        for row in rows:

            # get the price and message
            price_in_plat, message = helper_functions.parse_row(row, item_name)
            
            print(price_in_plat, message)

            driver.quit()
            quit()

# gets links from the json file
links = []

with open(settings.item_links_path, "r", encoding="utf-8") as f:
    links = json.load(f)

tester = TestThread(links[0])
tester.run()
