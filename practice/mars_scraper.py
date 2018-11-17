from bs4 import BeautifulSoup as bs
import requests
import pymongo
import pandas as pd
from splinter import Browser
import re
import time
from os.path import basename

def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


#get details of all items


#get headlines from NASA website
def getHeadlines():
    news_dict = {}
    browser = init_browser()
    #to get the headlines
    # URL of page to be scraped -NASA Mars News
    url1 = 'https://mars.nasa.gov/news/'
    browser.visit(url1)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(browser.html, 'lxml')
    # Select the container for main contents > article containers
    news_hits = soup.find('div', class_='grid_list_page module content_page')\
        .find_all('div', class_='image_and_description_container')

    # Go through each article and strip the title and preview summary
    for news in news_hits:
        title = news.find('div', class_='content_title').get_text()
        para = news.find('div', class_='article_teaser_body').get_text()
        news_dict["Title"] = title
        news_dict["Para"] = para

        break


    browser.quit()
    return news_dict


# news = getHeadlines()
# print(news)


def getFeaturedImage():
    caro_dict = {}
    browser = init_browser()

    base_url = 'https://www.jpl.nasa.gov' 
    url = base_url + '/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Have splinter focus on the full size of the featured image
    browser.click_link_by_partial_text('FULL IMAGE')

    # Pause to give browser time to load before moving on
    time.sleep(2)

    # Scrape the URL of the image
    html = browser.html
    jpl_soup = bs(html, 'html.parser')
    feature_img_tag = jpl_soup.find('img', class_='fancybox-image')
    feature_img_url = feature_img_tag.get('src')
    print(base_url + feature_img_url)

    caro_dict['featured_img_url'] = base_url + feature_img_url

    # Grab the image itself
    save_dir = basename(feature_img_url)
    featured_img = requests.get(base_url+feature_img_url).content
    
    with open(save_dir, 'wb') as dl:
        dl.write(featured_img)   
    
    browser.quit()
    return caro_dict


# caro = getFeaturedImage()
# print(caro)


def getTweets():

    Tweet_dict = {}
    browser = init_browser()
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)
    soup = bs(browser.html, 'lxml')
    MarsWeather = soup.find('p', class_="tweet-text").text
    Tweet_dict['Mars_Weather'] = {'MarsWeather': MarsWeather}
    browser.quit()
    return Tweet_dict


# tweepy = getTweets()
# print(tweepy)


def getMarsFacts():
    Mars_dict = {}
    url4 = "https://space-facts.com/mars/"
    table = pd.read_html(url4)

    profile =table[0]
    
    df = table[0]
    df.columns = ["description", "value"]
    df.set_index("description")
    table = df.to_html(classes=['table-table-striped'])



    browser = init_browser()
    browser.visit(url4)
    soup = bs(browser.html, 'lxml')
    profile = soup.find('p').text

    Mars_dict = {'profile': profile, 'table': table}

    browser.quit()

    return Mars_dict


# mfact = getMarsFacts()
# print(mfact)


def getMarsHemispheres():
    Hemi_dict = {}
    browser = init_browser()
    url5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url5)
    time.sleep(2)
    soup = bs(browser.html, 'lxml')
    results = soup.find_all(class_='item')

    marsHemList = []
    marsHem = {}

    for x in results:
        img = x.find('img')
        img_url = img['src']
        title = x.find('h3').text
        marsHem.update({title: ('https://astrogeology.usgs.gov' + img_url)})
        marsHem = {
            "title": title,
            "img_url": ('https://astrogeology.usgs.gov' + img_url)
        }
        marsHemList.append(marsHem)

    print()
    print()
    print()
    print(marsHemList)

    Hemi_dict['images'] = marsHemList
    browser.quit()
    return Hemi_dict


#print(getMarsHemispheres())

# # def getMarsInfo():
#     browser = init_browser()
#     news = getHeadlines()
#     print("\nMars News: " + news)
#     caro = getFeaturedImage()
#     print(caro)
#     print("Caro  \n")
#     tweepy = getTweets()
#     print(tweepy)
#     print("\n Tweets")
#     mfact = getMarsFacts()
#     print("\n Facts")
#     print(mfact)
#     mHemisphere= getMarsHemispheres()
#     print("\n Hemispheres")
#     print(mHemisphere)
