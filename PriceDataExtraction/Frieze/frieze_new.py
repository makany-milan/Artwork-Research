from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv
from pathlib import Path
from datetime import date


TODAY = date.today().strftime('%d-%m-%Y')


options = ChromeOptions()
# maximises the window on launch
options.add_argument("--start-maximized")



class Engine:
    def __init__(self):
        self.driver = Chrome(executable_path=r"C:\Users\u2048873\Downloads\chromedriver.exe", options=options)
        self.actions =  ActionChains(self.driver)

    def scrollToBottom(self):
        # get scroll height
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        bottom = False
        while not bottom:
            try:
                sleep(3)
                # scroll down to bottom
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                html = self.driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                # wait for page to load
                sleep(3)
                # calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script('return document.body.scrollHeight')
                if new_height == last_height:
                    bottom = True
                last_height = new_height
            except:
                pass

    def scrollToItem(self, item):
        try:
            self.actions.move_to_element(item).perform()
        except:
            try:
                scrollLoc = item.location['y']
                self.driver.execute_script(f'window.scrollTo(0, {scrollLoc})')
            except:
                pass

    def get(self, url):
        self.driver.get(url)
        sleep(3)
    

class Fair:
    def __init__(self, engine, fair_page, fair_name) -> None:
        self.main_page = 'https://www.frieze.com/fairs'
        self.fair_page = fair_page
        self.fair_name = fair_name
        self.engine = engine
        self.username = 'dawei.zhuang@outlook.com'
        self.password = 'ArtProject+44'

        self.exportLoc = Path(rf'C:\Users\u2048873\Oxford_Data\frieze\frieze-{fair_name}-{TODAY}.csv')
        self.createExport()

        self.galleries = []

        try:
            self.login()
        except:
            pass
        self.findGalleries()

        self.exportData()


    def login(self):
        self.engine.get(self.main_page)
        sleep(2)
        sleep(2)
        sleep(3)
        self.engine.driver.find_element_by_id('pelcro-input-email').send_keys(self.username)
        self.engine.driver.find_element_by_id('pelcro-input-password').send_keys(self.password)
        self.engine.driver.find_element_by_id('login-submit').click()
        sleep(3)


    def findGalleries(self):
        self.engine.get(self.fair_page)
        self.engine.scrollToBottom()
        html = self.engine.driver.page_source
        soup = bs(html, 'html.parser')
        results = soup.find_all('a', {'class': 'cqulfal'})
        links = []
        for result in results:
            link = result['href']
            link_complete = f'https://viewingroom.frieze.com{link}'
            links.append(link_complete)
        for link in links:
            gallery = Gallery(link, self.engine)
            gallery.getArtworks()
            gallery.collectArtworkData()

            self.galleries.append(gallery)


    def createExport(self):
        with open(self.exportLoc, 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='|')
            writer.writerow(['artist', 'title', 'year', 'price', 'materials', 'dimensions', 'image_url', 'url', 'gallery',])


    def exportData(self):
        with open(self.exportLoc, 'a', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='|')
            for gallery in self.galleries:
                for line in gallery.artworks:
                    line = [element.replace('"', '').replace(';', ',') for element in line]
                    writer.writerow(line)
    

class Gallery:
    def __init__(self, link, engine) -> None:
        self.main_page = link
        self.engine = engine
        self.artworks = []

    def getArtworks(self):
        self.engine.get(self.main_page)
        self.engine.scrollToBottom()
        html = self.engine.driver.page_source
        soup = bs(html, 'html.parser')
        self.gallery_name = soup.find('h1', {'class': 'tlid1pl'}).text

        results = soup.find_all('a', {'class': 'cqulfal'})
        self.artwork_links = []
        for result in results:
            link = result['href']
            link_complete = f'https://viewingroom.frieze.com{link}'
            self.artwork_links.append(link_complete)
            

    def collectArtworkData(self):
        for link in self.artwork_links:
            self.engine.get(link)
            html = self.engine.driver.page_source
            soup = bs(html, 'html.parser')
            data = self.extractData(soup)
            data.extend([self.gallery_name, link])
            self.artworks.append(data)


    def extractData(self, soup):
        try:
            artist = soup.find('h3', {'class': 'artist'}).text
        except:
            artist = ''
        try:
            title = soup.find('span', {'class': 'name'}).text
            title_year = soup.find('span', {'class': 'name-year'}).text
            year = title_year.replace(title, '').replace(', ', '')
        except:
            title = ''
            year = ''

        materials = ''
        dimensions =''
        price = ''
        try:
            blocks_container = soup.find('div', {'class': 'a10pwqbs'})
            blocks = blocks_container.find_all('p', {'class': 'tn8btz'})
            for inx, block in enumerate(blocks):
                if inx == 0:
                    materials = block.text
                elif inx == 1:
                    dimensions = block.text
                else:
                    if block.text != '':
                        price = block.text
                        break
        except:
            price = ''
            materials = ''
            dimensions = ''

        try:
            image = soup.find('img', {'class': 'sgwuv5o'})
            image = image['src']
        except:
            image = ''
        
        return [artist, title, year, price, materials, dimensions, image]


if __name__ == '__main__':
    engine = Engine()
    fairs = {
        'masters': 'https://viewingroom.frieze.com/search/viewingRooms?limit=20&skip=0&sections%5B0%5D=38&sections%5B1%5D=40&name=',
        'london': 'https://viewingroom.frieze.com/search/viewingRooms?sections%5B0%5D=39&sections%5B1%5D=43&sections%5B2%5D=42&sections%5B3%5D=37&sections%5B4%5D=41&name=&skip=20&neighborSkip=0'
    }
    for key in fairs:
        fair = fairs[key]
        f = Fair(engine, fair, key)

    engine.driver.close()