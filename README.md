# Scrapy spider for www.myhome.ie

This spider scraps data form advertising pages of real estate website.
Spider covers all existing pagination pages of properties that if on sale.

## Spider collects from each page:
- Link to advertising page
- Title
- Price
- Property type
- Property category
- Property advertise type
- Number of bedrooms
- Number of bathrooms
- Property square
- Description
- Property facilities
- Property features
- Coordinates
- Photos urls
- Real estate agency name
- Agency phone
- Agency email
- Advertising last update date
- Date and time when page was scraped

### Path to spider file
- scr
  - webscraper
    - spiders
      - ireland_myhome_spider.py

### Path to example of output file with stored data
- scr
  - extracted_data
    - myhome_test.json