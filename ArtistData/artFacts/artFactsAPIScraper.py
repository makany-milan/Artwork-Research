import requests
import json
import csv
import brotli

from tqdm import tqdm
from time import perf_counter, sleep

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from os.path import join, exists

LOCK = Lock()

# API FORMAT
# https://artfacts.net/api/v0/artists/{ARTIST_ID}/spotlight
# LIST OF APIS: WEBPAGE > NETWORK>SPOTLIGHT>ARTWORKS


REQUEST_HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-US,en;q=0.9,',
    'authorization': '',
    'cache-control': 'no-cahce',
    'referer': 'https://artfacts.net/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
}


EXPORTFOLDER = r'D:\Said Business School\json\spotlight'


def importArtistLinks():
    links = []
    pbar = tqdm(desc='Importing Artist Links', total=615136)
    with open(r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\artFacts\data\artistLinks.txt', 'r') as r:
        for line in r:
            link = line.strip()
            links.append(link)
            pbar.update(1)
    pbar.close()
    return links


def getArtistData(artistLink):
    artistID = artistLink.split('/')[-1]
    fileName = artistID + '.json'
    url = f'https://artfacts.net/api/v0/artists/{artistID}/spotlight'

    if not exists(join(EXPORTFOLDER, fileName)):
        locked = LOCK.locked()
        if not locked:
            with requests.Session() as s:
                s.get('https://artfacts.net')
                cookies = s.cookies.get_dict()
                # xtoken = s.headers['']
                req = requests.Request('GET', url, headers=REQUEST_HEADERS)
                req.cookies = cookies
                prep = s.prepare_request(req)
                r = s.send(prep)
                # decompressed = brotli.decompress(r.content)

            if r.status_code == 200:
                with open(join(EXPORTFOLDER, fileName), 'w', encoding='utf-8') as w:
                    w.write(r.text)
            elif r.status_code == 429:
                print(f' {r.status_code}')
                LOCK.acquire()
                sleep(300)
                LOCK.release()
            elif str(r.status_code)[0] == '5':
                pass
            else:
                print(f' {r.status_code}')
                return None
        elif locked:
            while locked:
                sleep(5)
                locked = LOCK.locked()
            getArtistData(artistLink)
    else:
        return None

    # loaded = json.loads(response)
    # data = extractJSON(loaded)

    return artistID


if __name__ == '__main__':
    artistLinks = importArtistLinks()
    numberOfArtists = len(artistLinks)
    print(str(numberOfArtists) + ' artist IDs imported.')
    # export = []0
    # setupCSV()
    # print('CSV Setup Complete.')

    timerStart = perf_counter()
    pbar = tqdm(desc='Extracting Data', total=numberOfArtists)

    # CSVStream = open(EXPORTLOC, 'a', encoding='utf-8', newline='')
    # CSVWriter = csv.writer(CSVStream, delimiter=';')

    with ThreadPoolExecutor(max_workers=10, thread_name_prefix='aFS') as ex:
        # lock = Lock()

        futures = {ex.submit(getArtistData, aL): aL for aL in artistLinks}
        for future in as_completed(futures):
            artistID = futures[future]
            pbar.update(1)
            try:
                data = future.result()
                # lock.acquire()
                # CSVWriter.writerow(data)
                # lock.release()
            except Exception as e:
                print('%r generated an exception %s' % (artistID, e))

    # CSVStream.close()

    pbar.close()
    timerEnd = perf_counter()
    performance = timerEnd - timerStart
    print(f'Extracted {numberOfArtists} JSON files in {performance:0.4f} seconds')
