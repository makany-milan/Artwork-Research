from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
import csv
import os
import requests

Links = []
MAIN_PAGE = "https://www.artbasel.com/ovr/show?activeTab=artworks&orderBy=random(4705),id"
TIMEOUT = 10


def driverSetup():
    global driver

    settings = webdriver.ChromeOptions()
    # This option starts the webdriver maximized to the display.
    settings.add_argument("--start-maximized")
    settings.add_experimental_option("detach", True)

    driver = webdriver.Chrome(r"C:\Users\makan\Downloads\chromedriver.exe", options=settings)


def scrollToBottom():
    sleep(3)
    # get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    bottom = False
    while not bottom:
        # scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # wait for page to load
        sleep(3)
        # calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            bottom = True
        last_height = new_height

    # scroll back to the top
    driver.execute_script("window.scrollTo(0, 0)")
    sleep(3)


def scrollThrough():
    for x in range(200):
        try:
            driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_DOWN)
            Links.append(getLinks())
        except:
            sleep(2)
            pass


def getLinks():
    links = []
    indx = 0
    errors = 0
    while(True):
        indx += 1
        try:
            obj = driver.find_element_by_xpath(f"/html/body/div/div/div[4]/div/div/section[3]/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[{indx}]/div/header/a")
            links.append(obj.get_attribute("href"))
            errors = 0
        except exceptions.NoSuchElementException:
            errors += 1
            if errors >= 100:
                break

    return links


# Opens the individual artwork pages and scrapes price data.
def scrapeData(link:str):
    link = link.strip()
    driver.get(link)
    try:
        WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[2]/div/section/div/div/div[2]/div/h2/a/span")))
        try:
            artist = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/h2/a/span").text
        except:
            artist = ""
        try:
            title_bar = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[2]/h3").text
            try:
                title_pre = title_bar.split(", ")[:-1]
                year_pre = title_bar.split(", ")[-1]
                if year_pre.isnumeric():
                    title = title_pre[0]
                    year = year_pre
                elif year_pre.split(" - ")[0].insumeric:
                    title = title_pre[0]
                    year = year_pre
                else:
                    title = title_bar
                    year = ""
            except:
                title = title_bar
                year = ""
        except:
            title = ""
            year = ""
        try:
            gallery = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[1]/h3/a/span").text
        except:
            gallery = ""
        try:
            price = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[3]").text
        except:
            price = ""
        try:
            currency_prelim = price.split(" ")
            if len(currency_prelim) == 2:
                currency_prelim = currency_prelim[0]
            elif len(currency_prelim) == 3:
                currency_prelim = currency_prelim[1]
            elif len(currency_prelim) > 3:
                currency_prelim = currency_prelim[0]

            if currency_prelim == "USD":
                currency = "USD"
                price = price.replace("USD ", "")
            elif currency_prelim == "EUR":
                currency = "EUR"
                price = price.replace("EUR ", "")
            else:
                currency = ""
        except:
            currency = ""

        try:
            category = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[1]").text
        except:
            category = "" 

        try:
            materials = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[2]").text
        except:
            materials = ""

        try:
            dimensions = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[4]").text
        except:
            dimensions = ""

        try:
            url = link
        except:
            url = ""

        try:
            image_url = driver.find_element_by_tag_name("background-image").text
        except:
            image_url = ""
    
    except exceptions.TimeoutException:
        try:
            artist = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/h2/a/span").text
        except:
            artist = ""
        try:
            title_bar = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[2]/h3").text
            try:
                title_pre = title_bar.split(", ")[:-1]
                year_pre = title_bar.split(", ")[-1]
                if year_pre.isnumeric():
                    title = title_pre[0]
                    year = year_pre
                elif year_pre.split("-")[0].insumeric:
                    title = title_pre[0]
                    year = year_pre
                else:
                    title = title_bar
                    year = ""
            except:
                title = title_bar
                year = ""
        except:
            title = ""
            year = ""
        try:
            gallery = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[1]/h3/a/span").text
        except:
            gallery = ""
        try:
            price = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/div[3]").text
        except:
            price = ""
        # Define by symbol at the start of the string!
        try:
            currency_prelim = price.split(" ")
            if len(currency_prelim) == 2:
                currency_prelim = currency_prelim[0]
            elif len(currency_prelim) == 3:
                currency_prelim = currency_prelim[1]
            elif len(currency_prelim) > 3:
                currency_prelim = currency_prelim[0]

            if currency_prelim == "USD":
                currency = "USD"
                price = price.replace("USD ", "")
            elif currency_prelim == "EUR":
                currency = "EUR"
                price = price.replace("EUR ", "")
            else:
                currency = ""
        except:
            currency = ""

        try:
            category = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[1]").text
        except:
            category = "" 

        try:
            materials = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[2]").text
        except:
            materials = ""

        try:
            dimensions = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/section/div/div/div[2]/div/section[1]/div[4]").text
        except:
            dimensions = ""

        try:
            url = link
        except:
            url = ""

        try:
            image_url = driver.find_element_by_tag_name("background-image").text
        except:
            image_url = ""

    ret = [artist, title, year, gallery, price, currency, category, materials, dimensions, url, image_url]
    return ret


# Exports the price data into a csv file.
def exportData(l:list):
    filename = ("data/export.csv")
    with open(filename, "a", encoding="UTF-8", newline="") as f:
        w = csv.writer(f, delimiter=";", quotechar = "|")
        for item in l:
            w.writerow(item)


def setupCSV():
    filename = ("data/export.csv")
    with open(filename, "w", encoding="UTF-8", newline="") as f:
        w = csv.writer(f, delimiter=";", quotechar = "|")
        w.writerow(["artist", "title", "year", "gallery", "price", "currency", "category", "materials", "dimensions", "url", "image_url"])



if __name__ == "__main__":
    driverSetup()
    driver.get(MAIN_PAGE)
    login()
    #scrollToBottom()
    scrollThrough()
    setupCSV()

    linksFinal = []
    for item in Links:
        for x in item:
            if x not in linksFinal:
                linksFinal.append(x)

    print(len(linksFinal))

    data = []
    for link in linksFinal:
        a = scrapeData(link)
        data.append(a)

    exportData(data)
