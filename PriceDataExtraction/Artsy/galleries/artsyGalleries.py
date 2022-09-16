import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from datetime import date

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common import exceptions

from time import sleep
import os
from tqdm import tqdm


BASE_URL = 'https://www.artsy.net/galleries?location={}&category={}'


CATEGORIES = [
    '19th-century-art', '20th-century-design', 'african-art',
    'ancient-art-artifacts-and-antiquities', 'ceramics',
    'chinese-contemporary-art', 'contemporary', 'contemporary-design',
    'contemporary-glass', 'contemporary-realist-painting-and-sculpture',
    'drawings', 'east-asian-art', 'eastern-european-art', 'emerging-art',
    'emerging-design', 'established', 'indian-art', 'jewelry',
    'latin-american-art', 'mid-career', 'middle-eastern-art',
    'modern', 'modern-british', 'new-media-and-video', 'old-masters',
    'outsider-art', 'painting', 'photography', 'pop-art',
    'portfolios-and-books', 'print-publishers-and-print-dealers',
    'prints-and-multiples', 'sculpture',
    'south-asian-and-southeast-asian-art', 'spanish-contemporary-art',
    'traditional-art-of-africa-oceania-and-the-americas',
    'traditional-asian-art', 'urban-art-slash-street-art'
    ]
LOCATIONS = [
    'barcelona-spain', 'berlin-germany', 'brussels-belgium', 'buenos-aires-argentina',
    'dubai-united-arab-emirates', 'hong-kong-hong-kong', 'istanbul-turkey',
    'london-united-kingdom', 'los-angeles-ca-usa', 'mexico-city-mexico', 'miami-fl-usa',
    'milan-italy', 'moscow-russia', 'new-york-ny-usa', 'paris-france', 'san-francisco-ca-usa',
    'seoul-south-korea', 'singapore-singapore', 'sydney-australia', 'sao-paulo-brazil',
    'tokyo-japan', 'toronto-canada'
]
HEADERS = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    }
LOADTIME = 3
FILELOC = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\galleries\galleryListCategory\\'


# function from StackOverflow @ Cuong Tran
def scrollToBottom(driver):
    try:
        # scroll down to bottom
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # wait for page to load
        sleep(10)
    except:
        pass


def getGalleries():
    wD = Chrome(r'C:\Users\Milan\Downloads\chromedriver.exe')
    galleries = {}
    total = 0
    lenght = len(LOCATIONS) * len(CATEGORIES)
    pbar = tqdm(desc='Fetching Galleries', total=lenght)
    for cat in CATEGORIES:
        galleryCategory = {}
        for loc in LOCATIONS:
            gals = []
            url = BASE_URL.format(loc, cat)
            wD.get(url)
            sleep(LOADTIME)
            scrollToBottom(wD)
            resultsGrid = wD.find_element_by_class_name('galleries-institutions-results-grid')
            galObjs = resultsGrid.find_elements_by_class_name('partner-featured-image')
            for galObj in galObjs:
                galurl = galObj.get_attribute('href')
                gals.append(galurl)
            if len(gals) > 0:
                galleryCategory[loc] = gals
                total += len(gals)
            elif len(gals) == 0:
                pass
            pbar.update()
        galleries[cat] = galleryCategory
        exportGalleryURLS(galleries)
    pbar.close()
    print(f'Total number of galleries found: {total}/3322')
    return galleries


def exportGalleryURLS(galleryURLS):
    for category in galleryURLS:
        for region in galleryURLS[category]:
            filename = category + ';' + region + '.txt'
            with open(FILELOC + filename, 'w', encoding='utf-8') as w:
                for item in galleryURLS[category][region]:
                    w.write(item + '\n')


def importGalleryURLS():
    galleryURLS = {}
    files = os.listdir(FILELOC)
    for file in files:
        category, location = file.split('.')[0].split(';')
        urls = []
        with open(os.path.join(FILELOC, file), 'r', encoding='utf-8') as r:
            for line in r:
                urls.append(line.strip())
        galleryURLS[category][location] = urls
    return galleryURLS







class Gallery:
    def __init__(self, url):
        self.url = url




if __name__ == '__main__':
    exported = False
    if not exported:
        galleryURLS = getGalleries()
    elif exported:
        galleryURLS = importGalleryURLS()
    

