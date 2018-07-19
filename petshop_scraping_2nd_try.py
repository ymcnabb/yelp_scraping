#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 17:06:21 2018

Credit: The Scraping function was adapted from rex woon's blog (see
https://rexdatascience.wordpress.com/2015/07/10/hello-world/)
"""
import pandas as pd
from bs4 import BeautifulSoup
import requests

#Edited function, customized for pet shops

data=[]
for page in range(0, 70, 10): #This part can be automated. Here I manually added a range corresponding to the number of petshops
    #The url can be more general: find_desc and find_loc here are specific for my project 
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

# Converting to a data frame and doing some cleaning
df = pd.DataFrame(data)
df.info()
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['address'] = df['address'].str.strip()
df['neighbourhood'] = df['neighbourhood'].str.strip()

# A useful function to remove html tags
def remove_html_tags(text):
    """Remove html tags from a string. Adapted from Jorge Luis Galvis Quintero's script
    https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text))

# Removing them tags
remove_html_tags(df.iloc[:,1])
remove_html_tags(df.name)

"""
This is some extra data cleaning I had to do as some nieghbourhoods weren't entered in the hood field. I got the neighbourhood
"""
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

"""
Steps for scraping reviews:
1. Create a list of the yelp urls of each Amsterdam business
2. For each url, get the reviews

The following code was very much inspired by Gordon Yun's post on scraping:
https://datacritics.com/2018/06/01/python-webscraping/
"""

# Make a list of the petshops' urls
urls = df['url']
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
