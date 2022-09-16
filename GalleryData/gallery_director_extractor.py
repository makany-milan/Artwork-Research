import requests
from bs4 import BeautifulSoup as bs
import csv
from tqdm import tqdm
from datetime import date
import re
from time import sleep

import logging
from threading import Thread
from queue import Queue

 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class Gallery:
    # Could implement threading when looking for CEO/Director names,
    # however the server might block too many concurrent requests.
    def __init__(self, csvdata, gallery_index, website_index) -> None:
        self.csvdata = csvdata
        self.gallery_name = self.csvdata[gallery_index]
        self.gallery_website = self.csvdata[website_index]
        self.request_headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en-US,en;q=0.9,',
            'authorization': '',
            'cache-control': 'no-cahce',
            'referer': 'https://google.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self.link_tags = ['about', 'contact', 'team', 'us', 'staff', 'trust',]
        self.links = []
        self.director_found = False

        self.regex_name = r'^[a-zA-Z \\,.\'-]+$'
        self.potential_directors = []
    

    def send_request(self, website, retries = 0) -> bool:
        if 'http' not in website:
            website = f'https://{website}'
        try:
            response = requests.get(website, headers=self.request_headers, allow_redirects=True)
            if response.status_code == 200:
                self.soup = bs(response.text, 'html.parser')
                return True
            else:
                return False
        except:
            if retries > 2:
                return False
            else:
                sleep(5)
                retries += 1
                response = self.send_request(website, retries)


    def append_csv_data(self, data, index = -1):
        # Inserts the element to a specified index in the csv data.
        # By default inserts the data to the end of the line.
        if index == -1:
            self.csvdata.append(data)
        else:
            self.csvdata.insert(index, data)


    def extract_links(self, soup: bs):
        interesting_links = []
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            if any(tag in link['href'] for tag in self.link_tags):
                if 'http' not in link['href']:
                    complete_link = self.gallery_website + link['href']
                else:
                    complete_link = link['href']
                if complete_link not in self.links:
                    if complete_link not in interesting_links:
                        interesting_links.append(complete_link)
        return interesting_links


    def find_name(self, text):
        names_found = re.findall(self.regex, text)
        names = []

        for name in names_found:
            if not any(word in name.lower() for word in ['director', 'ceo', 'deputy', 'executive']):
                name = name.lstrip().rstrip().replace(',', '')
                title = text.replace(name, '').replace(',', '').lstrip().rstrip()
                names.append([name, title])



    def find_director(self):
        if not self.director_found:
            name_title_matches = []

            p_elements = self.soup.find_all('p')
            b_elements = self.soup.find_all('b')
            strong_elements = self.soup.find_all('strong')
            span_elements = self.soup.find_all('span')

            all_elements = [p_elements, b_elements, strong_elements, span_elements]
            
            for category in all_elements:
                for element in category:
                    element_text = element.text
                    keyword_found = any(word in element_text.lower() for word in ['director', 'ceo', 'deputy', 'executive'])
                
                    if keyword_found:
                        names = self.find_name(element_text)
                        for name in names:
                            name_title_matches.append(name)
                    
                        try:
                            element_text = element.previous_sibling.text

                        except:
                            pass

            for match in name_title_matches:
                if match[1] == 'Director':
                    self.director = match[0]
                    self.director_title = 'Director'
                    self.director_found = True

            if not self.director_found:
                for match in name_title_matches:
                    self.potential_directors.append(match)

    
    def scrape(self):
        logger.info(f'Scraping data at {self.gallery_name}')
        status = self.send_request(self.gallery_website)
        if status:
            self.find_director()
            if not self.director_found:
                self.links = self.extract_links(self.soup)
                self.explore_links()
        self.finalise_results()
        

    def finalise_results(self):
        if self.director_found == False & len(self.potential_directors) == 0:
            pass
        elif self.director_found == False & len(self.potential_directors) == 1:
            self.director = self.potential_directors[1]
            self.director_title = self.potential_directors[0]
            self.director_found = True
        elif self.director_found == False & len(self.potential_directors) > 1:
            for potential in self.potential_directors:
                if 'director' in potential[1].lower():
                    self.director_found = True
                    self.director = potential[0]
                    self.director_title = potential[1]
        
            if self.director_found == False:
                for potential in self.potential_directors:
                    if 'ceo' in potential[1].lower():
                        self.director_found = True
                        self.director = potential[0]
                        self.director_title = potential[1]
            
            if self.director_found == False:
                for potential in self.potential_directors:
                    self.director =  f'{self.director};{potential[0]}'
                    self.director_title = f'{self.director_title};{potential[1]}'

        
        if self.director_found:
            self.append_csv_data('1')
            self.append_csv_data(self.director)
            self.append_csv_data(self.director_title)
        else:
            self.append_csv_data('0')
            self.append_csv_data('')
            self.append_csv_data('')

    
    def explore_links(self):
        for link in self.links:
            status = self.send_request(link)
            if status:
                self.find_director()
                if self.director_found:
                    break



class DataExtractor(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    

    def run(self):
        while True:
            func, gallery = self.queue.get()
            try:
                func(gallery)
            finally:
                self.queue.task_done()


def import_gallery_data() -> list:
    data_location = r'C:\Users\makan\OneDrive\Desktop\Said\Art\Gallery Data\data\gallery_contacts.csv'
    data = []
    with open(data_location, 'r', encoding='utf-8-sig') as f:
        csvr = csv.reader(f, delimiter=',', quotechar=r'"')
        for line in csvr:
            data.append(line)
    return data


def export_gallery_data(csvdata) -> None:
    today = date.today().strftime('%d-%m-%Y')
    data_export_location = rf'C:\Users\makan\OneDrive\Desktop\Said\Art\Gallery Data\data\gallery_contacts-{today}.csv'
    with open(data_export_location, 'w', encoding='utf-8', newline='') as f:
        csvw = csv.writer(f, delimiter=';', quotechar='"')
        for line in csvdata:
            csvw.writerow(line)


def extract_data(gallery: Gallery):
    gallery.scrape()
    

if __name__ == '__main__':
    raw_gallery_data = import_gallery_data()
    raw_gallery_data[0].append('Name Found')
    raw_gallery_data[0].append('Title')
    raw_gallery_data[0].append('Name')
    
    website_index = raw_gallery_data[0].index('Website')
    gallery_index = raw_gallery_data[0].index('Title')

    galleries = []

    #for data in raw_gallery_data[1:10]:
    for data in raw_gallery_data[20:30]:
        gallery = Gallery(data, gallery_index, website_index)
        galleries.append(gallery)

    q = Queue()
    for _ in range(1):
        worker = DataExtractor(q)
        worker.daemon = True
        worker.start()
    
    for gal in galleries:
        q.put((extract_data, gal))
    
    q.join()
    logging.info('Process Complete')

    export_data = [raw_gallery_data[0]]
    for gal in galleries:
        export_data.append(gal.csvdata)

    export_gallery_data(export_data)
