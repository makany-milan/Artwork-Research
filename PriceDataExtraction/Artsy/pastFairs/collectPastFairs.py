from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException, StaleElementReferenceException

import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd

from time import sleep
from multiprocessing.pool import ThreadPool

MAINPAGE = 'https://www.artsy.net/art-fairs'
SAVED = True
URLLOC = r'C:\Users\makan\OneDrive\Desktop\SBS\Artworks\Artsy\past_fairs\pastFairURLs.txt'
EXPORTLOC = r'C:\Users\makan\OneDrive\Desktop\SBS\Artworks\Artsy_Complete_Code\past_fairs\pastFairData_v2.xlsx'
LOADT = 3

# initialize cromedriver - must be downloaded in order to run the code - https://chromedriver.chromium.org/
# you can use any browser driver that you prefer!
# change parameter to download location
# setting up options for the webdriver
options = ChromeOptions()
# maximises the window on launch
options.add_argument('--start-maximized')
DRIVER = Chrome(executable_path=r'C:\Users\Milán\Downloads\chromedriver.exe', options=options)


def openMainPage():
    DRIVER.get(MAINPAGE)


# function from StackOverflow @ Cuong Tran
def scrollToBottom():
    # get scroll height
    last_height = DRIVER.execute_script('return document.body.scrollHeight')
    bottom = False
    while not bottom:
        try:
            # scroll down to bottom
            DRIVER.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            # wait for page to load
            sleep(LOADT)
            # calculate new scroll height and compare with last scroll height
            new_height = DRIVER.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                bottom = True
            last_height = new_height
        except:
            pass

    # scroll back to the top
    # DRIVER.execute_script('window.scrollTo(0, 0)')
    # sleep(LOADT)


def clickMoreFairs():
    buttonID = 'fairs-see-more'
    while True:
        scrollToBottom()
        try:
            DRIVER.find_element_by_id(buttonID).click()
        except ElementNotInteractableException:
            break
        except NoSuchElementException as e:
            print(e)
            break
        except ElementClickInterceptedException as e:
            print(e)
            break
        except StaleElementReferenceException as e:
            print(e)
            break


def fetchFairURLs():
    urls = []
    className = 'fairs__past-fair'
    fairs = DRIVER.find_elements_by_class_name(className)
    print(len(fairs))
    for f in fairs:
        urls.append(f.get_attribute('href'))

    return urls


def exportURLs(li:list):
    with open(URLLOC, 'w') as f:
        for l in li:
            f.write(l + '\n')


def expandFairs():
    openMainPage()
    clickMoreFairs()
    urls = fetchFairURLs()
    exportURLs(urls)

    return urls


def importFairURLs():
    urls = []
    with open(URLLOC, 'r') as f:
        for line in f:
            urls.append(line.strip())
    return urls


def getFairData(indx:int, url:str):
    global df
    r = requests.get(url)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        title1 = soup.find('title').text.split(' | ')[0]
        title2 = title1.split(' ')[:-1]

        try:
            date = soup.find('div', {'class': 'eNbxOy'}).text
        except:
            date = ''
        try:
            holder = date.split(', ')[1]
            date = date.split(', ')[0]
        except:
            pass

        title = ' '.join(title2)
        year = title1.split(' ')[-1]
        df.loc[indx] = [title, year, date, url]

        print(indx)
    else:
        print('ERROR ' + str(r.status_code))

    return r.status_code




if __name__ == '__main__':
    if SAVED:
        DRIVER.close()
        urls = importFairURLs()
    if not SAVED:
        urls = expandFairs()
        DRIVER.close()
        
    df = pd.DataFrame(columns=['Fair', 'Year', 'Date', 'URL'])

    pool = ThreadPool(40)
    results = pool.map(getFairData, enumerate(urls))

    print(df)

    with pd.ExcelWriter(EXPORTLOC) as w:
        df.to_excel(w, sheet_name='Data', index=False)
