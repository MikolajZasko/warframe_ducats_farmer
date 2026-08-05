"""settings.py

Defines the script behaviour - one place to modify functionality
"""

from selenium import webdriver
from pathlib import Path

#
# settings - alter the way the script works
#
 
# batches / theads / pages processed at a time 
# (use with caution, too big number can corrupt the results, wf.market refuses to view too many sites at the same time)
# number 2 seems to work fine, 3 is sometimes too much
simultaneousThreads = 2
debugging = False
warframe_market_url = "https://warframe.market/tools/ducats"
save_desparate_deals = True

# amount of total prime parts concidered
totalLinksLoaded = 20

# paths
current_path = Path.cwd()
data_path = current_path / "data"
deals_path = data_path / "deals.txt"
deals_desperate_path = data_path / "deals_desperate.txt"
item_links_path = data_path / "itemLinks.json"

#
# Basic settings selenium/webdriver
#
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\babec\\Pobrane" })
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2 })
chromeOptions.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
chromeOptions.add_argument("--start-maximized")
chromeOptions.add_argument('--window-size=3840,2160')
chromeOptions.add_argument("--headless")