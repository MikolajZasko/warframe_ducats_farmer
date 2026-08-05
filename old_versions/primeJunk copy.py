from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import os
import threading 
import multiprocessing 

# Basic settings selenium/webdriver
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\babec\\Desktop\\test" })
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2 })
chromeOptions.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
chromeOptions.add_argument("--start-maximized")
chromeOptions.add_argument('--window-size=1920,1080')
chromeOptions.add_argument("--headless")

def scrape(url): 
    driver = webdriver.Chrome() 
    driver.get(url) 

    # Check if page is loaded
    try:
        main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content__body--qkyqR flex--root"))
        )
    except:
        print("works?")

    infoBlock = driver.find_elements(By.XPATH, "//div[@class='info-block--mRK0g']")[0]

    ducatsDiv = infoBlock.find_element(By.TAG_NAME, "div")

    ducats = ducatsDiv.find_element(By.TAG_NAME, "span").text

    if (int(ducats) == 45):

        # rows
        rows = driver.find_elements(By.XPATH, "//div[@class='row order-row--Alcph']") 

        # price div
        for j in rows:
            
            priceDiv = j.find_element(By.XPATH, ".//div[@class='order-row__price--hn3HU']")

            priceDivSecond = priceDiv.find_element(By.XPATH, ".//div[@class='platinum-price--DQ63t sell--UxmH0']")

            price = priceDivSecond.find_element(By.TAG_NAME, "b").text

            if (int(price) <= 3):

                nick = j.find_element(By.XPATH, ".//span[@class='user__name--xF_ju']").text

                itemArr = i.split("/")[2]

                itemArr = itemArr.split("_")

                item = ""

                for index, h in enumerate(itemArr):
                    item += h.capitalize()
                    # check if this is the last item in array
                    if (not(index == len(itemArr) - 1)):
                        item += " "

                msg = "/w " + nick + " Hi! I want to buy: " + '"' + item + '"' + " for " + price + " platinum. (warframe.market)"

                if (int(price) <= 2):
                    # Open the file in write mode ("w")
                    with open("deals2.txt", "a") as file:
                        # Write the variable to the file
                        file.write(msg + "\n")
                else:
                    # Open the file in write mode ("w")
                    with open("deals3.txt", "a") as file:
                        # Write the variable to the file
                        file.write(msg + "\n")
                

                print(msg) 
            else:
                break

    else:
        print("no point / ducats are not 45")

driver = webdriver.Chrome(options=chromeOptions)

# clear the files
open('deals2.txt', 'w').close()
open('deals3.txt', 'w').close()

# Page for Selenium
driver.get("https://warframe.market/tools/ducats")

# Check if page is loaded
try:
    main = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "content--UwhYJ grow--Q24fj"))
    )
except:
    print("works?")
    
# Click the popup
popUp = driver.find_elements(By.XPATH, "//button[@class='ncmp__btn']")[0].click()

# Zoom out the page using JavaScript
driver.execute_script("document.body.style.zoom='25%'")

# Find an elements by class name
# offerList = driver.find_elements(By.CLASS_NAME, "link smartLink--bBcyL ducats__link--cyTat")
offerList = driver.find_elements(By.XPATH, "//a[@class='link smartLink--bBcyL ducats__link--cyTat']")
                                                
offerListLinks = [] 

# Get the links
for index, i in enumerate(offerList):
    if (index >= 3):
        break
    else:
        link = i.get_dom_attribute("href")
        offerListLinks.append(link)

# Make a list of links
links = []

for i in offerListLinks:
    links.append("https://warframe.market" + i)
    
processes = [] 
for url in links: 
    p = multiprocessing.Process(target=scrape, args=(url,)) 
    if __name__ == '__main__':
        p.start() 
        processes.append(p) 
  
for p in processes: 
    p.join()

os.startfile('C:\\Users\\Szejker12\\Desktop\\wf-forducats\\deals2.txt')
os.startfile('C:\\Users\\Szejker12\\Desktop\\wf-forducats\\deals3.txt')
driver.quit()


