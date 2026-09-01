"""settings.py

Defines the script behaviour - one place to modify functionality
"""

from pathlib import Path

#
# settings - alter the way the script works
#
 
# paths
current_path = Path.cwd()
data_path = current_path / "data"
scripts_path = current_path / "scripts"
deals_json_path = data_path / "deals.json"
deals_desperate_path = data_path / "deals_desperate.txt"
item_links_path = data_path / "itemLinks.json"
item_info_path = data_path / "itemInfo.json"
item_ids_path = data_path / "itemIds.json"

# batches / theads / pages processed at a time 
# (use with caution, too big number can corrupt the results, wf.market refuses to view too many sites at the same time)
# number 2 seems to work fine, 3 is sometimes too much
simultaneousThreads = 2
debugging = False
warframe_market_url = "https://warframe.market/tools/ducats"


# amount of total prime parts concidered
totalLinksLoaded = 20

# if true, every time a desperate deal is found we save it to the deals_desperate_path file 
save_desparate_deals = False


# api links
item_info_link = "https://api.warframe.market/v2/items"

# #
# # Basic settings selenium/webdriver
# #
# chromeOptions = webdriver.ChromeOptions()
# chromeOptions.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\babec\\Pobrane" })
# chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2 })
# chromeOptions.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
# chromeOptions.add_argument("--start-maximized")
# chromeOptions.add_argument('--window-size=3840,2160')
# chromeOptions.add_argument("--headless")