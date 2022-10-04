import requests
from bs4 import BeautifulSoup as bs
from multiprocessing.pool import ThreadPool
import json
import csv
import sys
from tqdm import tqdm
from datetime import date
from time import sleep
from pathlib import Path
import re
from random import random


CD = Path().cwd()
TODAY = date.today().strftime('%d-%m-%Y')


class Artsy:
    def __init__(self):
        self.main_page = 'https://www.artsy.net/art-fairs'
        self.timeout = 120
        self.headers = {
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            }
        self.export_path = Path(r'C:\Users\u2048873\Oxford_Data')
        self.identify_fairs()


    def identify_fairs(self):
        current_fair_tags = ['div', 'class', 'HKmvV']
        part_fair_tags = ['div', 'class', 'bhRLJp']

        contents = self.make_request(self.main_page)
        soup = bs(contents, 'html.parser')
        current_fairs = soup.find_all(current_fair_tags[0], {current_fair_tags[1]: current_fair_tags[2]})
        self.current_fairs = []
        for fair in current_fairs:
            try:
                link = fair.find('a')
                link = 'https://www.artsy.net' + link['href']
                if 'fair' in link:
                    self.current_fairs.append(link)
            except:
                pass

        past_fairs = soup.find_all(part_fair_tags[0], {part_fair_tags[1]: part_fair_tags[2]})
        self.past_fairs = []
        for fair in past_fairs:
            link = 'https://www.artsy.net' + fair['href']
            if 'fair' in link:
                self.past_fairs.append(link)
        

    def make_request(self, url):
        sleep(5)
        r = requests.get(url, timeout=120, headers=self.headers)
        if r.status_code == 200:
            return r.content
        else:
            print(r.status_code)
            return None


    def extract_current_fairs(self):
        for current_fair in self.current_fairs:
            fair = Fair(current_fair, self.export_path)
            print(f'{current_fair} - Extracting')
            fair.fetch_data()


    def extract_past_fairs(self):
        for past_fair in self.past_fairs:
            fair = Fair(past_fair, self.export_path)
            print(f'{past_fair} - Extracting')
            fair.fetch_data()
    

    def extract_txt_fairs(self):
        self.import_fairs_from_txt()
        for txt_fair in self.txt_fairs:
            fair = Fair(txt_fair, self.export_path)
            print(f'{txt_fair} - Extracting')
            fair.fetch_data()


    def import_fairs_from_txt(self):
        self.txt_fairs = []
        file_loc = (CD / 'fairs.txt').resolve()
        with open(file_loc, 'r', encoding='utf-8') as fs:
            for line in fs:
                line = line.strip()
                fair_url = f'https://www.artsy.net{line}'
                self.txt_fairs.append(fair_url)


class Fair:
    def __init__(self, url, export_path):
        self.url = url
        self.export_file = url.split('/')[-1] + '.csv'
        self.search_url = url + '/artworks?page='

        self.timeout = 120
        self.headers = {
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            }

        self.export_path = Path(export_path, self.export_file)
        self.setup_csv(self.export_path)


        self.long_fair = self.check_long_fair()
        if self.long_fair:
            self.long_fair_tags = self.generate_long_fair_tags()
        

    def fetch_data(self):
        artworks = []
        print(f'{self.url} - Collecting links')
        links = self.fetch_links()
        print(f'{self.url} - Extracting Data')
        for link in links:
            content = self.make_request(link)
            if content:
                artwork = Artwork(content)
                artworks.append(artwork)
                self.export_data(self.export_path, artwork=artwork.export_to_csv())


    def fetch_links(self):
        search_tags = ['div', 'data-test', 'artworkGridItem']#
        links = []
        if self.long_fair:
            for tag in self.long_fair_tags:
                for x in range(100):
                    x = x+1
                    link = self.search_url + str(x) + tag
                    content = self.make_request(link)
                    if content:
                        soup = bs(content, 'html.parser')
                        page_links = soup.find_all(search_tags[0], {search_tags[1]: search_tags[2]})
                        if page_links:
                            for page_link in page_links:
                                link = 'https://www.artsy.net' + page_link.find('a')['href']
                                links.append(link)
                        else:
                            break
        else:
            # CHANGE BACK TO 100
            for x in range(100):
                x = x+1
                link = self.search_url + str(x)
                content = self.make_request(link)
                if content:
                    soup = bs(content, 'html.parser')
                    page_links = soup.find_all(search_tags[0], {search_tags[1]: search_tags[2]})
                    if page_links:
                        for page_link in page_links:
                            link = 'https://www.artsy.net' + page_link.find('a')['href']
                            links.append(link)
                    else:
                        break
        return set(links)


    def make_request(self, url):
        # Make sure the server does not block requests
        sleeptime = random() * 3
        sleep(sleeptime)
        r = requests.get(url, timeout=120, headers=self.headers)
        if r.status_code == 200:
            return r.content
        else:
            print(r.status_code)
            sleep(200)
            return None


    def export_data(self, exloc, artwork=None):
        if artwork:
            with open(exloc, 'a', encoding='UTF-8', newline='') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(artwork)
        else:
            with open(exloc, 'a', encoding='UTF-8', newline='') as f:
                w = csv.writer(f, delimiter=';')
                for artwork in self.artworks:
                    try:
                        if artwork.data:
                            w.writerow(artwork.export_to_csv())
                    except:
                        pass


    def setup_csv(self, exloc):
        with open(exloc, 'w', encoding='UTF-8', newline='') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['artist', 'artist_slug', 'title', 'year', 'gallery', 'price', 'currency', 'category', 'materials', 'dimensions', 'sold', 'url', 'image_url'])


    def check_long_fair(self):
        r = requests.get(self.search_url, timeout=self.timeout, headers=self.headers)
        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
        else:
            print('Error loading fair')
            sys.exit()

        numberOfArtworks = soup.find('div', {'class': 'iAatLR'}).text
        numberOfArtworks = re.search('(\d+)', numberOfArtworks)

        try:
            numberOfArtworks = int(numberOfArtworks.group())
        except Exception as e:
            print(e)
            return False

        if numberOfArtworks > 3000:
            return True
        if numberOfArtworks <= 3000:
            return False


    def generate_long_fair_tags(self):
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
            'price_range=1000-5000',
            'price_range=5000-10000',
            'price_range=10000-25000',
            'price_range=25000-100000',
            'price_range=2A-1000'
        ]

        tags = []
        for art in arttype:
            for p in price:
                tags.append(f'&additional_gene_ids%5B0%5D=' + art + '&' + p)
   
        return tags


