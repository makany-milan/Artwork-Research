import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
from datetime import date


today = date.today()
DATE = today.strftime('%d-%m-%Y')

# Loop through pages 1-x
WEBSITE_LINK = 'https://www.sothebys.com/en/buy/gallery-network?page='
# Identify the link for each artwork on the page.
LINK_CLASS = 'link_linkStyles__fEg2r'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
}
LINK_EXPORTLOC = fr'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Sothebys\data\urls\links_{DATE}.txt'
EXPORTLOC = fr'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Sothebys\data\export_{DATE}.csv'


def getArtworks():
    links = []
    pageNumber = 1
    while True:
        website = WEBSITE_LINK + str(pageNumber)
        pageNumber += 1
        try:
            r = requests.get(website, headers=HEADERS)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.find_all('a', {'class': LINK_CLASS})
                if len(items) == 0:
                    break
                for item in items:
                    try:
                        artwork = 'https://www.sothebys.com/' + item['href']
                        links.append(artwork)
                    except Exception as e:
                        print(e)
                        break
            else:
                print(r.status_code)
                break
        except Exception as e:
            print(e)
            break

    return links


def exportLinks(links: list):
    with open(LINK_EXPORTLOC, 'w', encoding='utf-8') as w:
        for item in links:
            w.write(item + '\n')


def importLinks():
    links = []
    with open(LINK_EXPORTLOC, 'r', encoding='utf-8') as r:
        for line in r:
            links.append(line.strip())
    return links


def getData(url: str):
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        data = extractData(soup, url)
    return data


def extractData(soup: BeautifulSoup, url):
    try:
        artistObj = soup.find('h2', {'class': 'typography_h2__AK-R9'})
        artist = artistObj.text.replace(';', '')
    except Exception as e:
        artist = ''
    try:
        title = soup.find('h1', {'class': 'typography_h1__2vMVJ'}).text.replace(';', '')
    except Exception as e:
        title = ''
    try:
        yearObj = soup.find('p', {'class': 'paragraph-module_paragraph14Regular__2yq4S'})
        year = yearObj.text.replace(';', '')
    except Exception as e:
        year = ''
    try:
        gallery = soup.find('p', {'class': 'caps-module_caps14Medium__2ajFO'}).text.split(' - ')[1].replace(';', '')
    except Exception as e:
        gallery = ''
    try:
        materialObj = yearObj.parent.nextSibling
        material = materialObj.text
    except Exception as e:
        material = ''
    try:
        priceCurr = soup.find_all('p', {'class': 'label-module_label16Medium__2HDfw'})[1].text
        try:
            price = priceCurr.split(' ')[0]
            currency = priceCurr.split(' ')[1]
        except Exception as e:
            price = priceCurr
            currency = ''
    except Exception as e:
        price = ''
        currency = ''
    try:
        dimensionsList = soup.find_all('div', {'class': 'inner_html_innerHtml__2OIfa'})
        height, width, depth = '', '', ''
        for item in dimensionsList:
            dim = item.text
            parts = dim.split(': ')
            if parts[0] == 'Height':
                height = parts[1]
            elif parts[0] == 'Width':
                width = parts[1]
            elif parts[0] == 'Depth':
                depth = parts[1]
        if depth != '':
            dimensions = ' x '.join([height, width, depth])
        else:
            dimensions = ' x '.join([height, width])
    except Exception as e:
        dimensions = ''
    try:
        image = soup.find('img', {'class': 'carousel_mainImage__2A5Iz carousel_zoomOut__1uiG1'})['src']
    except Exception as e:
        image = ''

    return [artist, title, year, gallery, price, currency, material, dimensions, url, image]


# [artist, title, year, gallery, price, currency, material, dimensions, url, image]
def exportData(data):
    with open(EXPORTLOC, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';', quotechar='|')
        csvW.writerow(['artist', 'title', 'year', 'gallery', 'price', 'currency', 'material', 'dimensions', 'url', 'image_url'])
        for row in data:
            csvW.writerow(row)


if __name__ == '__main__':
    linksCollected = False
    if not linksCollected:
        artworkLinks = getArtworks()
        exportLinks(artworkLinks)
    elif linksCollected:
        artworkLinks = importLinks()

    data = []
    pbar = tqdm(desc='Downloading Data', total=len(artworkLinks))
    for link in artworkLinks:
        data.append(getData(link))
        pbar.update(1)
    pbar.close()
    exportData(data)
