# imports
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

# gets links from the json file
links = []

with open(settings.item_links_path, "r", encoding="utf-8") as f:
    links = json.load(f)

# initiate the main driver
driver = webdriver.Chrome(options=settings.chromeOptions)
driver.get(links[0])

helper_functions.check_if_loaded(driver)

ducats = helper_functions.get_ducats_price(driver)

print("Final result:", ducats)

driver.quit()