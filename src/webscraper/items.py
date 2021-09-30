import scrapy


class MyPropertyItem(scrapy.Item):
    property_source_website = scrapy.Field()
    property_link = scrapy.Field()
    property_title = scrapy.Field()
    property_price = scrapy.Field()
    property_type = scrapy.Field()
    property_category = scrapy.Field()
    property_advertise_type = scrapy.Field()
    property_bedrooms = scrapy.Field()
    property_bathrooms = scrapy.Field()
    property_square = scrapy.Field()
    property_description = scrapy.Field()
    property_facilities = scrapy.Field()
    property_features = scrapy.Field()
    property_coordinates = scrapy.Field()
    property_photos = scrapy.Field()
    property_agency = scrapy.Field()
    property_agency_phone = scrapy.Field()
    property_agency_email = scrapy.Field()
    property_update_date = scrapy.Field()
    date_time = scrapy.Field()
    pass
