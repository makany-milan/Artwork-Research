from selenium import webdriver
import selenium.common.exceptions as EXPECTIONS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import csv
from datetime import date
import re


username = 'dawei.zhuang@outlook.com'
password = 'ArtProject+44'

TODAY = date.today().strftime('%d-%m-%Y')

FAIRNAME = f'frieze-ny-{TODAY}.csv'
EXPORTLOC = rf'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Frieze\data\{FAIRNAME}'
CONTACTEXPORTLOC = rf'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Frieze\data\{FAIRNAME}-contacts.csv'

options = webdriver.ChromeOptions()
# maximises the window on launch
options.add_argument("--start-maximized")

driver = webdriver.Chrome(executable_path=r"C:\Users\Milan\Downloads\chromedriver.exe", options=options)
actions = ActionChains(driver)


def login():
    driver.get('https://viewingroom.frieze.com/')
    sleep(3)
    signInButton = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/button')
    signInButton.click()
    sleep(3)
    driver.find_element_by_id('pelcro-input-email').send_keys(username)
    driver.find_element_by_id('pelcro-input-password').send_keys(password)
    driver.find_element_by_id('login-submit').click()
    sleep(3)


def openCategories():
    links = [
        'https://viewingroom.frieze.com/section/11?sections%5B0%5D=11&skip=0&limit=100',
        'https://viewingroom.frieze.com/section/12?sections%5B0%5D=12&skip=0&limit=16',
        'https://viewingroom.frieze.com/section/13?sections%5B0%5D=13&skip=0&limit=200'
    ]
    return links


def openGallery(url):
    driver.get(url)
    sleep(3)
    gallery = getGalleryData()
    scrollToBottom()
    artworks = driver.find_elements_by_class_name('a16heqoh')
    resp = []
    for item in artworks:
        ret = getArtworkData(item, gallery[0])
        resp.append(ret)
    
    return gallery, resp


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


def getArtworkData(item, gallery):
    try:
        actions.move_to_element(item).perform()
    except:
        try:
            scrollLoc = item.location['y']
            driver.execute_script(f'window.scrollTo(0, {scrollLoc})')
        except:
            pass


    try:
        url = item.find_element_by_class_name('cyyxzs8').get_attribute('href')
    except:
        url = ''
    try:
        artist = item.find_element_by_class_name('cyyxzs8').text
    except:
        artist = ''
    try:
        dataBlock = item.find_element_by_class_name('name-year')
        try:
            match = re.match(r'.*([1-3][0-9]{3})', dataBlock.text)
            if match:
                year = match.group(1)
                title = dataBlock.text.replace(f', {year}', '')
            else:
                title = ''
                year = ''
        except:
            title = ''
            year = ''
    except:
        title = ''
        year = ''
    try:
        price = item.find_element_by_class_name('price').text
    except:
        price = ''
    
    try:
        block = item.find_element_by_class_name('secondary-text').text.split('\n')
        try:
            dimensions = block[1]
            materials = block[2]
        except:
            dimensions = ''
            materials = ''
    except:
        dimensions = ''
        materials = ''



    return [artist, gallery, title, year, price, dimensions, materials, url]


def createExport(exportLoc, type):
    with open(exportLoc, 'w', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='|')
        if type == 0:
            writer.writerow(['artist', 'gallery', 'title', 'year', 'price', 'dimensions', 'materials', 'url'])
        elif type == 1:
            writer.writerow(['name', 'address', 'city', 'country', 'phone', 'email', 'website'])


def exportData(data:list, exportLoc):
    with open(exportLoc, 'a', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='|')
        for line in data:   
            writer.writerow(line)


def getGalleryData():
    element = driver.find_element_by_class_name('c6xsev8')
    blocks = element.find_elements_by_class_name('c1opg6bx')
    elementsFirstBlock = blocks[0].find_elements_by_class_name('th9agxl')
    elementsSecondBlock = blocks[1].find_elements_by_class_name('th9agxl')
    numberOfElements = len(elementsFirstBlock) -2
    
    try:
        street = elementsFirstBlock[:numberOfElements]
        street = [x.text for x in street]
        street = (' ').join(street)
    except:
        street = ''
    try:
        city = elementsFirstBlock[-2].text
    except:
        city = ''
    try:
        country = elementsFirstBlock[-1].text
    except:
        country = ''
    try:
        phone = elementsSecondBlock[0].text
    except:
        phone = ''
    try:
        email = elementsSecondBlock[1].text
    except:
        email = ''

    try:
        name = driver.find_element_by_class_name('t16zl9n1').text
    except:
        name = ''

    try:
        website = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/ul/li[3]/a').get_attribute('href')
    except:
        website = ''


    return [name, street, city, country, phone, email, website]


def findGalleries():
    sleep(2)
    galleryObjs = driver.find_elements_by_class_name('cyyxzs8')
    galleries = [gallery.get_attribute('href') for gallery in galleryObjs]
    return galleries


if __name__ == '__main__':
    login()
    data = []
    galleryContacts = []
    links = openCategories()
    for link in links:
        sleep(3)
        driver.get(link)
        galleries = findGalleries()
        for gallery in galleries:
            galleryData, adat = openGallery(gallery)
            for item in adat:
                data.append(item)
            galleryContacts.append(galleryData)
                
    
    # type parameter set to 0 if export is price
    createExport(EXPORTLOC, 0)
    # type parameter set to 1 if export is contacts
    createExport(CONTACTEXPORTLOC, 1)
    exportData(data, EXPORTLOC)
    exportData(galleryContacts, CONTACTEXPORTLOC)
