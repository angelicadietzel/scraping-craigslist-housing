from requests import get 
from bs4 import BeautifulSoup
from time import sleep
import re
from random import randint 
from warnings import warn
from time import time
from IPython.core.display import clear_output
import numpy as np
import pandas as pd
from datetime import datetime

# request the contents of the page we're scraping
results = get('https://phoenix.craigslist.org/d/apartments-housing-for-rent/search/apa?availabilityMode=0&hasPic=1')

# make the content we grabbed easy to read
html_soup = BeautifulSoup(results.text, 'html.parser')

# get the macro-container containing the posts we want
post = html_soup.find_all('li', class_= 'result-row')


# find the total number of posts to find the limit of the pagination
find_total = html_soup.find('div', class_= 'search-legend')

# grab the total count of posts 
total_posts = int(find_total.find('span', class_='totalcount').text) 

# vary the value of the page parameters
pages = np.arange(0, total_posts+1, 120)

# count tracker for number of iterations
iterations = 0

# initialize empty lists where we'll store our date 
post_times = []
post_neighborhoods = []
post_titles = []
post_bedrooms = []
post_sqft = []
post_links = []
post_prices = []


# create for loop
for page in pages:
    
    # get request
    response = get("https://phoenix.craigslist.org/search/apa?" 
                   + "s=" # parameter for defining the page number 
                   + str(page) # page number in the pages array 
                   + "&hasPic=1"
                   + "&availabilityMode=0")
    
    # control the crawl rate 
    sleep(randint(1,10))
    
    # throw warning for status codes that are not 200
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))
        
    # define the html text
    html = BeautifulSoup(response.text, 'html.parser')
    
    # define the posts
    posts = html_soup.find_all('li', class_= 'result-row')
   
   # extract data item-wise
    for post in posts:

        # if we aren't missing the neighborhood information
        if post.find('span', class_ = 'result-hood') is not None:

            # date
            post_datetime = post.find('time', class_= 'result-date')['datetime']
            post_times.append(post_datetime)

            # neighborhoods
            post_hoods = post.find('span', class_= 'result-hood').text
            post_neighborhoods.append(post_hoods)

            # title 
            post_title = post.find('a', class_='result-title hdrlnk')
            post_title_text = post_title.text
            post_titles.append(post_title_text)

            # link
            post_link = post_title['href']
            post_links.append(post_link)
            
            # removes the \n whitespace from each side, removes the currency symbol, and turns it into an int
            post_price = int(float(post.a.text.strip().replace("$", "").replace(",","")))
            post_prices.append(post_price)
            # if the number of bedrooms OR sqft aren't missing 
            if post.find('span', class_ = 'housing') is not None:
                
                # if the first element is accidentally square footage
                if 'ft' in post.find('span', class_ = 'housing').text.split()[0]:
                    
                    # make bedroom NaN
                    bedroom_count = np.nan
                    post_bedrooms.append(bedroom_count)
                    
                    # make sqft the first element
                    sqft = int(post.find('span', class_ = 'housing').text.split()[0][:-3])
                    post_sqft.append(sqft)
                    
                # if the length of the housing details element is more than 2
                elif len(post.find('span', class_ = 'housing').text.split()) > 2:
                    
                    # therefore element 0 will be bedroom count
                    bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                    post_bedrooms.append(bedroom_count)
                    
                    # and sqft will be number 3, so set these here and append
                    sqft = int(post.find('span', class_ = 'housing').text.split()[2][:-3])
                    post_sqft.append(sqft)
                    
                # if there is num bedrooms but no sqft
                elif len(post.find('span', class_ = 'housing').text.split()) == 2:
                    
                    # therefore element 0 will be bedroom count
                    bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                    post_bedrooms.append(bedroom_count)
                    
                    # and sqft will be number 3, so set these here and append
                    sqft = np.nan
                    post_sqft.append(sqft)                    
                
                else:
                    bedroom_count = np.nan
                    post_bedrooms.append(bedroom_count)
                
                    sqft = np.nan
                    post_sqft.append(sqft)
            # if none of those conditions catch, make bedroom NaN 
            else:
                bedroom_count = np.nan
                post_bedrooms.append(bedroom_count)
                
                sqft = np.nan
                post_sqft.append(sqft)
                
    iterations += 1
      
    print("Page " + str(iterations) + " scraped successfully!")

    
print("\n")
print("Scrape complete!")

phx_apts = pd.DataFrame({'posted': post_times,
                       'neighborhood': post_neighborhoods,
                       'post title': post_titles,
                       'number bedrooms': post_bedrooms,
                        'sqft': post_sqft,
                        'URL': post_links,
                       'price': post_prices})

print(phx_apts.info())
phx_apts

# to move all the scraped data to a CSV file
phx_apts.to_csv('phx_apts.csv', index=False)
