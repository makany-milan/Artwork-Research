from fairs.artsy_fair_extraction import Artwork, Artsy, Fair
from bs4 import BeautifulSoup as bs
import re
import csv

class ArtsyAuctions(Artsy):
    def __init__(self):
        super().__init__()

    def identify_auctions(self):
        auction_page = 'https://www.artsy.net/auctions'
        auction_tag = 'dsNAEX'
        page = self.make_request(auction_page)
        if page:
            soup = bs(page.text, 'html.parser')
            auctions = soup.find_all('div', {'class': auction_tag})
            auctions = [Auction(auction['href']) for auction in auctions]
            # extract auction data
            for auction in auctions:
                auction.fetch_data()

class Auction(Fair):
    def __init__(self, url, export_path):
        super().__init__(url, export_path)

    def setup_csv(self, exloc):
        '''''
            self.estimated_price = ''
            self.bid_price = ''
            self.ends = ''
            self.bids = ''
        '''''
        with open(exloc, 'w', encoding='UTF-8', newline='') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['artist', 'artist_slug', 'title', 'year', 'gallery', 'estimated_price', 'bid_price', 'ends', 'bids' 'category', 'materials', 'dimensions', 'sold', 'url', 'image_url'])




class AuctionArt(Artwork):
    def __init__(self, content):
        super().__init__(content)

    def extract_artwork_data(self, json_data, soup):
        # THE PRICE IS NOT IN THE JSON
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
            price_block = soup.find('div', {'data-test': 'artworkSidebar'})
            # loop over elements to find estimated price and bid price
            self.estimated_price = ''
            self.bid_price = ''
            self.ends = ''
            self.bids = ''
            for element in price_block.children:
                if 'Estimated value' in element.text:
                    self.estimated_price = re.match('[0-9,]+').group(0)
                elif 'Starting bid' in element.text:
                    self.bid_price = re.match('[0-9,]+').group(0)
                elif 'Ends' in element.text:
                    self.ends = element.text
                elif re.match('[0-9]+ bid', element.text):
                    self.bids = re.match('[0-9]+', element.text).group(0)
        except:
            self.estimated_price = ''
            self.bid_price = ''
            self.ends = ''
            self.bids = ''

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
            self.url = json_data['url']
        except:
            self.url = ''
        
        try:
            self.image_url = json_data['image']
        except:
            self.image_url = ''

    def export_to_csv(self):
        '''''
            self.estimated_price = ''
            self.bid_price = ''
            self.ends = ''
            self.bids = ''
        '''''
        return [self.artist, self.artist_slug, self.title, self.year, self.gallery, self.estimated_price, self.bid_price, self.ends,  self.bids, self.category, self.materials, self.dimensions, self.sold, self.url, self.image_url]
