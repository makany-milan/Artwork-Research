import requests
import json
import os
from time import sleep
from tqdm import tqdm


GALLERYLOC = r'D:\Said Business School\ArtsyAPI\Galleries'
ARTISTLOC = r'D:\Said Business School\ArtsyAPI\Artists'
PROFILELOC = r'D:\Said Business School\ArtsyAPI\GalleryProfiles'
AGGREGATEARTWORKLOC = r'D:\Said Business School\ArtsyAPI\Artworks\Aggregate'
INDIVIDUALARTWORKLOC = r'D:\Said Business School\ArtsyAPI\Artworks\Individual'


def getAPIKey():
    r = requests.post('https://api.artsy.net/api/tokens/xapp_token?client_id=1ace2cce7af3eb34f68a&client_secret=c488bd75b5b128da06ac04f4bf36467d')
    content = r.text
    jsonData = json.loads(content)
    tokenCode = jsonData['token']
    return tokenCode


def exportGalleryJSON(jsonData):
    galleryName = jsonData['slug']
    fileName = galleryName + '.json'
    fileLocation = os.path.join(GALLERYLOC, fileName)

    with open(fileLocation, 'w', encoding='utf-8') as w:
        json.dump(jsonData, w)


def extractGalleryJSONData(data):
    jsonData = json.loads(data)
    try:
        nextLink = jsonData['_links']['next']['href']
    except:
        nextLink = ''
    galleryData = jsonData['_embedded']['partners']

    for gallery in galleryData:
        exportGalleryJSON(gallery)

    return nextLink


def exportJSON(jsonData, filename, location):
    fileLocation = os.path.join(location, filename)

    with open(fileLocation, 'w', encoding='utf-8') as w:
        json.dump(jsonData, w)


def fetchGalleryAPIData(url):
    global requestHeaders
    try:
        r = requests.get(url, headers=requestHeaders)
    except:
        print(f'\nError accesing API. url: {url}')
    
    if r.status_code == 200:
        nextLink = extractGalleryJSONData(r.text)
    elif r.status_code == 429:
        sleep(1)
        nextLink = fetchGalleryAPIData(url)
    
    return nextLink


def galleryJSONImport(jsonData):
    try:
        name = jsonData['name']
    except:
        name = ''
    try:
        uid = jsonData['id']
    except:
        uid = ''
    try:
        slug = jsonData['slug']
    except:
        slug = ''
    try:
        gType = jsonData['type']
    except:
        gType = ''
    try:
        email = jsonData['email']
    except:
        email = ''
    try:
        region = jsonData['region']
    except:
        region = ''
    try:
        website = jsonData['_links']['website']['href']
    except:
        website = ''
    try:
        artsyWebsite = jsonData['_links']['permalink']['href']
    except:
        artsyWebsite = ''

    gallery = Gallery(name, uid, slug, gType, email, region, website, artsyWebsite)

    return gallery


def getAllGalleries():
    url = 'https://api.artsy.net/api/partners'
    endOfAPI = False

    while not endOfAPI:
        url = fetchGalleryAPIData(url=url)
        sleep(0.2)
        if url == '':
            endOfAPI = True


