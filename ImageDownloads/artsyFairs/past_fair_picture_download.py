# Description: This code was written to download artwork images from Artsy.
# I used requests to get the HTML code for the artwork website, where I identify
# the image based on it's class. The code also utilizes multithreading in order
# to improve download speed.
#
# Author: Milan Makany
# Organisation: Said Business School


import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import os
import shutil
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
import pandas as pd
import csv


directURLs = True


lock = Lock()
pictures_downloaded = []

IMPORT_PATH = ''
DOWNLOAD_PATH = r'D:\Said Business School\FairImages'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


EXCEL_LOCATION = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\pastFairDataDetailed.xlsx'


def importFairData():
    df = pd.read_excel(EXCEL_LOCATION)
    return df


def importFair(fileloc):
    images = []
    with open(fileloc, 'r', encoding='UTF-8', newline='') as f:
        r = csv.reader(f, delimiter=';', quotechar='|')
        for line in r:
            images.append((str(line[0]) + ';' + line[11]))
    return images


def checkValidity(url):
    parse = urlparse(url)
    return bool(parse.netloc) and bool(parse.scheme)


def getImage(urlx):
    id, url = urlx
    soup = bs(requests.get(url).content, 'html.parser')
    images = soup.find_all('img', {'class': 'Lightbox__StyledImage-sc-6dvwq-1 lhXqkP Image__BaseImage-sq2zgu-0 dAJLTk'})
    for img in images:
        img_url = img.attrs.get('src')
        if not img_url:
            continue
        if checkValidity(img_url):
            downloadImage1(id, img_url)
            print(img_url)


def downloadImage1(id, url):
    global lock
    try:
        if url not in pictures_downloaded:
            addToPictures(url)
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                filename = os.path.join(DOWNLOAD_PATH, str(fairID) + '_' + str(id) + '.' + url.split('.')[-1])
                r.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                pass
        if url in pictures_downloaded:
            pass
    except:
        print('Invalid URL or other issue.')


def downloadImageDirect(urlx):
    id, url = urlx.split(';')
    try:
        if url not in pictures_downloaded:
            # pictures_downloaded.append(url)
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                filename = os.path.join(DOWNLOAD_PATH, str(fairID) + '_' + str(id) + '.' + url.split('.')[-1])
                r.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                pass
        if url in pictures_downloaded:
            pass
    except:
        # print('Invalid URL or other issue.')
        pass

    return id


def addToPictures(url):
    pictures_downloaded.append(url)


def exportData(df):
    options = {}
    options['strings_to_formulas'] = False
    options['strings_to_urls'] = False
    with pd.ExcelWriter(EXCEL_LOCATION, options=options) as w:
        df.to_excel(w, sheet_name='Data', index=False)


if __name__ == '__main__':

    df = importFairData()
    filelocs = []
    for item in df.iterrows():
        if pd.isna(item[1][0]) == False:
            if item[1][8] != 1:
                idn = item[1][0]
                fileloc2 = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\pastFairs\data\\' + item[1][5]
                fileloc = str(idn) + ';' + fileloc2
                filelocs.append(fileloc)
                df.loc[item[0], 'Images Downloaded'] = 1

    for file_ in filelocs:
        fairID, fileloc = file_.split(';')
        website_urls = importFair(fileloc)

        if directURLs == False:
            # Multithreading implemented 02/10/2020
            pool = ThreadPool(40)
            results = pool.map(getImage, website_urls)
            print(f'Successfully downloaded ' + str(len(results)) + ' images for ' + fileloc)

        elif directURLs == True:
            pool = ThreadPool(40)
            results = pool.map(downloadImageDirect, website_urls)
            print('Successfully downloaded ' + str(len(results)) + ' images for ' + fileloc )
            
    
    exportData(df)


    



    # Old function not using syncrounous threading
    # for url in website_urls:
    #    getImage(url)

    # for image in picture_urls:
    #   a = downloadImage(image, inx)
    #  if a == True:
    # pictures_downloaded.append(image)
