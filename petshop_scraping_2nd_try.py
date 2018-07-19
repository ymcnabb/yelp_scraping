#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 17:06:21 2018

@author: mcnab002

Scraping function adapted from rex woon's blog: 
    https://rexdatascience.wordpress.com/2015/07/10/hello-world/
"""

#Edited function, customized for pet shops

import pandas as pd
from bs4 import BeautifulSoup
import requests


data=[]
for page in range(0, 70, 10):
    url = "https://www.yelp.com/search?find_desc=Pet+Stores&find_loc=Amsterdam,+Noord-Holland,+The+Netherlands&start={0}".format(page)
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, "lxml")
    for item in soup.findAll("li", {"class":"regular-search-result"}):
        url = yelpPage = item.find("a", {"class":"biz-name"})["href"] #url
        name = item.find("a", {"class":"biz-name"}).contents[0] # name of the petshop
        #reviews = item.find("span", {"class":"review-count rating-qualifier"}).contents[0] # number of reviews
        rating = item.find("img", {"class":"offscreen"}) # collects tag for rating
        address = item.find("div", {"class":"secondary-attributes"}).address.getText()
        neighbourhood = item.find("div", {"class":"secondary-attributes"}).span.getText() 
        data.append({"name": name, "url": url, "rating": str(rating)[10:13], "address": address, "neighbourhood": neighbourhood})



df = pd.DataFrame(data)
df.info()
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['address'] = df['address'].str.strip()
df['neighbourhood'] = df['neighbourhood'].str.strip()


def remove_html_tags(text):
    """Remove html tags from a string. Adapted from Jorge Luis Galvis Quintero's script
    https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text))

remove_html_tags(df.iloc[:,1])
remove_html_tags(df.name)

df.head()

# Getting all the unique neighbourhood names
df['neighbourhood'].unique()

# Getting the number of unique neighbourhood names
len(df['neighbourhood'].unique())

# Find those instances of "Phone number" instead of neighbourhood name
df[df['neighbourhood'] == 'Phone number']

# Assign "Diemen" to df.iloc[51,2] 
df.iloc[61,2] = "Diemen"

# Assign "Amstelveen" to df.iloc[10,2] and df.iloc[53:55,2]
df.iloc[63:65,2] = "Amstelveen"
df.iloc[11,2] = "Amstelveen"
df.iloc[20,2] = "Amstelveen"

df.to_csv("amsterdam_petshop_directory.csv")

# Group by neighbourhoods

by_hood_mean_rating = df.groupby('neighbourhood')['rating'].mean()
by_hood_nr_ratings = df.groupby('neighbourhood')['rating'].count()
by_hood_mean_rating_nr = df.groupby('neighbourhood')['rating'].mean().count()
pet_shops_per_hood = df.groupby('neighbourhood')['neighbourhood'].count()

# Plot mean rating per hood
plt.clf()
by_hood_mean_rating.plot.barh()
plt.ylabel("Neighbourhood")
plt.xlabel("Mean rating")
plt.title("Amsterdam petshops: Mean yelp rating per neighbourhood")
plt.tight_layout()
plt.show()

# Plot nr of petshops per hood
plt.clf()
pet_shops_per_hood.plot.barh()
plt.ylabel("Neighbourhood")
plt.xlabel("Number of petshops")
plt.title("Amsterdam: Number of petshops per neighbourhood")
plt.tight_layout()
plt.show()

# Next we can scrape the data from all petshops in the randstad to see if we can say something about
# Rating and location. But next we should do some text mining on ratings.

"""Steps for scraping reviews:
1. Create a list of the yelp url of each Amsterdam business
2. For each url, get the reviews
    """
    
# Grabbing the reviews
"""
Procedure:
create a for loop that:
    1. grabs a url from a list of business urls
    for u in urls
    
    do the following:
    1. take the url
    2. request website content
    3. creat the soup with an html parser
    4. a for loop through all the reviews that retuns the necessary details

The following code was very much inspired by Gordon Yun's post on scraping:
    https://datacritics.com/2018/06/01/python-webscraping/
"""
# Upload the a'dam petshop dataset
ams_petshops = pd.read_csv("amsterdam_petshop_directory.csv")

# Make a list of the petshops' urls
urls = ams_petshops['url']
# Add https://www.yelp.com' to each url
prefix = 'https://www.yelp.com'
urls = ['https://www.yelp.com' + urls for u in urls]

reviews = []

for u in range(len(urls)):
    url = urls[0][u]
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, "html.parser")
    
    for i in range(len(soup.select(' .review-content'))):
        #author = item.select(' .media story .user-passport-info')[i].getText()
        name = soup.select(' .biz-page-title')[0].getText()
        date = soup.select(' .review-content .rating-qualifier')[i].getText()
        rating = soup.select(' .review-content .i-stars')[i].getText
        # the first '5' rating is in str(rating)[67]
        description = soup.select(' .review-content p')[i]
        reviews.append({"name": name, "rating": str(rating)[67], "date": date, "description": description})

reviews_df = pd.DataFrame(reviews)
reviews_df.head()

reviews_df = pd.DataFrame(reviews)
reviews_df.head()
reviews_df['rating'] = pd.to_numeric(reviews_df['rating'], errors='coerce')
reviews_df["name"] = reviews_df["name"].str.strip("\r\n")
reviews_df["date"] = reviews_df["date"].str.strip("\r\n")
reviews_df["date"] = reviews_df["date"].str.strip()
reviews_df["name"] = reviews_df["name"].str.strip()
reviews_df["description"] = [remove_html_tags(review) for review in reviews_df.description]

reviews_df.to_csv("adam_petshops_reviews.csv")


    
# The initial code to grab one business's reviews
url = 'https://www.yelp.com/biz/4-cats-amsterdam?osq=Pet+Stores/reviews'
r = requests.get(url)
html_doc = r.text
soup = BeautifulSoup(html_doc, "html.parser")  

for i in range(len(soup.select(' .review-content'))):
    #author = item.select(' .media story .user-passport-info')[i].getText()
    name = soup.select(' .biz-page-title')[0].getText()
    date = soup.select(' .review-content .rating-qualifier')[i].getText()
    rating = soup.select(' .review-content .i-stars')[i].getText
    # the first '5' rating is in str(rating)[67]
    description = soup.select(' .review-content p')[i]
    reviews.append({"name": name, "rating": str(rating)[67], "date": date, "description": description})