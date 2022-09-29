import requests
from bs4 import BeautifulSoup as bs
from multiprocessing.pool import ThreadPool
import json
import csv
import sys
from tqdm import tqdm
from datetime import date
from time import sleep


FAIRS = [
    'https://www.artsy.net/fair/sea-focus-2022',
    'https://www.artsy.net/fair/art-antwerp-2021'
]

CD = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\fairs\data\\'
TODAY = date.today().strftime('-%d-%m-%Y')

TIMEOUT = 120
HEADERS = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        }


# This section is used to generate all combination of links on the collections
# website. Necessary due to the badly coded collections site.
# The ?page=x index only works up to 100. ->
#  More artworks are accesible if we use combinations of filers.
# In case there is no local save of the combination URLs.
def longFairTags():
    arttype = [
        'painting',
        'photography',
        'sculpture',
        'prints',
        'work-on-paper',
        'design',
        'drawing',
        'installation',
        'film-slash-video',
        'jewelry',
        'performance-art'
    ]
    price = [
        'price_range=50000-%2A',
        'price_range=25000-50000',
        'price_range=10000-25000',
        'price_range=5000-10000',
        'price_range=1000-5000',
        'price_range=0-1000'
    ]

    tags = []
    for art in arttype:
        for p in price:
            tags.append('&additional_gene_ids%5B0%5D=' + art + '&' + p)
   
    return tags


def checkLongFair(fair):
    r = requests.get(fair, timeout=TIMEOUT, headers=HEADERS)
    if r.status_code == 200:
        soup = bs(r.text, 'html.parser')
    else:
        print('Error loading fair')
        sys.exit()

    numberOfArtworks = soup.find('div', {'class': 'iAatLR'}).text.strip()
    numberOfArtworks = numberOfArtworks.replace('(', '').replace(')', '')

    try:
        numberOfArtworks = int(numberOfArtworks)
        print(numberOfArtworks)
    except Exception as e:
        print(e)
        return False

    if numberOfArtworks > 3000:
        return True
    if numberOfArtworks <= 3000:
        return False


def getData(url: str):
    global pbar
    sleep(0.1)
    try:
        r = requests.get(url, timeout=120, headers=HEADERS)
        if r.status_code == 200:
            data = JSONextractor(r.text)
            pbar.update(1)
        elif r.status_code == 429:
            sleep(5)
            data = getData(url)
        else:
            data = []
            pbar.update(1)
    except TimeoutError:
        data = []
    except Exception as e:
        data = []
        print(e)

    return data


def JSONextractor(container):
    soup = bs(container, 'html.parser')
    art_json_data = soup.find('script', {'type': 'application/ld+json'})
    art_json_data = str(art_json_data).replace('<script data-reactroot=\"\" data-rh=\"\" type=\"application/ld+json\">', '')
    art_json_data = str(art_json_data).replace('</script>', '')
    try:
        JSONdata = json.loads(art_json_data)
    except:
        JSONdata = []
    
    try:
        outerblock = soup.find('div', {'class': 'hVgfsm'})
    except:
        outerblock = bs()

    # Data extracted from JSON & website
    try:
        artist = JSONdata['brand']['name'].replace('\"', '\'')
    except:
        artist = ''
    
    try:
        block = outerblock.find('a', {'class': 'gzsrpX'})
        artistURL = block.get('href')
    except:
        artistURL = ''


    try:
        titleYear = soup.find('h1', {'class': 'gDTxCv'}).text
        title = ','.join(titleYear.split(',')[:-1])
        yearCheckHolder = titleYear.split(',')[-1].strip()
    except:
        try:
            title = JSONdata['name'].split(' | ')[1].replace(';', ',').replace('\"', '\'')
            yearCheckHolder = ''
        except:
            title = ''
            yearCheckHolder = ''

    try:
        year = JSONdata['productionDate'].replace(';', ',').replace('\"', '\'')
        if year == '':
            if yearCheckHolder != '':
                year = yearCheckHolder
    except:
        year = ''

    try:
        gallery = JSONdata['offers']['seller']['name']
    except:
        try:
            gallery = JSONdata['description'].split('for sale from ')[1].split(',')[0]
        except:
            gallery = ''

    try:
        price = JSONdata['offers']['price']
    except:
        try:
            lowprice = JSONdata['offers']['lowPrice']
            highprice = JSONdata['offers']['highPrice']
            price = f'{str(lowprice)}-str{(highprice)}'
        except:
            price = ''

    try:
        currency = JSONdata['offers']['priceCurrency']
    except:
        currency = ''

    try:
        category = JSONdata['category'].replace(';', ',').replace('\"', '\'')
    except:
        category = ''

    try:
        c = JSONdata['description'].count(',')
        if JSONdata['description'].split(',')[3].split(' (')[0][4].isdigit():
            materials_preliminary = JSONdata['description'].split(',')[4:c]
            materials = ','
            materials = materials.join(materials_preliminary)
            materials = materials[1:].replace(';', ',').replace('\"', '\'')

        else:
            materials_preliminary = JSONdata['description'].split(',')[3:c]
            materials = ','
            materials = materials.join(materials_preliminary)
            materials = materials[1:].replace(';', ',').replace('\"', '\'')
    except:
        materials = ''

    try:
        height = JSONdata['height'].replace(';', ',').replace('\"', '\'')
    except:
        height = ''

    try:
        width = ' × ' + JSONdata['width'].replace(';', ',').replace('\"', '\'')
    except:
        width = ''

    try:
        depth = ' × ' + JSONdata['depth'].replace(';', ',').replace('\"', '\'')
    except:
        depth = ''

    try:
        dimensions = height + width + depth
    except:
        dimensions = ''

    try:
        soldT = JSONdata['offers']['availability'].split('/')[-1]
        
        if soldT == 'InStock':
            sold = 'False'
        elif soldT == 'OutOfStock':
            sold = 'True'
        else:
            raise ValueError
    except:
        try:
            if 'available' in JSONdata['description'].lower():
                sold = 'False'
            else:
                sold = 'True'
        except:
            sold = ''

    try:
        artwork_url = JSONdata['url']
    except:
        artwork_url = ''

    try:
        image_url = JSONdata['image']
    except:
        image_url = ''


    returnData = [artist, artistURL, title, year, gallery, price, currency, category, materials,
    dimensions, sold, artwork_url, image_url]

    return returnData


