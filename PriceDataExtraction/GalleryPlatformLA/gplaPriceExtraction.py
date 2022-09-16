import requests
import csv
from bs4 import BeautifulSoup
from sys import exit
import re
from datetime import date


URL = 'https://galleryplatform.la/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

# CONTAINER_CLASS = 'block--work width--small'
# CONTAINER_CLASS2 = 'block--work width--large'
# INFO_CLASS = 'info'
# PRICE_CLASS = 'price'

TODAY = date.today().strftime('%d-%m-%Y')

PRICE_EXPORT = fr'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\GalleryPlatformLA\data\price\price-{TODAY}.csv'
CONTACT_EXPORT = fr'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\GalleryPlatformLA\data\contact\contact-{TODAY}.csv'

# Gallery block are under h2


class Artwork:
    def __init__(self, artist, title, year, gallery, price, image, *args, **kwargs):
        self.artist = artist
        self.title = title
        self.year = year
        self.gallery = gallery
        self.price = price
        self.image = image

    def toList(self):
        export = [self.artist, self.title, self.year, self.gallery, self.price, self.image]
        return export


class Gallery:
    def __init__(self, soup):
        self.soup = soup
        self.name = self.extractName()
        self.email, self.website, self.description = self.extractContacts()
        self.artworks = self.extractArtworks()
    

    def addArt(self, art):
        self.artworks.append(art)


    def extractName(self):
        title = self.soup.find('header', {'class': 'title-window'})
        name = title.find('h2').text.strip()
        return name


    def extractContacts(self):
        email = ''
        website = ''
        data = self.soup.find('div', {'class': 'window-modal'})
        li = data.find('ul')
        details = li.find_all('a')
        for d in details:
            if '@' in d['href']:
                email = d.text
            if 'www' in d['href']:
                website = d['href']
            if 'http' in d['href']:
                website = d['href']
        try:
            description = li.find('li', {'class': 'no-label'}).text.strip().replace('\xa0', ' ').replace(';', ',').replace('\"', '')
        except Exception as e:
            description = ''

        return email, website, description

    def contacts(self):
        return [self.name, self.website, self.email, self.description]

    
    def extractArtworks(self):
        artworks = []
        arts = self.soup.find_all('div', {'data-component': 'work-modal'})
        for art in arts:
            infoc = art.find('div', {'class': 'info'}).text.strip()
            info = infoc.split(',')

            artistBlock = self.soup.find('div', {'class': 'block--title'})
            try:
                artist = artistBlock.text.split('\n')[1].strip()
            except:
                artist = artistBlock.text.split('\n')[0].strip()
            
            if ':' in artist:
                artist = artist.split(':')[0].strip()

            if artist in info:
                title = info[1].strip()
            else:
                title = info[0].strip()

            try:
                year = re.search(r"(?<!\d)\d{4}(?!\d)", info[2]).group()
            except:
                year = ''

            gallery = self.name

            try:
                price = art.find('span', {'class': 'price'}).text
            except:
                price = ''

            image = art.find('img')['data-src']

            aW = Artwork(artist, title, year, gallery, price, image)
            artworks.append(aW)

        return artworks


def getHTML():
    r = requests.get(URL, headers=HEADERS)
    return r.status_code, r.text


def validateResponse(response):
    code = 0
    dtype = type(response)
    if dtype == int:
        code = response
        if code == 200:
            status = True
        else:
            print(f'Error fetching website. Error code: {code}')
            status = False
    if dtype == requests.models.Response:
        code = response.status_code
        if code == 200:
            status = True
        else:
            print(f'Error fetching website. Error code: {code}')
            status = False

    return status


def getGallerySections(soup):
    sections = soup.find_all('section', {'class': 'bg-rotator'})
    return sections


if __name__ == '__main__':
    status, wsite = getHTML()
    valid = validateResponse(status)
    if valid:
        soup = BeautifulSoup(wsite, features='html.parser')
    else:
        print('Exiting...')
        exit()
    
    sections = soup.find_all('section', {'class': 'bg-rotator'})

    galleries = []
    for section in sections:
        gallery = Gallery(section)
        galleries.append(gallery)
    
    artworks = []
    contacts = []
    for gallery in galleries:
        for art in gallery.artworks:
            artworks.append(art)

    with open(PRICE_EXPORT, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';')
        csvW.writerow(['artist', 'title', 'year', 'gallery', 'price', 'image'])
        for aW in artworks:
            csvW.writerow(aW.toList())

    with open(CONTACT_EXPORT, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';')
        csvW.writerow(['name', 'website', 'email', 'description'])
        for gal in galleries:
            csvW.writerow(gal.contacts())