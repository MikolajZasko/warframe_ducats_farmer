"""helper_functions.py

Helper functions used in:
- primeJunk_get_links.py
- primeJunk_v3.py
"""

# imports
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import re
from urllib.parse import urlparse
import subprocess

# types
from selenium.webdriver.remote.webelement import WebElement

# modules
from . import settings

#
# helper functions
#

def check_if_loaded(driver):
    """Checks if page is fully loaded

    Args:
        driver (WebDriver): a driver to be checked

    Returns:
        None
    """

    try:
        # Waits until the browser document state is completely loaded
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        if settings.debugging:
            print("Page loaded completely!")
    except TimeoutException:
        if settings.debugging:
            print("Debug: Timed out waiting for document.readyState.")

def get_ducats_price(driver):
    """gets the price in ducats of currently loaded item

    Args:
        driver (WebDriver): a driver where the url is loaded
    Returns:
        str: amount of ducats for the prime part
    """

    # get the right DOM element
    section = driver.find_element(By.XPATH, "//section[@class='information-container--ufjiP compensation--Mq1HF']")
    section_children = section.find_elements(By.XPATH, "./*")

    # find child containing "Ducats" and get only it's ints
    for child in section_children:
        if "Ducats" in child.text:

            # extract just the number
            pattern = re.compile(r"\d+")

            # Extracts all numbers as integers efficiently
            numbers = [int(n) for n in pattern.findall(child.text)]

            return numbers[0]

def get_item_name(url):
    """gets the item name from provided url

    last fragment ("/") of url path

    Args:
        url (str): url

    Returns:
        str: last part of url path
    """

    # parse the url using urlparse
    parsed = urlparse(url)
    path_segments = parsed.path.strip("/").split("/")

    # return the last element
    return path_segments[-1]

def parse_row(row : WebElement, item_name):

    # get the price (in plat)
    price_in_plat_div = row.find_element(By.XPATH, ".//div[contains(@class, 'order-row__price--hn3HU')]") 

    price_in_plat = price_in_plat_div.text

    # get the nickname
    nickname_div = row.find_element(By.XPATH, ".//div[contains(@class, 'order-row__user--TrsYv')]")

    nickname = nickname_div.text.split("wts")[1].strip()

    # change the item name so it does not look sus
    altered_item_name = item_name.replace("_", " ").title()

    # create the message
    message = f"/w {nickname} Hi! I want to buy: \"{altered_item_name}\" for {price_in_plat} platinum. (warframe.market)"

    return (int(price_in_plat),message)

def prep_console():

    # clearing the console using some voodoo stuff from gemini
    subprocess.run("cls", shell=True)

    print("Warframe Ducat farmer 💰")
    print()
    print("[ducats gained per plat - more = better]")
    print()