def exportData(ex: list, exloc):
    with open(exloc, 'a', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        for item in ex:
            try:
                if item != []:
                    w.writerow(item)
            except:
                pass


def setupCSV(exloc):
    with open(exloc, 'w', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(
            ['artist', 'artist_slug', 'title', 'year', 'gallery', 'price', 'currency', 'category', 'materials', 'dimensions', 'sold', 'url',
             'image_url'])


def exportURLS(urls: list, exportloc):
    with open(exportloc, 'w', encoding='UTF-8') as f:
        for line in urls:
            f.write(line + '\n')


CLASS_ID = 'GridItem__Link-l61twt-0'


def shortFairLinks(fair):
    links = []
    for x in range(100):
        sleep(0.1)
        page = fair + f'?page={x+1}'
        try:
            r = requests.get(page, timeout=TIMEOUT, headers=HEADERS)
        except:
            sleep(10)
            try:
                r = requests.get(page, timeout=TIMEOUT, headers=HEADERS)
            except:
                continue
        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            elements = soup.find_all('a', {'class': CLASS_ID})
            if len(elements) == 0:
                print(f'No elements on page {x+1}. Total number of artworks: {len(links)}')
                break
            for el in elements:
                artLink = 'https://www.artsy.net' + el['href']
                if artLink not in links:
                    links.append(artLink)
    return links


def longFairLinks(tags, fair):
    links = []
    for t in tags:
        for x in range(100):
            sleep(0.1)
            page = fair + f'?page={x+1}' + t
            try:
                r = requests.get(page, timeout=TIMEOUT, headers=HEADERS)
                if r.status_code == 200:
                    soup = bs(r.text, 'html.parser')
                    elements = soup.find_all('a', {'class': CLASS_ID})
                    if len(elements) == 0:
                        print(f'No elements on page {x+1}. Total number of artworks: {len(links)}')
                        break
                    for el in elements:
                        artLink = 'https://www.artsy.net' + el['href']
                        if artLink not in links:
                            links.append(artLink)
            except:
                pass

    return links



if __name__ == '__main__':
    for fair in FAIRS:
        fair = fair + '/artworks'
        print(fair)

        filename = fair.split('/')[-2] + TODAY
        exportloc = rf'{CD}{filename}.csv'
        url_loc = rf'{CD}urls\{filename}.txt'

        isLong = checkLongFair(fair)
        if isLong:
            fairLinks = longFairTags()
            links = longFairLinks(fairLinks, fair)
            
            print(str(len(links)) + ' URLs fetched.')
            p = ThreadPool(5)
            pbar = tqdm('Downloading Data', total=len(links))
            data = p.map(getData, links)
            #data = []
            #for link in links:
            #    observation = getData(link)
            #    data.append(observation)
            #    pbar.update()
            pbar.close()
            p.close()
            setupCSV(exportloc)
            exportData(data, exportloc)
        elif not isLong:
            links = shortFairLinks(fair)
            print(str(len(links)) + ' URLs fetched.')
            p = ThreadPool(5)
            pbar = tqdm('Downloading Data', total=len(links))
            data = p.map(getData, links)
            #data = []
            #for link in links:
            #    observation = getData(link)
            #    data.append(observation)
            #    pbar.update()
            pbar.close()
            p.close()
            setupCSV(exportloc)
            exportData(data, exportloc)
