import requests
from bs4 import BeautifulSoup
from datetime import date

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from time import sleep

import csv


DATE = date.today().strftime('%d-%m-%Y')

# 42 artworks / page
URL = 'https://fiac.viewingrooms.com/artworks/?skip={}'
COOKIE_BUTTON = '/html/body/div[6]/div[3]/div/div[1]/div/div[2]/div/button[2]'
EMAIL_FIELD = '/html/body/div[3]/div[1]/div/div[4]/form/div[1]/div[1]/input'
CONFIRM_BUTTOM = '/html/body/div[3]/div[1]/div/div[4]/form/div[1]/div[3]/label'
LOGIN_BUTTON = '/html/body/div[3]/div[1]/div/div[4]/form/div[1]/div[4]/div[1]/a'

ITEM_XPATH = '/html/body/div[1]/div[2]/div/div[3]/div/div[1]/div[1]/ul[{}]/li[{}]/div/div[1]/div[1]/a'



DRIVER = Chrome(r'C:\Users\makan\Downloads\chromedriver.exe')
DRIVER.get('https://fiac.viewingrooms.com/artworks/')
sleep(5)
DRIVER.find_element_by_xpath(COOKIE_BUTTON).click()
sleep(1)
DRIVER.find_element_by_xpath(EMAIL_FIELD).send_keys('dawei.zhuang@outlook.com')
sleep(5)
# The confirm pseudo button has to be clicked manually.
# Could be automated, however too lenghty for now.
DRIVER.find_element_by_xpath(LOGIN_BUTTON).click()


artworks = []
for x in range(50): # change back to 50
    sleep(2)
    currNo = x * 42
    DRIVER.get(URL.format(currNo))
    sleep(2)
    for ul in range(3): # change back to 3
        ulID = ul + 1
        for li in range(14): # change back to 14
            liID = li + 1
            try:
                element = DRIVER.find_element_by_xpath(ITEM_XPATH.format(ulID, liID))
                link = element.get_attribute('href')
                artworks.append(link)
            except:
                pass

data = []

ARTIST = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/h1/div' # LSTRIP & RSTRIP!
TITLE = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[2]/span[1]'
YEAR = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[2]/span[3]'
MEDIUM = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[3]/div[1]'
DIMENSIONS = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[3]/div[2]'
GALLERY = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[1]/a'
PRICE = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[5]/div' #LSTRIP & RSTRIP!, eur and dollar - split(/)
PRICE2 = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[2]/div[1]/div[4]/div'
IMAGE = '/html/body/div[3]/div[2]/div/div[1]/div/div[3]/div[1]/div/span/span/img[2]' # SRC


for art in artworks:
    sleep(2)
    DRIVER.get(art)
    sleep(2)
    try:
        artistO = DRIVER.find_element_by_xpath(ARTIST)
        artist = artistO.text.lstrip().rstrip()
    except:
        artist = ''
    try:
        titleO = DRIVER.find_element_by_xpath(TITLE)
        title = titleO.text
    except:
        title = ''
    try:
        yearO = DRIVER.find_element_by_xpath(YEAR)
        year = yearO.text
    except:
        year = ''
    try:
        galleryO = DRIVER.find_element_by_xpath(GALLERY)
        gallery = galleryO.text
    except:
        gallery = ''
    try:
        priceO = DRIVER.find_element_by_xpath(PRICE)
        priceRaw = priceO.text.split('\n')[0]
        try:
            priceEUR, priceUSD = priceRaw.lstrip().rstrip().split(' / ')
            priceEUR = priceEUR.strip('€').strip().strip(',')
            priceUSD = priceUSD.strip('$').strip().strip(',')
        except:
            priceEUR = priceRaw
            priceUSD = priceRaw
    except:
        priceEUR = ''
        priceUSD = ''

    if priceEUR == '':
        try:
            priceO = DRIVER.find_element_by_xpath(PRICE2)
            priceRaw = priceO.text.split('\n')[0]
            try:
                priceEUR, priceUSD = priceRaw.lstrip().rstrip().split(' / ')
                priceEUR = priceEUR.strip('€').strip(',').strip()
                priceUSD = priceUSD.strip('$').strip(',').strip()
            except:
                priceEUR = priceRaw
                priceUSD = priceRaw
        except:
            priceEUR = ''
            priceUSD = ''
    else:
        pass
    try:
        mediumO = DRIVER.find_element_by_xpath(MEDIUM)
        medium = mediumO.text
    except:
        medium = ''
    try:
        dimensionO = DRIVER.find_element_by_xpath(DIMENSIONS)
        dimension1 = dimensionO.text.split('\n')[0]
        try:
            dimension = dimension1.split('|')[1]
        except:
            dimension = dimension1
    except:
        dimension = ''
    try:
        url = art
    except:
        url = ''
    try:
        imageO = DRIVER.find_element_by_xpath(IMAGE)
        image = imageO.get_attribute('src')
    except:
        image = ''

    export = [artist, title, year, gallery, priceEUR, priceUSD, medium, dimension, url, image]

    data.append(export)


with open(rf'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\FIAC\data\export_{DATE}.csv', 'w', newline='', encoding='utf-8') as w:
    csvW = csv.writer(w, delimiter=';')
    csvW.writerow(['artist', 'title', 'year', 'gallery', 'priceEUR', 'priceUSD', 'medium', 'dimensions', 'url', 'image_url'])
    for line in data:
        csvW.writerow(line)


sleep(10)
DRIVER.close()
