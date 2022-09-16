from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import json
import csv
import os
from datetime import datetime


EXPORT_LOC = r'C:\Users\makan\OneDrive\Desktop\SBS\Artworks\Artissima\data\\'

DATE = datetime.now()
TODAY_DATE = DATE.strftime('%d-%m-data')

FAIR = 'https://www.artissima.art/artworks/?_sf_s=&_sft_edition=2020'

# initialize cromedriver - must be downloaded in order to run the code - https://chromedriver.chromium.org/
# you can use any browser driver that you prefer!
# change parameter to download location
# setting up options for the webdriver
options = webdriver.ChromeOptions()
# maximises the window on launch
options.add_argument('--start-maximized')

driver = webdriver.Chrome(executable_path=r'C:\Users\makan\Downloads\chromedriver.exe', options=options)


# function from StackOverflow @ Cuong Tran
def scrollToBottom():

    # get scroll height
    last_height = driver.execute_script('return document.body.scrollHeight')
    bottom = False
    while not bottom:
        try:
            sleep(3)
            # scroll down to bottom
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            # wait for page to load
            sleep(3)
            # calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                bottom = True

            last_height = new_height

        except:
            pass


def getURLs():
    urls = []
    errorcount = 0
    for x in range(2000):
        try:
            element = driver.find_element_by_xpath(f'/html/body/div[3]/div/div[4]/div/div[{x}]/a')
            url = element.get_attribute('href')
            urls.append(url)
            errorcount = 0

        except NoSuchElementException:
            errorcount += 1
            pass

        except StaleElementReferenceException:
            errorcount += 1
            try:
                pass
            except:
                pass
            try:
                element = driver.find_element_by_xpath(f'/html/body/div[3]/div/div[4]/div/div[{x}]/a')
                url = element.get_attribute('href')
                urls.append(url)
            except:
                pass
        except ElementClickInterceptedException:
            errorcount += 1
            try:
                element = driver.find_element_by_xpath(f'/html/body/div[3]/div/div[4]/div/div[{x}]/a')
                url = element.get_attribute('href')
                urls.append(url)
            except:
                pass
        except Exception as e:
            errorcount += 1
            print(e)
            pass

        if errorcount > 20:
            break

    print(len(urls))

    return urls


def exportURLs(links:list):
    with open(EXPORT_LOC+TODAY_DATE+'-urls.txt', 'w', encoding='UTF-8') as f:
        for item in links:
            try:
                f.write(item + '\n')
            except Exception as e:
                print(e)


def importURLs():
    urls = []
    with open(EXPORT_LOC+TODAY_DATE+'-urls.txt', 'r', encoding='UTF-8') as f:
        for item in f:
            urls.append(item.strip())

    return urls


def getData(url:str):
    headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }   
    try:
        r = requests.get(url, timeout=20, headers=headers)
        
        if r.status_code == 200:
            data = JSONextractor(r.text, url)
        else:
            data = ['']
            print('Error during download: ' + url)
    except TimeoutException:
        data = ['']
        print('TIMEOUT')
    except:
        data = ['']

    return data


def JSONextractor(container, url):
    soup = BeautifulSoup(container,'html.parser')
    data = soup.find_all('div', {'class': 'whats-data'})
    cTitle = soup.find('div', {'class': 'breadcrumbs'})

    try:
        title = cTitle.text.replace('The Fair', '').split('\n')[-1].strip().replace(';', '')
    except:
        title = ''

    try:
        name = data[0].text.replace('Artist', '').strip().replace(';', '')
    except:
        name = ''

    try:
        year = data[6].text.replace('Year', '').strip().replace(';', '')
    except:
        year = ''

    try:
        gallery = data[4].text.replace('Gallery', '').strip().replace(';', '')
    except:
        gallery = ''

    try:
        price1 = data[3].text.replace('Price (VAT excluded)', '').strip()
        price = price1.split(' ')[0]
        if price == 'Price':
            price = ''
        symbol = price1.split(' ')[1]
        if symbol == '€':
            currency = 'EUR'
        elif symbol == '£':
            currency = 'GBP'
        elif symbol == '$':
            currency = 'USD'
        else:
            currency = ''
    except:
        price = ''
        currency = ''

    try:
        materials = data[1].text.replace('Materials', '').strip().replace(';', '')
    except:
        materials = ''

    try:
        dimensions1 = data[7].text.replace('Size', '').strip()
        dimensions = ''.join(dimensions1.split()).replace('(h)', '').replace('(l)', '').replace('(w)', '').replace(';', '')
    except:
        dimensions = ''

    try:
        image1 = soup.find('div', {'class': 'img-container'})
        image = image1.img['src']
    except:
        try:
            image1 = soup.find('div', {'class': 'slick-for'})
            image = image1.img['src']
        except:
            image = ''


    export = [name, title, year, gallery, price, currency, materials, dimensions, url, image]

    return export


def exportData(ex:list):
    with open(EXPORT_LOC+'artissima-'+TODAY_DATE+'.csv', 'a', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter = ';', quotechar = '|')
        for item in ex:
            try:
                w.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])
            except:
                pass


def setupCSV():
    with open(EXPORT_LOC+'artissima-'+TODAY_DATE+'.csv', 'w', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';', quotechar = '|')
        w.writerow(['artist', 'title', 'year', 'gallery', 'price', 'currency', 'materials', 'dimensions', 'url', 'image_url'])


if __name__ == '__main__':

    saved = False

    if saved == False:
        driver.get(FAIR)

        try:
            driver.find_element_by_class_name('cookies_bottone').click()
        except:
            pass

        scrollToBottom()
        links = getURLs()
        exportURLs(links)

    if saved == True:
        links = importURLs()
        print('Successfully imported ' + str(len(links)) + ' artworks.')

    driver.close()

    setupCSV()
    export = []

    with ThreadPoolExecutor(max_workers=40) as executor:
        future = {executor.submit(getData, link): link for link in links}
        for fut in as_completed(future):
            try:
                a = fut.result()
                export.append(a)
                print(a)
            except:
                pass


    exportData(export)