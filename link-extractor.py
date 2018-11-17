# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 20:02:43 2018
Extracts links from an entire website
@author: Stefanj
"""

#import necessary libraries
import requests
import time
import pickle
import urllib.parse
from bs4 import BeautifulSoup

def get_links_on_page(url):
    """
    Get all the links from a page
    """
    #specify headers so the request seems human
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
            }
    #get the page object
    pageobj = requests.get(url=url, headers=headers)
    #parse the text through beautiful soup
    soup = BeautifulSoup(pageobj.text, 'html.parser')
    #extract all of the links from all of the link objects on a page
    links = [linkobj.get('href') for linkobj in soup.find_all("a")]
    return links

#FIX THIS: NEED TO HANDLE FOR HTTPS AND HTTP DUPLICATION
#FIX THIS: NEED TO HANDLE FOR PAGINATION!
#FIX THIS: NEED TO REMOVE PARAMS LIKE ?replytocom=19
def verify_links(home_page_url, links_to_verify):
    """
    Verify the links by dropping the duplicates and external links
    """
    #get the domain name from the home_page_url
    internal_domain = urllib.parse.urlparse(home_page_url).netloc
    #list to store our valid links that we will crawl
    valid_links = []
    #go through each one and drop those that are external or duplicates
    for link in links_to_verify:
        #get the domain of the url
        url_domain = urllib.parse.urlparse(link).netloc
        #defrag the url (drop the fragments) so we don't have the same
        #url in our list with different fragments
        defragged_url = urllib.parse.urldefrag(link)[0]
        #check if the domain is the same and if the link is already in list
        if url_domain == internal_domain and defragged_url not in valid_links:
            valid_links.append(defragged_url)
    return valid_links

#---------------------------------------------------------------------
#ABOVE THIS ARE FUNCTIONS
#---------------------------------------------------------------------

#set the home_page_url
home_page_url = r"https://selftaught.blog/"

#get an initial list of links to crawl from the home page
links_to_crawl = verify_links(home_page_url, get_links_on_page(home_page_url))

#list to store links we've already crawled
crawled_links = []

#crawl through the links transferring previously crawled links into the
#crawled_links list and adding more links to the links_to_crawl list
#until there are no more links to crawl
for link in links_to_crawl:
    if link in crawled_links:
        continue
    #get and verify the links on a page, and add this to links_to_crawl
    links_to_crawl.extend(verify_links(link, get_links_on_page(link)))
    #add this link to crawled_links
    crawled_links.append(link)
    #print a status message
    print(f"EXTRACTED URLS FROM {link}")
    #suspend program before crawling the next link
    #we don't want to ddos the site
    time.sleep(2)

#for now save all links to crawl as a pickle file
#save crawled_links as well
with open("testing_links_to_crawl.p", "wb") as file:
    pickle.dump(links_to_crawl, file)
    
with open("testing_crawled_links.p", "wb") as file:
    pickle.dump(crawled_links, file)

    
        

