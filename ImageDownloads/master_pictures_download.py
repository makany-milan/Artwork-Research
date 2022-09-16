# Author: Milan Makany
# Organisation: Said Business School


from artsyFairs.fair_pictures_download import IMPORT_PATH
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import os
import shutil
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
import csv
from tqdm import tqdm


lock = Lock()


DATA_PATH = r'D:\SBS\Data\30-06-2021\images.csv'
DOWNLOAD_PATH = r'D:\SBS\Images-01-07-2021'


HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def importImageURLs():
    images = []
    idIndex = 0
    urlIndex = 0
    with open(DATA_PATH, 'r', encoding='utf-8') as fs:
        csvR = csv.reader(fs, delimiter=',', quotechar='\"')
        for inx, line in enumerate(csvR):
            if inx == 0:
                idIndex = line.index('imageID')
                urlIndex = line.index('image_url')
            else:
                try:
                    idNum = line[idIndex]
                    url = line[urlIndex]
                    images.append([idNum, url])
                except:
                    pass
    return images


def downloadImage(li):
    id, url = li
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            f = str(id) + '.' + url.split('.')[-1]
            filename = os.path.join(DOWNLOAD_PATH, f)
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            pass
        #if url in pictures_downloaded:
        #    pass
    except Exception as e:
        pass
    return id


if __name__ == '__main__':
    images = importImageURLs()
    with ThreadPool(40) as pool:
        with tqdm(total=len(images)) as pbar:
            for i, _ in enumerate(pool.imap_unordered(downloadImage, images)):
                pbar.update()