import requests
from bs4 import BeautifulSoup as bs
import json
import csv
import sys
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep


CD = r'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\pastFairs\data\v2\\'
EXCEL_LOCATION = r'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\pastFairDataDetailed_v2.xlsx'

CLASS_ID = 'GridItem__Link-l61twt-1'
TIMEOUT = 120


def importFairData():
    df = pd.read_excel(EXCEL_LOCATION)
    return df


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
            tags.append('&medium=' + art + '&' + p)
            
    return tags


def getData(url: str):
    global pbar
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'From': 'david.zhuang@outlook.com'}
    try:
        r = requests.get(url, timeout=120, headers=headers)

        if r.status_code == 200:
            data = JSONextractor(r.text)
        else:
            data = ['']
            #print(r.status_code)
    except TimeoutError:
        data = ['']
        #print('TIMEOUT')

    pbar.update(1)
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
        titleYear = soup.find('h1', {'class': 'bptVBo'}).text
        title = ','.join(titleYear.split(',')[:-1])
        yearCheckHolder = titleYear.split(',')[-1].strip()
    except:
        try:
            title = JSONdata['name'].text.split(' | ')[1].replace(';', ',').replace('\"', '\'')
            yearCheckHolder = ''
        except:
            title = ''
            yearCheckHolder = ''

    try:
        year = JSONdata['productionDate'].replace(';', ',').replace('\"', '\'')
        if yearCheckHolder != '':
            if year != yearCheckHolder:
                if year == '':
                    year = yearCheckHolder
    except:
        year = ''

    try:
        block = soup.find('div', {'data-test': 'aboutTheWorkPartner'})
        galleryBlock = block.find('a')
        gallery = galleryBlock.find('div', {'class': 'glLAxv'}).text
        galleryURL = galleryBlock.get('href')
    except:
        galleryURL = ''
        try:
            # in soup there are no classes to be found..
            # check for a solution
            gallery1 = soup.find('div', {'class': 'Box-sc-15se88d-0 Text-sc-18gcpao-0 dSdejU'})
            gallery = gallery1.text
        except:
            try:
                gallery1 = soup.find('a', {'class': 'GALLERY_CLASS'})
                gallery = gallery1.findChild().text.replace(';', ',').replace('\"', '\'')
            except:
                gallery = ''

    try:
        price = JSONdata['offers']['price']
    except:
        try:
            lowprice = JSONdata['offers']['lowPrice']
            highprice = JSONdata['offers']['highPrice']
            price = str(lowprice) + '-' + str(highprice)
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
            if 'available' in JSONdata['description'].lower():
                sold = 'False'
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


    returnData = [artist, artistURL, title, year, gallery, galleryURL, price, currency, category, materials,
    dimensions, sold, artwork_url, image_url]

    return returnData


def shortFairLinks(fair):
    links = []
    for x in range(100):
        page = fair + f'?page={x+1}'
        try:
            r = requests.get(page, timeout=TIMEOUT)
        except:
            sleep(5)
            try:
                r = requests.get(page, timeout=TIMEOUT)
            except:
                continue
        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            elements = soup.find_all('a', {'class': CLASS_ID})
            if len(elements) == 0:
                break
            for el in elements:
                artLink = 'https://www.artsy.net' + el['href']
                if artLink not in links:
                    links.append(artLink)
    return links


def longFairLinks(fair, tags):
    links = []
    for t in tags:
        for x in range(100):
            page = fair + f'?page={x+1}' + t
            r = requests.get(page, timeout=TIMEOUT)
            if r.status_code == 200:
                soup = bs(r.text, 'html.parser')
                elements = soup.find_all('a', {'class': CLASS_ID})
                if len(elements) == 0:
                    break
                for el in elements:
                    artLink = 'https://www.artsy.net' + el['href']
                    if artLink not in links:
                        links.append(artLink)
  
    return links


def exportData(exportname, ex: list):
    with open(exportname, 'a', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        for idnum, item in enumerate(ex):
            uid = idnum + 1
            newList = []
            newList.append(uid)
            for i in item:
                newList.append(i)
            try:
                w.writerow(newList)
            except:
                pass


def setupCSV(exportname):
    with open(exportname, 'w', encoding='UTF-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['id', 'artist', 'artist_slug', 'title', 'year', 'gallery', 'gallery_slug', 'price', 'currency', 'category', 'materials', 'dimensions', 'sold', 'url', 'image_url'])


def checkLongFair(fair):
    r = requests.get(fair, timeout=TIMEOUT)
    if r.status_code == 200:
        soup = bs(r.text, 'html.parser')
    else:
        print('Error loading fair')
        sys.exit()

    numberOfArtworks = soup.find('div', {'class': 'iAatLR'}).text.strip()
    numberOfArtworks = numberOfArtworks.replace('(', '').replace(')', '')

    try:
        numberOfArtworks = int(numberOfArtworks)
    except Exception as e:
        print(e)
        return False

    if numberOfArtworks > 2000:
        return True
    if numberOfArtworks <= 2000:
        return False


if __name__ == '__main__':
    fairData: pd.DataFrame = importFairData()
    for i in fairData.iterrows():
        if i[1][6] != 1:
            fairname = i[1][1]
            print(fairname)
            exportloc = CD + i[1][5]
            fairURL = i[1][4] + r'/artworks'
            isLong = checkLongFair(fairURL)
            if isLong:
                tags = longFairTags()
                links = longFairLinks(fairURL, tags)
            elif not isLong:
                links = shortFairLinks(fairURL)
            setupCSV(exportloc)
            print(str(len(links)) + ' URLs fetched for ' + fairname)
            fairData.loc[i[0], 'Data Collected'] = 1
            fairData.loc[i[0], 'Number of Artworks'] = len(links)

            export = []
            pbar = tqdm(desc='Downloading Artworks', total=len(links))
            with ThreadPoolExecutor(max_workers=40) as executor:
                future = {executor.submit(getData, link): link for link in links}
                for fut in as_completed(future):
                    try:
                        a = fut.result()
                        export.append(a)
                    except:
                        pass
            pbar.close()
            exportData(exportloc, export)

            options = {}
            options['strings_to_formulas'] = False
            options['strings_to_urls'] = False
            try:
                with pd.ExcelWriter(EXCEL_LOCATION, options=options) as w:
                    fairData.to_excel(w, sheet_name='Data', index=False)
                #print('Data Updated.')
            except:
                print('Data Update Failed')
