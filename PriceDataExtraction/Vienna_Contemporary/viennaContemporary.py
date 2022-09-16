from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
import csv
import os


# Global variables
TIMEOUT = 5
LOGIN_PAGE = "https://mp.viennacontemporary.at/login"


# Initializes chromedriver and creates a global driver variable.
def driverInit():
    global driver
    settings = webdriver.ChromeOptions()
    # This option starts the webdriver maximized to the display.
    settings.add_argument("--start-maximized")
    settings.add_experimental_option("detach", True)
    driver = webdriver.Chrome(r"C:\Users\makan\Downloads\chromedriver.exe", options=settings)

    return driver


# Opens a specified URL with the webdriver.
def getPage(url:str):
    # strip() is used to make sure no special characters are left in the string. (such as \n)
    url = url.strip()
    driver.get(url)


# Logs into the specified account. Change variables in userData.py
def login():
    from userData import username, password
    address_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/form/div[1]/div[1]/input"
    password_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/form/div[1]/div[2]/input"
    enter_button_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/form/div[2]/div/button"
    try:
        WebDriverWait(driver, timeout=TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, address_xpath)))
        driver.find_element_by_xpath(address_xpath).send_keys(username)
        driver.find_element_by_xpath(password_xpath).send_keys(password)
        driver.find_element_by_xpath(enter_button_xpath).click()
    except exceptions.TimeoutException:
        pass
    except exceptions.NoSuchElementException:
        pass
    except exceptions.ElementClickInterceptedException:
        pass
    

# Clicks on the accept cookies button in order to avoid ClickIntercepted exceptions.
def acceptCookies():
    cookie_button_xpath = "/html/body/div[1]/div/div[1]/button"
    driver.find_element_by_xpath(cookie_button_xpath).click()


