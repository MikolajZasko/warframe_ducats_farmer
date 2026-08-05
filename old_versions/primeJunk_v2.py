from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import os
import threading 
import time

# settings
# 
# batches / theads / pages processed at a time 
# (use with caution, too big number can corrupt the results, wf.market refuses to view too many sites at the same time)
# number 2 seems to work fine, 3 is sometimes too much
simultaneousThreads = 2
debugging = True

# amount of total prime parts concidered
totalLinksLoaded = 15

# clear the files
open('deals2.txt', 'w').close()
open('deals3.txt', 'w').close()

# # open weekly tasks
# os.startfile(r"C:\Users\Szejker12\Desktop\giery screeny itp\warframe\messages\weekly.txt")

# class for threading
class ScrapeThread(threading.Thread): 
    def __init__(self, url): 
        threading.Thread.__init__(self) 
        self.url = url
        self.driver = None
        self.page_source = None
        self.data = None
  
    def run(self): 
        if debugging:
            print()
            print("new prime part")
            print()

        # Basic settings selenium/webdriver
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\babec\\Pobrane" })
        chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2 })
        chromeOptions.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
        chromeOptions.add_argument("--start-maximized")
        chromeOptions.add_argument('--window-size=3840,2160')
        chromeOptions.add_argument("--headless")

        driver = webdriver.Chrome(options=chromeOptions) 
        driver.get(self.url)  

        # Check if page is loaded
        try:
            main = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "info-block--mRK0g"))
            )
        except:
            if debugging:
                print("works?")

        # check item price

        infoBlock = driver.find_elements(By.XPATH, "//div[@class='info-block--mRK0g']")[0]

        ducatsDiv = infoBlock.find_element(By.TAG_NAME, "div")

        itemDucats = ducatsDiv.find_element(By.TAG_NAME, "span").text

        # if (int(ducats) == 45):

        # rows
        rows = driver.find_elements(By.XPATH, "//div[@class='row order-row--Alcph']") 

        # row number / dont go more than 5 rows
        # rowNumber = 0

        for j in rows:
            
            # if (rowNumber > 5):
            #     break
            
            priceDiv = j.find_element(By.XPATH, ".//div[@class='order-row__price--hn3HU']")

            priceDivSecond = priceDiv.find_element(By.XPATH, ".//div[@class='price--LQgqJ sell--UxmH0']")

            platPrice = priceDivSecond.find_element(By.TAG_NAME, "b").text

            ducatAvg = int(itemDucats)/int(platPrice)

            nick = j.find_element(By.XPATH, ".//span[@class='user__name--xF_ju']").text

            # now we dig into url to get the item name
            urlList = self.url.split("/")[4]

            nameList = urlList.split("_")

            item = ""

            for index, word in enumerate(nameList):
                item += word.capitalize()
                # check if this is the last item in array
                if (not(index == len(nameList) - 1)):
                    item += " "

            msg = "[ducatAvg: " + str(round(ducatAvg,2)) + "] /w " + nick + " Hi! I want to buy: " + '"' + item + '"' + " for " + platPrice + " platinum. (warframe.market)"

            if debugging:
                print(msg)

            if (ducatAvg >= 22.5):

                # Print the message to the console so it can be copied easily
                print(msg)
                
                # Open the file in write mode ("w")
                with open("deals2.txt", "a") as file:
                    # Write the variable to the file
                    file.write(msg + "\n")
            else:
                break
                # # Open the file in write mode ("w")
                # with open("deals3.txt", "a") as file:
                #     # Write the variable to the file
                #     file.write(msg + "\n")

            # rowNumber+=1
                        
  
        # else:
        #     print("price different from 45, no point", self.url)

        driver.quit()


# Basic settings selenium/webdriver
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\babec\\Pobrane" })
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2 })
chromeOptions.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
chromeOptions.add_argument("--start-maximized")
chromeOptions.add_argument('--window-size=3840,2160')
chromeOptions.add_argument("--headless")

driver = webdriver.Chrome(options=chromeOptions)

# Page for Selenium
driver.get("https://warframe.market/tools/ducats")

# Check if page is loaded
try:
    main = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
except:
    if debugging:
        print("works?")
    
# Click the popup
# popUp = driver.find_elements(By.XPATH, "//button[@class='ncmp__btn']")[0].click()

# Zoom out the page using JavaScript
driver.execute_script("document.body.style.zoom='25%'")

# find offers / item names
# offerList = driver.find_elements(By.CLASS_NAME, "link smartLink--bBcyL ducats__link--cyTat")


# click ducatonator until ducats/plat is highest

clickMore = True
clicks = 0

while (clickMore) :
    
    time.sleep(0.5)

    ducatPlatDiv = driver.find_element(By.XPATH, "//div[@class='ducanator__dpp-sort--N3DM0']")
    ducatPlatButton = ducatPlatDiv.find_element(By.TAG_NAME, "div")
    driver.execute_script("arguments[0].click();", ducatPlatButton)
    ducatPlatButtonClass = ducatPlatButton.get_dom_attribute("class")

    if debugging:
        print()
        print(ducatPlatButtonClass)
        print()

    if (ducatPlatButtonClass == "sort-button--hEVZx small--of0QL down--wbjzK" or clicks >= 3):
        clickMore = False

    clicks += 1
    

# find all names
offerList = driver.find_elements(By.XPATH, "//a[@class='link smartLink--bBcyL ducats__link--cyTat']")
# Find all ducat numbers (next to names)
ducatPricesDOMList = driver.find_elements(By.XPATH, "//div[@class='ducats--uE1yU']")

offerListLinks = [] 
# ducatPricesList= []

# Get the links
for index, item in enumerate(offerList):
    if (index >= totalLinksLoaded):
        break
    else:
        link = item.get_dom_attribute("href")
        offerListLinks.append(link)

# # Get the prices
# for index, item in enumerate(ducatPricesDOMList):
#     if (index >= totalLinksLoaded):
#         break
#     else:
#         ducatAmount = item.text
#         if ducatAmount != '45':
#             # delete the link
#             offerListLinks[index] == ''
#             ducatPricesList.append('')
#         else:
#             ducatPricesList.append(ducatAmount)

# # Here if price is different from 45, remove this link and its price
# offerListLinks = list(filter(lambda a: a != '', offerListLinks))
# ducatPricesList = list(filter(lambda a: a != '', ducatPricesList))

if debugging:
    print()
    print(offerListLinks)
    print()
    # print(ducatPricesList)
    # print()


# Make a list of links
links = []

for i in offerListLinks:
    links.append("https://warframe.market" + i)

driver.quit()

# run in batches max 2
smaller_lists = [links[i:i+simultaneousThreads] for i in range(0, len(links), simultaneousThreads)]

for sublist in smaller_lists:
    threads = []

    for url in sublist: 
        t = ScrapeThread(url) 
        t.start() 
        threads.append(t) 
    
    for t in threads: 
        t.join()

os.startfile('deals2.txt')
# os.startfile('deals3.txt')
