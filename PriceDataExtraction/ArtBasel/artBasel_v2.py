import requests
import json
from bs4 import BeautifulSoup as bs
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import csv
from multiprocessing.pool import ThreadPool


REQUEST_HEADERS = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}
MAIN_PAGE = "https://www.artbasel.com/ovr/show?activeTab=artworks&orderBy=random(4705),id"
TIMEOUT = 10

URL_EXPORT_LOCATION = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\ArtBasel\data\links\\'
EXPORT_LOCATION = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\ArtBasel\data\\'

TODAY = date.today().strftime('%d-%m-%Y')


def make_request(url):
    r = requests.get(url, headers=REQUEST_HEADERS)
    if r.status_code == 200:
        data = extract_data(r.text)
    else:
        data = []
    
    return data


def extract_data(html):
    soup = bs(html, 'html.parser')
    data_container = soup.find('script', {'type': 'application/json'})
    json_data = json.loads(data_container.contents[0])

    try:
        artist = json_data['props']['pageProps']['pageMetaInfo']['artistName']
    except:
        artist = ''

    try:
        title = json_data['props']['pageProps']['pageMetaInfo']['displayName']
    except:
        title = ''

    try:
        year = json_data['props']['pageProps']['pageMetaInfo']['year']
        year = str(year)
    except:
        year = ''

    
    try:
        second_currency = json_data['props']['pageProps']['pageMetaInfo']['secondCurrency']
        if second_currency == '':
            currency = 'USD'
        else:
            currency = second_currency
    except:
        currency = ''

    try:
        low_price = json_data['props']['pageProps']['pageMetaInfo']['fromPrice']
        low_price = str(low_price)
    except:
        low_price = ''
    
    try:
        high_price = json_data['props']['pageProps']['pageMetaInfo']['toPrice']
        high_price = str(high_price)
    except:
        high_price = ''

    try:
        price_inusd = json_data['props']['pageProps']['pageMetaInfo']['priceInUsd']
        price_inusd = str(price_inusd)
    except:
        price_inusd = ''

    try:
        if high_price != '':
            if low_price != '':
                price = f'{low_price}-{high_price}'
            if low_price == '':
                price = f'-{high_price}'
        else:
            if low_price != '':
                price = low_price
            if low_price == '':
                if price_inusd != '':
                    price = price_inusd
                    currency = 'USD'
                else:
                    price = ''
            
    except:
        price = ''
    
    try:
        sold_status = json_data['props']['pageProps']['pageMetaInfo']['sold']
        if sold_status == False:
            sold = 'False'
        elif sold_status == True:
            sold = 'True'
    except:
        sold = ''

    try:
        materials = json_data['props']['pageProps']['pageMetaInfo']['materials']
    except:
        materials = ''

    try:
        category = json_data['props']['pageProps']['pageMetaInfo']['medium']['name']
    except:
        category = ''
    
    try:
        image_url = json_data['props']['pageProps']['pageMetaInfo']['imageUrl']
    except:
        image_url = ''

    try:
        gallery = json_data['props']['pageProps']['pageMetaInfo']['galleryName']
    except:
        gallery = ''

    try:
        url_slug = json_data['props']['pageProps']['pageMetaInfo']['shareUrl']
        url = 'www.artbasel.com' + url_slug
    except:
        url = ''

    try:
        
        try:
            width = json_data['props']['pageProps']['pageMetaInfo']['width']
            width = str(width)
        except:
            width = ''
        try:
            height = json_data['props']['pageProps']['pageMetaInfo']['height']
            height = str(height)
        except:
            height = ''
        try:
            unit = json_data['props']['pageProps']['pageMetaInfo']['unitMeasure']
        except:
            unit = ''
        
        if unit == 'inches':
            if height != '':
                if width != '':
                    dimensions = f'{height} × {width} in'
                else:
                    dimensions = f'{height} in'
            elif width != '':
                dimensions = f'{width} in'
            else:
                dimensions = ''
        else:
            if height != '':
                if width != '':
                    dimensions = f'{height} × {width} cm'
                else:
                    dimensions = f'{height} cm'
            elif width != '':
                dimensions = f'{width} cm'
            else:
                dimensions = ''
    except Exception as e:
        print(e)
        dimensions = ''

    data = [artist, title, year, gallery, price, currency, category, materials, dimensions, sold, url, image_url]

    return data


def scrollThrough():
    driver.get(MAIN_PAGE)
    sleep(2)
    links = []
    for x in range(500):
        try:
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            sleep(1)
            links_found = getLinks()
            for link in links_found:
                if link not in links:
                    links.append(link)
            
        except:
            sleep(2)
            pass
    return links


def getLinks():
    links = []
    
    try:
        objs = driver.find_elements_by_class_name('artwork-item')
        for obj in objs:
            try:
                link = obj.find_element_by_tag_name('a').get_attribute('href')
                links.append(link)
            except:
                pass
    except Exception as e:
        print(e)
    
    return links


def driverSetup():
    global driver

    settings = webdriver.ChromeOptions()
    # This option starts the webdriver maximized to the display.
    settings.add_argument('--start-maximized')
    settings.add_experimental_option('detach', True)

    driver = webdriver.Chrome(r'C:\Users\Milan\Downloads\chromedriver.exe', options=settings)


def export_urls(urls):
    with open(URL_EXPORT_LOCATION + TODAY + '.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url)


def import_urls():
    links = []
    with open(URL_EXPORT_LOCATION + TODAY + '.txt', 'r', encoding='utf-8') as f:
        for url in f:
            links.append(url.strip())

    return links


def export_data(data):
    with open(EXPORT_LOCATION + 'OVR-' + TODAY + '.csv', 'a', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        for obs in data:
            w.writerow(obs)


def setupCSV():
    with open(EXPORT_LOCATION + 'OVR-' + TODAY + '.csv', 'w', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['artist', 'title', 'year', 'gallery', 'price', 'currency', 'category', 'materials', 'dimensions', 'sold', 'url','image_url'])


if __name__ == '__main__':
    links_available = True

    if not links_available:
        driverSetup()
        links = scrollThrough()
        driver.close()
        export_urls(links)
    else:
        links = import_urls()

    data = []

    p = ThreadPool(5)

    #for link in links:
    #    observation = make_request(link)
    #    data.append(observation)
    data = p.map(make_request, links)
    p.close()

    setupCSV()
    export_data(data)
    