# Clicks repetedly on the "Load More" button, until it no longer exists. -> Thus the page is fully loaded with all the artworks.
def expandPage():
    button_xpath = "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div/div/button"
    status = True
    while status == True:
        attempts = 0
        while attempts < 10:
            try:
                driver.switch_to.window(driver.window_handles[0])
                WebDriverWait(driver, timeout=TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
                e = driver.find_element_by_xpath(button_xpath)
                e.click()
                disabled = e.get_property("disabled")
                if disabled == True:
                    status = False
                    break
                else:
                    pass
            except exceptions.TimeoutException:
                attempts += 1
                try:
                    e = driver.find_element_by_xpath(button_xpath)
                    disabled = e.get_property("disabled")
                    if disabled == True:
                        status = False
                        break
                    else:
                        continue
                except:
                    status = False
                    break
            except exceptions.NoSuchElementException:
                status = False
                break
            except exceptions.StaleElementReferenceException:
                attempts += 1
                continue
            except exceptions.ElementNotInteractableException():
                status = False
                break


# Checks for the number of total artworks on the page.
# Currently not working (?)
def numberOfArtworks():
    number_xpath = "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/p/span"
    try:
        sleep(2)
        number = driver.find_element_by_xpath(number_xpath).text
        number = number.split(" ")[0]
    except:
        number = 800

    number = int(number)
    
    return number


# Gets the links for all the artworks on the page.
def getArtworks(indx:int):
    artwork_xpath = f"/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div/div[{indx+1}]/div[1]/div/div/img"
    art = driver.find_element_by_xpath(artwork_xpath)
    link = art.get_attribute("href")
    print(link)

    return link


# Exports the links variable into the data/links.txt file.
def exportLinks(links:list):
    with open("data/links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")


# Imports the URLs into the links variable from the data/links.txt file.
def importLinks():
    links = []
    with open("data/links.txt", "r") as f:
        for line in f:
            links.append(line.strip())

    return links


def setupCSV():
    now = datetime.now()
    filename = (r"C:\Users\makan\OneDrive\Desktop\SBS\Artworks\Vienna_Contemporary\Vienna_Contemporary\data\\" + now.strftime("%d-%m-data.csv"))

    with open(filename, "w", encoding="UTF-8", newline="") as f:
        w = csv.writer(f, delimiter=";", quotechar = "|")
        w.writerow(["artist", "title", "year", "gallery", "price", "currency", "materials", "dimensions", "url", "image_url" , "sold"])

# Opens the individual artwork pages and scrapes price data.
def scrapeData(link:str):
    link = link.strip()
    getPage(link)
    try:
        WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div/a")))
        try:
            artist = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div/a/h1").text
        except:
            artist = ""
        try:
            title_bar = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/p[2]/span").text
            try:
                title = title_bar.split(", ")[0]
                year = title_bar.split(", ")[1]
            except:
                title = title_bar
                year = ""
        except:
            title = ""
            year = ""
        try:
            gallery = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[5]/p[2]/a").text
        except:
            gallery = ""
        try:
            price = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/p[1]").text
        except:
            price = ""
        # Define by symbol at the start of the string!
        try:
            currency_prelim = price[0]
            if currency_prelim == "$":
                currency = "USD"
                price = price.replace("$", "")
            if currency_prelim == "€":
                currency = "EUR"
                price = price.replace("€", "")
        except:
            currency = ""
        try:
            materials = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/p[2]").text
        except:
            materials = ""
        try:
            status = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/p[2]/span").text
        except:
            status = ""
        try:
            dimensions = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/p[2]").text
        except:
            dimensions = ""

        try:
            url = link
        except:
            url = ""

        try:
            image_url = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div/div[1]/img")["srcset"]
        except:
            image_url = ""
    
    except exceptions.TimeoutException:
        try:
            artist = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div/a/h1").text
        except:
            artist = ""
        try:
            title_bar = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/p[2]/span").text
            try:
                title = title_bar.split(", ")[0]
                year = title_bar.split(", ")[1]
            except:
                title = title_bar
                year = ""
        except:
            title = ""
            year = ""
        try:
            gallery = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[5]/p[2]/a").text
        except:
            gallery = ""
        try:
            price = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/p[1]").text
        except:
            price = ""
        # Define by symbol at the start of the string!
        try:
            currency_prelim = price[0]
            if currency_prelim == "$":
                currency = "USD"
                price = price.replace("$", "")
            if currency_prelim == "€":
                currency = "EUR"
                price = price.replace("€", "")
        except:
            currency = ""
        try:
            materials = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/p[2]").text
        except:
            materials = ""
        try:
            status = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/p[2]/span").text
        except:
            status = ""
        try:
            dimensions = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/p[2]").text
        except:
            dimensions = ""

        try:
            url = link
        except:
            url = ""

        try:
            img = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div/div[1]/img")
            image_url = img.get_attribute("src")
        except:
            image_url = ""

    ret = [artist, title, year, gallery, price, currency, materials, dimensions, url, image_url, status]
    return ret


# Exports the price data into a csv file.
def exportData(l:list):
    now = datetime.now()
    filename = (r"C:\Users\makan\OneDrive\Desktop\SBS\Artworks\Vienna_Contemporary\Vienna_Contemporary\data\\" + now.strftime("%d-%m-data.csv"))
    with open(filename, "a", encoding="UTF-8", newline="") as f:
        w = csv.writer(f, delimiter=";", quotechar = "|")
        for item in l:
            w.writerow(item)


if __name__ == "__main__":
    driver = driverInit()
    # Goes to the login page and enters details.
    getPage(LOGIN_PAGE)
    login()
    links = []
    sleep(5)

    # IMPORTANT !
    # Set the BOOL value according to needs. If there are already URLs recorded => False


    ###################################################################################################################
    getLinks = True
    ###################################################################################################################


    # This process is in case we do not have a complete list of URLs already recorded in data/links.txt
    if getLinks == True:
        total_artworks = numberOfArtworks()
        print(total_artworks)
        acceptCookies()
        expandPage()
        for inx in range(total_artworks):
            links.append(getArtworks(inx))
        exportLinks(links)

    # This process is in case we already have a complete list of URLs recorded 
    elif getLinks == False:
        links = importLinks()


    data = []
    for link in links:
        export = scrapeData(link)
        data.append(export)
        print(export)

    setupCSV()
    exportData(data)

