"""helper_functions.py

Helper functions used in:
- primeJunk_get_links.py
- primeJunk_v3.py
"""

# imports
import re
from urllib.parse import urlparse
import subprocess

# modules
from . import settings

#
# helper functions
#

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


def prep_console():
    """clears the console and prints info at the start of the program - the simplest UI the world has ever seen
    """

    # clearing the console using some voodoo stuff from gemini
    subprocess.run("cls", shell=True)

    print("Warframe Ducat farmer 💰")
    print()
    print("[ducats gained per plat - more = better]")
    print()

def get_links_quit_info():
    print("✅ Done! Making api requests ...")

def wait_for_enter_and_quit():
    """waits for user to press enter then quits the python script
    """
    while input("Press Enter to exit... ") != "":
        quit()