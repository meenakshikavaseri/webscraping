# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
from os.path import basename
import time
import pandas as pd
import pymongo


def scrape():
    # Create connection variable
    conn = 'mongodb://localhost:27017'

    # Pass connection to the pymongo instance.
    client = pymongo.MongoClient(conn)

    # Connect to a database. Will create one if not already available.
    db = client.mars_db

    mongo_mars_dict = {}
    
    # Splinter set up
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    # Open browser with splinter for scraping
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    mars_soup = BeautifulSoup(html, 'html.parser')

    # Select the container for main contents > article containers
    news_hits = mars_soup.find('div', class_='grid_list_page module content_page')\
        .find_all('div', class_='image_and_description_container')

    # Create lists for findings
    news_list = []

    # Go through each article and strip the title and preview summary
    for news in news_hits:
        title = news.find('div', class_='content_title').get_text()
        tease = news.find('div', class_='article_teaser_body').get_text()
        # Check the count of items scraped and preview the last find
        
        news_list.append({'title':title, 'teaser':tease})
    

    mongo_mars_dict['news'] = news_list

    # Redirect browser to the JPL website and prepare for scraping
    base_url = 'https://www.jpl.nasa.gov' 
    url = base_url + '/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Have splinter focus on the full size of the featured image
    browser.click_link_by_partial_text('FULL IMAGE')

    # Pause to give browser time to load before moving on
    time.sleep(5)

    # Scrape the URL of the image
    html = browser.html
    jpl_soup = BeautifulSoup(html, 'html.parser')
    feature_img_tag = jpl_soup.find('img', class_='fancybox-image')
    feature_img_url = feature_img_tag.get('src')
    print(base_url + feature_img_url)

    mongo_mars_dict['featured'] = base_url + feature_img_url

    # Grab the image itself
    save_dir = basename(feature_img_url)
    featured_img = requests.get(base_url+feature_img_url).content
    with open(save_dir, 'wb') as dl:
        dl.write(featured_img)

    # Navigate to mars weather report twitter page
    twit_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twit_url)

    # Grab html
    html = browser.html
    twit_soup = BeautifulSoup(html, 'html.parser')

    # Grab first tweet for weather status
    tweet = twit_soup.find('div', class_='js-tweet-text-container').get_text()
    print(tweet)

    mongo_mars_dict['tweet'] = tweet

    # Redirect to space-facts page
    fact_url = 'http://space-facts.com/mars/'
    browser.visit(fact_url)
    html = browser.html
    fact_soup = BeautifulSoup(html, 'html.parser')

    # Scrape the page for main facts
    facts_html = pd.read_html(fact_url)
    facts_pd = facts_html[0]

    # Adjust resulting dataframe
    facts_pd.columns = ['', 'Mars']
    #facts_pd.set_index('Planet Profile', inplace=True)

    pre_db_facts = facts_pd.to_html(index=False)
    pre_db_facts = str(pre_db_facts).replace('\n', '')

    mongo_mars_dict['profile'] = pre_db_facts

    facts = fact_soup.find('div', id='facts').find('ul').find_all('li')

    # Containers for fact portions
    fact_head = []
    fact_body = []
    facts_for_db = []

    # Scrape for facts
    for fact in facts:
        head_sp = fact.find('strong')
        fact_head.append(head_sp.get_text())
        body = fact.get_text().split('\n')[1]
        fact_body.append(body)
        facts_for_db.append({'fact':head_sp.get_text(), 'explanation':body})

    # Check scrape results
    print(f'{len(fact_head)} / {len(fact_body)}')

    mongo_mars_dict['facts'] = facts_for_db

    about_mars_pd = pd.DataFrame({'Fact':fact_head, 'Explanation':fact_body})

    rel_sp = fact_soup.find('div', class_='yarpp-related').find_all('a')

    # Containers for related fact portions
    rel_head = []
    rel_body = []
    rel_link = []

    # Scrape for facts
    for fact in rel_sp:
        rel_head.append(fact.get_text())
        rel_link.append(fact['href'])
        rel_body.append(fact.next_sibling)

    # Check scrape results
    print(f'{len(rel_head)} / {len(rel_body)} / {len(rel_link)}')
        
    related_pd = pd.DataFrame({'Title':rel_head, 'Teaser':rel_body, 'Link':rel_link})

    # Navigate to the USGS astrogeology webpage's search results on Mars' hemispheres
    base_url = 'https://astrogeology.usgs.gov'
    srch_url = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(base_url + srch_url)

    # Grab all the search results
    html = browser.html
    usgs_soup = BeautifulSoup(html, 'html.parser')
    items = usgs_soup.find('div', class_='collapsible results').find_all('div', class_='item')

    # Grab the URL and image for each result
    usgs_urls = []
    for item in items:
        img_url = item.find('a')['href']
        usgs_urls.append(base_url+img_url)

    # Containers for found urls and images
    usgs_img_urls = []
    usgs_imgs = []
    usgs_names = []
    local_usgs_locs = []
    images_for_db = []

    # Visit all the image pages 
    for url in usgs_urls:
        browser.visit(url)
        
        html = browser.html
        usgs_img_sp = BeautifulSoup(html, 'html.parser')
        
        # Get the name of the hemisphere
        usgs_name = usgs_img_sp.find('h2', class_='title').get_text()
        usgs_names.append(usgs_name)
        
        # Find the 2nd link in downloads associated with the enhanced res
        full_img_url = base_url + usgs_img_sp.find('img', class_='wide-image')['src']
        
        # Add to list
        usgs_img_urls.append(full_img_url)
        
        # Download images
        save_dir = basename(full_img_url)
        full_img = requests.get(full_img_url).content
        # Save image downloads
        with open(save_dir, 'wb') as dl:
            dl.write(full_img)
            print(f'{full_img_url} downloaded!')
        
        # Save local image locations
        local_usgs_locs.append(save_dir)

        images_for_db.append({'name':usgs_name, 'url':full_img_url, 'local': save_dir})
    
    mongo_mars_dict['hemis'] = images_for_db

    print(mongo_mars_dict)

    # Drops collection if available to remove duplicates
    db.mars.drop()
    # Insert updated collection
    db.mars.insert(mongo_mars_dict)
    browser.quit()

    return