class Artwork:
    def __init__(self, content):
        soup = bs(content, 'html.parser')
        self.extract_data(soup)


    def extract_data(self, soup):
        json_block = self.find_json_block(soup)
        self.extract_artwork_data(json_block, soup)

    
    def find_json_block(self, soup):
        block = soup.find('script', {'type': 'application/ld+json'})
        try:
            json_data = json.loads(block.text)
            return json_data
        except:
            return None
        

    def extract_artwork_data(self, json_data, soup):
        try:
            element = json_data['brand']['name']
            self.artist = element.strip().replace('\"', '')
        except:
            self.artist = ''
        
        try:
            block = soup.find('div', {'data-test': 'artworkSidebar'})
            element = block.find('a', {'class': 'cCmCIs'})
            self.artist_slug = element['href']
        except:
            self.artist_slug = ''
        
        try:
            element = soup.find('h1', {'class': 'fiPLKL'}).text
            if ', ' in element:
                self.title = ', '.join(element.split(', ')[:-1])
            else:
                self.title = element
        except:
            self.title = ''

        try:
            self.year = json_data['productionDate']
        except:
            self.year = ''
        
        try:
            block = soup.find('div', {'class': 'ArtworkSidebarPartnerInfo__PartnerContainer-sc-16oykvq-0'})
            element = block.find('a')
            self.gallery = element['href']
        except:
            self.gallery = ''
        
        try:
            price_block = json_data['offers']
        except:
            price_block = None

        try:
            if price_block:
                self.price = price_block['price']
            else:
                self.price = ''
        except:
            try:
                if price_block:
                    lowprice = price_block['lowPrice']
                    highprice = price_block['highPrice']
                    self.price = f'{str(lowprice)}-{str(highprice)}'
                else:
                    self.price = ''
            except:
                self.price = ''

        try:
            if price_block:
                self.currency = price_block['priceCurrency']
            else:
                self.currency = ''
        except:
            self.currency = ''

        try:
            details_block = soup.find('div', {'data-test', 'artworkDetails'})
        except:
            details_block = None


        try:
            element = json_data['category']
            self.category = element
            
        except:
            self.category = ''


        try:
            artwork_block = soup.find('div', {'data-test': 'artworkSidebar'})
        except:
            artwork_block = None


        try:
            if artwork_block:
                element = artwork_block.find('div', {'class': 'ldlHGe'})
                self.materials = element.text
            else:
                self.materials = ''

        except:
            self.materials = ''

        try:
            width = json_data['width'].replace(' in', '')
            height = json_data['height'].replace(' in', '')
            try:
                depth = json_data['depth'].replace(' in', '')
                self.dimensions = f'{width} x {height} x {depth} in'
            except:
                self.dimensions = f'{width} x {height} in'
        except:
            self.dimensions = ''
        

        try:
            if self.price:
                self.sold = 'False'
            else:
                self.sold = 'True'
        except:
            self.sold = ''
        
        try:
            self.url = json_data['url']
        except:
            self.url = ''
        
        try:
            self.image_url = json_data['image']
        except:
            self.image_url = ''

    
    def export_to_csv(self):
        return [self.artist, self.artist_slug, self.title, self.year, self.gallery, self.price, self.currency, self.category, self.materials, self.dimensions, self.sold, self.url, self.image_url]





if __name__ == '__main__':
    main = Artsy()
    #main.extract_current_fairs()
    #main.extract_past_fairs()
    main.extract_txt_fairs()
