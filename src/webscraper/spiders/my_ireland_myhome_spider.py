import os
import re
import json

import scrapy

from pathlib import Path
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.webscraper.items import MyPropertyItem
from src.webscraper.normalization.data_normalization import Normalization


class IrelandMyhomeSpider(scrapy.Spider, Normalization):
    name = 'Ireland_Myhome'
    start_urls = [
        'https://www.myhome.ie/residential/ireland/property-for-sale',
    ]

    file_path = Path(__file__).parents[2].joinpath("extracted_data")
    file_name = 'myhome_test.json'
    save_file = Path(file_path).joinpath(file_name)

    custom_settings = {
        'FEEDS': {
            save_file: {'format': 'json'}
        },

        'CONCURRENT_REQUESTS': 2,
        # 'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
    }

    def parse(self, response, **kwargs):
        """Extracting all pagination pages urls"""
        pagination_extract = response.xpath('//app-desktop-pagination/div/a/@href').extract()

        pagination_page_numbers = []
        for element in pagination_extract:
            item = int(self.get_digits(element))
            pagination_page_numbers.append(item)
        pagination_max_page = max(pagination_page_numbers)
        pagination_pages_numbers = list(range(2, pagination_max_page))
        pagination_pages = []
        for element in pagination_pages_numbers:
            pagination_url = 'https://www.myhome.ie/residential/ireland/property-for-sale?page='
            page = pagination_url + str(element)
            pagination_pages.append(page)

        """Following pagination"""
        for next_page in pagination_pages:
            yield response.follow(next_page, callback=self.parse_search_page, priority=10)

    def parse_search_page(self, response):
        """Extracting advertising urls from search pagination page"""
        home_page = 'https://www.myhome.ie'
        property_urls = response.xpath('//div/div/app-mh-property-listing-card/div/div/a/@href').extract()
        for element in property_urls:
            next_page = home_page + element
            yield response.follow(next_page, callback=self.parse_property_content, priority=200)

    def parse_property_content(self, response):
        """Extracting data from advertising page"""
        p_items = MyPropertyItem()

        """EXTRACT JSON"""
        script_extract = response.xpath('//script[@id="myhome.ie-state"]/text()').get()
        json_data_decode = re.sub('&q;', '"', script_extract)
        data_extract = json.loads(json_data_decode)

        property_data_extract = next(iter(data_extract.values()))
        property_data = property_data_extract['body']

        """BASE INFO"""
        property_data_main = property_data['Brochure']['Property']

        property_source_website = 'https://www.myhome.ie/'
        property_link = response.url

        property_title = property_data_main.get('DisplayAddress')
        property_price_extract = property_data_main.get('Price')
        if property_price_extract:
            property_price = property_price_extract.get('MinPrice')
        else:
            property_price = None

        property_type = property_data_main.get('PropertyType')

        property_advertise_type_extract = property_data['SeoDetails']['ClassUrl']
        if 'sale' in property_advertise_type_extract:
            property_advertise_type = 'Sale'
        else:
            property_advertise_type = 'Rent'

        property_bedrooms_extract = property_data_main.get('BedsString')
        try:
            property_bedrooms = int(self.get_digits(property_bedrooms_extract))
        except:
            property_bedrooms = None

        property_bathrooms = property_data_main.get('Bathrooms')
        property_square = property_data_main.get('SizeStringMeters')

        """DESCRIPTION"""
        property_data_desc = property_data_main.get('BrochureContent')
        property_description = None
        if property_data_desc:
            for item in property_data_desc:
                if item['ContentType'] == 'Description':
                    property_description = item['Content']

        property_data_facil = property_data_main.get('PropertyFeatureTypes')
        if property_data_facil:
            property_facilities = []
            for item in property_data_facil:
                element = item['Name']
                property_facilities.append(element)
        else:
            property_facilities = None

        property_desc_data_extract = response.xpath('//div[@class="PropertyDetails__Description mt-3"]').get()
        property_desc_data_extract_list = [
                                              item.split('/section>')[0]
                                              for item in property_desc_data_extract.split('mb-2"')
                                          ][1:]
        property_features = None
        for element in property_desc_data_extract_list:
            if '>Features<' in element:
                property_features = [
                                        item.split('</li>')[0]
                                        for item in property_desc_data_extract.split('<li>')
                                    ][1:]

        """COORDINATES"""
        property_coordinates = property_data_main.get('BrochureMap')

        """PHOTOS"""
        property_photos_extract = property_data_main.get('Images')
        if property_photos_extract:
            property_photos = []
            for item in property_photos_extract:
                element = item['Url']
                property_photos.append(element)
        else:
            property_photos = None

        """AGENCY"""
        property_agency_data = property_data['Brochure']['Group']
        property_agency = property_agency_data.get('Name')
        property_agency_phone = property_agency_data.get('DisplayPhone')
        property_agency_email = property_agency_data.get('Email')

        """DATES"""
        property_update_date_extract = property_data_main.get('RefreshedOn')
        if property_update_date_extract:
            property_update_date_chop = property_update_date_extract[:10]
            property_update_date = datetime.strptime(property_update_date_chop, '%Y-%m-%d')
        else:
            property_update_date = datetime.utcnow()

        date_time_get = datetime.utcnow()
        date_time = date_time_get.strftime("%Y.%m.%d %H:%M:%S")

        p_items['property_source_website'] = property_source_website
        p_items['property_link'] = property_link
        p_items['property_title'] = property_title
        p_items['property_price'] = property_price
        p_items['property_type'] = property_type
        p_items['property_advertise_type'] = property_advertise_type
        p_items['property_bedrooms'] = property_bedrooms
        p_items['property_bathrooms'] = property_bathrooms
        p_items['property_square'] = property_square
        p_items['property_description'] = property_description
        p_items['property_facilities'] = property_facilities
        p_items['property_features'] = property_features
        p_items['property_coordinates'] = property_coordinates
        p_items['property_photos'] = property_photos
        p_items['property_agency'] = property_agency
        p_items['property_agency_phone'] = property_agency_phone
        p_items['property_agency_email'] = property_agency_email
        p_items['property_update_date'] = property_update_date
        p_items['date_time'] = date_time

        yield p_items


class IrelandMyhomeScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = IrelandMyhomeSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = IrelandMyhomeScraper()
    scraper.run_spiders()
