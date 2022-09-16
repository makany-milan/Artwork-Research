import requests
from bs4 import BeautifulSoup as bs

from multiprocessing.pool import ThreadPool

# If there is a txt file containing the artist URLS set to True.
URL_COLLECTED = True
URL_LOC = r'C:\Users\Milan\OneDrive\Desktop\SBS\Artworks\Blouin_Scraper\data\artist_urls.txt'
URL = r'https://www.blouinartsalesindex.com/browse-artists?lastName='
EXPORTLOC = r'C:\Users\Milan\OneDrive\Desktop\SBS\Artworks\Blouin_Scraper\data\export.csv'


def genURLS():
    urls = []
    from string import ascii_uppercase
    for letter in ascii_uppercase:
        urls.append(URL + letter)

    return urls


def addPageNumber(url: str, number: int):
    url_return = url + '&startRowNum=' + str(number)
    return url_return


# The url of the artist's page can be identified using this class name.
ARTIST_CLASS = 'text-left'


def getArtistPages(url: str):
    urls = []
    counter = 0
    while True:
        startNum = counter * 150
        counter += 1
        currentURL = addPageNumber(url, startNum)
        r = requests.get(currentURL)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            artists = soup.find_all('li', {'class': ARTIST_CLASS})
            newArtists = len(artists)
            print(url[-1] + str(startNum))
            if newArtists == 0:
                break

            for artist in artists:
                artisturl = 'https://www.blouinartsalesindex.com' + artist.next['href']
                urls.append(artisturl)
        else:
            break

    return urls


def exportURLS(urls: list):
    with open(URL_LOC, 'w', encoding='utf-8') as writer:
        for batch in urls:
            for item in batch:
                try:
                    writer.write(item + '\n')
                except Exception as e:
                    print(e)


def importURLS():
    urls = []
    with open(URL_LOC, 'r') as r:
        for row in r:
            urls.append(row.strip())
        
    return urls


def countPronouns(text):
    m = 0
    f = 0
    male_pronouns = ['he', 'his', 'him', 'himself']
    female_pronouns = ['she', 'her', 'hers', 'herself']

    words = text.split(' ')
    for w in words:
        wClean = w.replace(',', '').replace('.', '').lower()
        if wClean in male_pronouns:
            m += 1
        if wClean in female_pronouns:
            f += 1

    return f, m


def determineConfidence(f: int, m: int):
    t = f + m
    # if the prediction is male p<0, if the prediction is female p>0
    # if the f=m, p=0 as the model cannot make any prediction on the gender
    if f > m:
        sign = 1
        p = sign * f / t
    elif f < m:
        sign = -1
        p = sign * m / t
    elif f == m:
        p = 0

    return p


def clearString(s: str):
    import re
    ret = re.sub('\n|\r|\t', '', s)
    ret = ret.replace('(', '').replace(')', '')
    return ret


ARTIST_NAME_CLASS = 'mt-10'
# The search will return multiple results for the YEAR_NATIONALITY class.
# Check if it is empty. Get data from the one that isn'.
YEAR_NATIONALITY_CLASS = 'clearfix'
ARTIST_BIO_CLASS = 'overview-bio'


def getArtistData(url: str):
    global pbar
    pbar.update(1)
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'From': 'david.zhuang@outlook.com'
        }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')

            try:
                name = soup.find('h2', {'class': ARTIST_NAME_CLASS}).text.strip()
            except:
                return []

            try:
                container1 = soup.find('p', {'class': YEAR_NATIONALITY_CLASS}).text
                container = clearString(container1)
                try:
                    parts = container.split(',b. ')
                    nationality = parts[0]
                    years = parts[1]
                    try:
                        birthYear = years.split(' - ')[0]
                        deathYear = years.split(' - ')[1]
                    except:
                        birthYear = years
                        deathYear = ''

                except:
                    nationality = container
                    birthYear = ''
                    deathYear = ''

            except Exception as e:
                nationality = ''
                birthYear = ''
                deathYear = ''

            try:
                bio = soup.find('div', {'class': ARTIST_BIO_CLASS}).text
            except:
                bio = ''

            if bio != '':
                f, m = countPronouns(bio)
                p = determineConfidence(f, m)
                if p > 0:
                    prediction = 'Female'
                elif p < 0:
                    prediction = 'Male'
                elif p == 0:
                    prediction = ''
            else:
                m = ''
                f = ''
                p = ''
                prediction = ''

            retValue = [name, nationality, birthYear, deathYear, prediction, m, f, p, url]
            return retValue

        else:
            return []
    except:
        return []


def exportResults(export: list):
    from csv import writer as csvwriter
    with open(EXPORTLOC, 'a', encoding='utf-8', newline='') as f:
        w = csvwriter(f, delimiter=';')
        for row in export:
            if row != []:
                try:
                    # name, nationality, birthYear, deathYear, prediction, m, f, p, url
                    w.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]])
                except:
                    print('Error exporting row')


def setupCSV():
    from csv import writer as csvwriter
    with open(EXPORTLOC, 'w', encoding='utf-8', newline='') as f:
        w = csvwriter(f, delimiter=';')
        w.writerow(['Name', 'Nationality', 'YoBirth', 'YoDeath', 'BlouinGenderPrediction', 'MalePronouns', 'FemalePronouns', 'PredictionAccuracy', 'URL'])


if __name__ == "__main__":
    if URL_COLLECTED is False:
        urls = genURLS()
        threadNum = len(urls)
        pool = ThreadPool(threadNum)
        artistUrls1 = pool.map(getArtistPages, urls)
        pool.close()
        exportURLS(artistUrls1)

        artistUrls = []
        for batch in artistUrls1:
            for item in batch:
                artistUrls.append(item)
    else:
        artistUrls = importURLS()

    from tqdm import tqdm
    with tqdm(total=len(artistUrls)) as pbar:
        pool = ThreadPool(50)
        results = pool.map(getArtistData, artistUrls)
        pool.close()

    setupCSV()
    exportResults(results)