class Gallery:
    global requestHeaders

    def __init__(self, name, uid, slug, gType, email, region, website, artsyPage, *args, **kwargs):
        self.name = name
        self.uid = uid
        self.slug = slug
        self.gType = gType
        self.email = email
        self.region = region
        self.website = website
        self.artsyPage = artsyPage

        self.s = requests.Session()
        self.headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en-US,en;q=0.9,',
            'authorization': '',
            'cache-control': 'no-cahce',
            'referer': 'https://artsy.net/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'X-Xapp-Token': 'eyJhbGciOiJIUzI1NiJ9.eyJyb2xlcyI6ImFydHN5Iiwic3ViamVjdF9hcHBsaWNhdGlvbiI6IjVkNDA5OTZlNmU2MDQ5MDAwNzQ5MGZhMiIsImV4cCI6MTYxNzg3MjM2MiwiaWF0IjoxNjE3MjY3NTYyLCJhdWQiOiI1ZDQwOTk2ZTZlNjA0OTAwMDc0OTBmYTIiLCJpc3MiOiJHcmF2aXR5IiwianRpIjoiNjA2NThiNmE4ZjA0MjkwMDBlMTE3NjVjIn0.9AH9pDHLYDvisxYL4K3F9Elz6uulYU3NRpMjKhJZgLw'
        }

        #Exception has occurred: ConnectionError
        # HTTPSConnectionPool(host='www.artsy.net', port=443): Max retries exceeded with url: /ibasho (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x0000021BF30588B0>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))

        self.profile = self.getProfileData()
        self.artists = self.getArtistData()
        self.aggregateArtworks = self.getAggregateArtworkData()
        self.individualArtworks = self.getIndividualArtworkData()
    

    def getProfileData(self):
        url = 'https://api.artsy.net/api/v1/partner/' + self.slug
        fileName = self.slug + '-profile.json'
        fileloc = PROFILELOC

        exists = os.path.exists(os.path.join(fileloc, fileName))

        if not exists:
            req = requests.Request('GET', url, headers=self.headers)
            req.headers['origin'] = 'https://www.artsy.net'
            prep = self.s.prepare_request(req)
            try:
                r = self.s.send(prep)
            except Exception as e:
                print(e)
                return e

            if r.status_code == 200:
                exportJSON(r.text, fileName, fileloc)
                return 'OK'
            else:
                return f'{r.status_code}'


    def getArtistData(self):
        url = f'https://api.artsy.net/api/v1/partner/{self.slug}/partner_artists?display_on_partner_profile=1&size=100'
        fileName = self.slug + '-artist.json'
        fileloc = ARTISTLOC

        exists = os.path.exists(os.path.join(fileloc, fileName))

        if not exists:
            req = requests.Request('GET', url, headers=self.headers)
            req.headers['origin'] = 'https://www.artsy.net'
            prep = self.s.prepare_request(req)
            try:
                r = self.s.send(prep)
            except Exception as e:
                print(e)
                return e

            if r.status_code == 200:
                exportJSON(r.text, fileName, fileloc)
                return 'OK'
            else:
                return f'{r.status_code}'


    def getAggregateArtworkData(self):
        url = f'https://api.artsy.net/api/v1/filter/artworks?size=0&aggregations[]=dimension_range&aggregations[]=medium&aggregations[]=price_range&aggregations[]=total&aggregations[]=for_sale&partner_id={self.slug}'
        fileName = self.slug + '-aggregateArtwork.json'
        fileloc = AGGREGATEARTWORKLOC

        exists = os.path.exists(os.path.join(fileloc, fileName))

        if not exists:
            req = requests.Request('GET', url, headers=self.headers)
            req.headers['origin'] = 'https://www.artsy.net'
            prep = self.s.prepare_request(req)
            try:
                r = self.s.send(prep)
            except Exception as e:
                print(e)
                return e

            if r.status_code == 200:
                exportJSON(r.text, fileName, fileloc)
                return 'OK'
            else:
                return f'{r.status_code}'


    def getIndividualArtworkData(self):
        url = f'https://api.artsy.net/api/v1/filter/artworks?size=10000&partner_id={self.slug}'
        fileName = self.slug + '-aggregateArtwork.json'
        fileloc = INDIVIDUALARTWORKLOC

        exists = os.path.exists(os.path.join(fileloc, fileName))

        if not exists:
            req = requests.Request('GET', url, headers=self.headers)
            req.headers['origin'] = 'https://www.artsy.net'
            prep = self.s.prepare_request(req)
            try:
                r = self.s.send(prep)
            except Exception as e:
                print(e)
                return e

            if r.status_code == 200:
                exportJSON(r.text, fileName, fileloc)
                return 'OK'
            else:
                return f'{r.status_code}'


def getGalleryData():
    galleries = []
    files = os.listdir(GALLERYLOC)
    pbar = tqdm(desc='Fetching JSON Data', total=len(files))
    for file in files:
        with open(os.path.join(GALLERYLOC, file), 'r', encoding='utf-8') as r:
            jsonData = json.load(r)
        gallery = galleryJSONImport(jsonData)
        # galleries.append(gallery)
        pbar.update(1)
    pbar.close()

    return galleries


if __name__ == '__main__':
    apiKey = getAPIKey()
    requestHeaders = {  
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'X-Xapp-Token': apiKey
    }

    galleries = getGalleryData()
    