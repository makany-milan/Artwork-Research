# Description: This code was written to download artwork images from Artsy.
# I used requests to get the HTML code for the artwork website, where I identify
# the image based on it's class. The code also utilizes multithreading in order
# to improve download speed.
#
# Author: Milan Makany
# Organisation: Said Business School



import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import os
import shutil
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool


inx = 1
lock = Lock()
lock2 = Lock()

active_pictures = []


DOWNLOAD_PATH = r'C:\Users\makan\OneDrive\Desktop\SBS\Artworks\artwork_pictures\\'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def importWebsites():
    website_urls = []
    with open('artwork_masterlist.txt', 'r') as f:
        for line in f:
            ref = line.strip()
            website_urls.append(ref)
    return website_urls


def importDownloaded():
    pictures_downloaded = []
    with open('artwork_pictures/pictures.txt', 'r') as f:
        for line in f:
            ref = line.strip()
            pictures_downloaded.append(ref)
    return pictures_downloaded


def checkValidity(url):
    parse = urlparse(url)
    return bool(parse.netloc) and bool(parse.scheme)


def getImage(url):
    soup = bs(requests.get(url).content, 'html.parser')
    images = soup.find_all('img', {'class': 'Lightbox__StyledImage-sc-6dvwq-1 lhXqkP Image__BaseImage-sq2zgu-0 dAJLTk'})
    for img in images:
        img_url = img.attrs.get('src')
        if not img_url:
            continue
        if checkValidity(img_url):
            if img_url not in active_pictures:
                active_pictures.append(img_url)
                addToPictures(img_url)
                downloadImage(img_url)
                print(img_url)


def downloadImage(url):
    global inx
    global lock
    try:
        if url not in pictures_downloaded:
            addToPictures(url)

            r = requests.get(url, stream = True)

            if r.status_code == 200:
                lock.acquire()
                filename = os.path.join(DOWNLOAD_PATH, str(inx) + '.' + url.split('.')[-1])
                inx += 1
                lock.release()
                r.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                pass
        if url in pictures_downloaded:
            pass
    except:
        print('Invalid URL or other issue.')


def addToPictures(url):
    lock2.acquire()
    with open('artwork_pictures/pictures.txt', 'a') as f:
        f.write(url + '\n')
    lock2.release()


if __name__ == '__main__':
    website_urls = importWebsites()
    pictures_downloaded = importDownloaded()
    # Multithreading implemented 02/10/2020
    pool = ThreadPool(40)
    results = pool.map(getImage, website_urls)
    print(results)

    
    
    
    # Old function not using syncrounous threading
    #for url in website_urls:
    #    getImage(url)

    #for image in picture_urls:
     #   a = downloadImage(image, inx)
      #  if a == True:
        #pictures_downloaded.append(image)
        