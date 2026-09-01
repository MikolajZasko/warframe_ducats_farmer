"""primeJunk_get_links.py

Fetches trade links from warframe market
and saves them into a json file
"""

# imports
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import json
from pathlib import Path
import sys

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import settings
from config import helper_functions

# print the starting info
helper_functions.get_links_prep_console()

# initiate the main driver
driver = webdriver.Chrome(options=settings.chromeOptions)
driver.get(settings.warframe_market_url)

helper_functions.check_if_loaded(driver)

# Zoom out the page using JavaScript
driver.execute_script("document.body.style.zoom='25%'")


# click sorting button until ducats/plat ratio is highest
clickMore = True
clicks = 0

while (clickMore) :
    
    time.sleep(0.5)

    ducatPlatDiv = driver.find_element(By.XPATH, "//div[@class='ducanator__dpp-sort--N3DM0']")
    ducatPlatButton = ducatPlatDiv.find_element(By.TAG_NAME, "div")
    driver.execute_script("arguments[0].click();", ducatPlatButton)
    ducatPlatButtonClass = ducatPlatButton.get_dom_attribute("class")

    if settings.debugging:
        print()
        print(ducatPlatButtonClass)
        print()

    if (ducatPlatButtonClass == "sort-button--hEVZx small--of0QL down--wbjzK" or clicks >= 3):
        clickMore = False

    clicks += 1

# find all names
offerList = driver.find_elements(By.XPATH, "//a[@class='link smartLink--bBcyL ducats__link--cyTat']")

linksToItems = [] 

# Get the links
for index, item in enumerate(offerList):
    if (index >= settings.totalLinksLoaded):
        break
    else:
        link = item.get_dom_attribute("href")
        linksToItems.append(link)

if settings.debugging:
    print("links found: ", linksToItems)

# Make a list of links
links = []

for i in linksToItems:

    url = "https://warframe.market" + i

    # get just the "slug"
    slug = i.split("/")[2]

    links.append(
        {
            "url":url,
            "slug":slug
        })

# save the results to the file
with open(settings.item_links_path, "w", encoding="utf-8") as file:
    json.dump(links, file, indent=4)

driver.close()

helper_functions.get_links_quit_info()