from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from tqdm import tqdm
import asyncio
import pandas as pd


ARTIST_DATA = []
EXPORTLOC = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\artFacts\data\\'


def getOuterLinks():
    outerLinks = []
    url = 'https://artfacts.net/lists/artists_a-z/'
    from string import ascii_lowercase
    for letter in ascii_lowercase:
        link = url + letter
        outerLinks.append(link)

    return outerLinks


def getInnerLinks(outerLinks):
    driver = Chrome(r'C:\Users\Milan\Downloads\chromedriver.exe')
    innerLinks = []
    for link in outerLinks:
        driver.get(link)
        sleep(2)
        for x in range(100):
            try:
                obj = driver.find_element_by_xpath(f'/html/body/div[2]/div/div/div[3]/ul/li[{x+1}]/a')
            except NoSuchElementException:
                break
            except Exception as e:
                print(e)
            link = obj.get_attribute('href')
            if link not in innerLinks:
                innerLinks.append(link)

    driver.close()
    return innerLinks


def getArtistLinks(innerLinks):
    global pbar
    artists = []
    driver = Chrome(r'C:\Users\Milan\Downloads\chromedriver.exe')
    for inner in innerLinks:
        driver.get(inner)
        sleep(2)
        for x in range(600):
            try:
                obj = driver.find_element_by_xpath(f'/html/body/div[2]/div/div/div[4]/ul/li[{x+1}]/a')
            except NoSuchElementException:
                break
            except Exception as e:
                print(e)

            link = obj.get_attribute('href')
            if link not in artists:
                artists.append(link)
        pbar.update(1)
    driver.close()
    return artists


def exportInnerLinks(innerLinks):
    with open(EXPORTLOC + 'categoryLinks.txt', 'w') as w:
        for l in innerLinks:
            w.write(l + '\n')


def importInnerLinks():
    innerLinks = []
    with open(EXPORTLOC + 'categoryLinks.txt', 'r') as r:
        for l in r:
            link = l.strip()
            innerLinks.append(link)
    return innerLinks


def exportArtistLinks(links):
    with open(EXPORTLOC + 'artistLinks.txt', 'w') as w:
        for l in links:
            w.write(l + '\n')


def importArtistLinks():
    links = []
    with open(EXPORTLOC + 'artistLinks.txt', 'r') as r:
        for line in r:
            links.append(line.strip())
    return links


headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'From': 'david.zhuang@outlook.com'
    }


def getHTML(artistURL, session):
    r = session.get(artistURL, headers=headers, timeout=120)
    r.html.render(wait=1, timeout=120)
    return r


def tableExtract(table):
    soup = BeautifulSoup(table, features='lxml')
    results = {}
    for row in soup.findAll('tr'):
        aux = row.findAll('td')
        key = aux[0]
        vals = aux[1]
        numberOfValues = len(vals.contents)
        if numberOfValues == 1:
            results[key.text] = vals.text
        else:
            values = []
            for item in vals.contents:
                try:
                    values.append(item.text)
                except AttributeError:
                    item = str(item). strip(' | ')
                    results['Birth Place'] = item

            results[aux[0].text] = ', '.join(values)

    return results


def getArtistData(artistURL, session):
    global pbar
    artistData = {}
    try:
        r = getHTML(artistURL, session)
    except:
        return {}

    try:
        nameObj = r.html.find('.app-js-components-PageTitle-PageTitle__pageTitle')[0].html
        artistName = BeautifulSoup(nameObj, features='lxml').find('h1').text
        artistData['Name'] = artistName
    except:
        return {}
    try:
        dataTable = r.html.find('.app-js-components-Spotlight-Spotlight__info')[0]
    except IndexError:
        dataTable = ''
    if dataTable != '':
        tableData = tableExtract(dataTable.html)
    artistData = {**artistData, **tableData}
    artistData['URL'] = artistURL

    pbar.update(1)

    return artistData


if __name__ == '__main__':
    categorySaved = True
    if not categorySaved:
        outerLinks = getOuterLinks()
        innerLinks = getInnerLinks(outerLinks)
        exportInnerLinks(innerLinks)
    else:
        innerLinks = importInnerLinks()
    artistsSaved = True
    if not artistsSaved:
        pbar = tqdm('Fetching Artist Data' ,total=len(innerLinks))
        artistLinks = getArtistLinks(innerLinks)
        pbar.close()
        exportArtistLinks(artistLinks)
    if artistsSaved:
        artistLinks = importArtistLinks()[:50] 

    pbar = tqdm(desc='Extracting Artist Data', total=len(artistLinks))
    data = []
    session = HTMLSession()
    for link in artistLinks:
        data.append(getArtistData(link, session))
    pbar.close()
    session.close()

    df = pd.DataFrame(data)
    df.to_csv(r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\artFacts\data\genderData.csv',
              sep=';', index_label='id', quotechar='|')
