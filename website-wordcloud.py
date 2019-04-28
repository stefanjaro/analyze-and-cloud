"""
Crawls through a website, extracting text content, and outputs a wordcloud
"""

#import necessary libraries
import requests
import time
import pandas as pd
from wordcloud import WordCloud
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Comment

def get_links_from_page(soup):
    """
    Get all the links from a page
    """
    # debug statement
    print("Extracting Links")

    # extract all links
    links = [x.get('href') for x in soup.find_all("a")]
    return links

def get_content_from_page(soup, file_store):
    """
    Get all text content from a page and store in the location
    specified by the file_store parameter
    """
    # debug statement
    print("Extracting Text")

    # extract only the body code
    body = soup.body

    # remove elements we don't want to consider
    forbidden_tags = [
        "style", "script", "noscript", "footer", "aside",
        "img", "form", "button", "nav", "figure", "a", "meta"
    ]

    for tag in forbidden_tags:
        try:
            for elem in body.find_all(tag):
                elem.decompose()
        except:
            continue

    # remove comments
    try:
        for item in body.find_all(string=lambda x: isinstance(x, Comment)):
            item.extract()
    except:
        pass

    # get all visible text, clean and join
    visible_text = [x for x in body.find_all(text=True) if x not in ["\n", "", " "]]
    joined_text = " ".join(visible_text)

    # store text
    with open(file_store, "a") as file:
        file.write(joined_text)

def verify_links(home_url, crawled_links, new_links):
    """
    Ensures the new links extracted are not duplicates, external links, 
    or haven't already been crawled
    """
    # debug statement
    print("Verifying Links")

    # get the website's domain name and primary scheme (http or https)
    domain_name = urlparse(home_url).netloc
    domain_scheme = urlparse(home_url).scheme

    # remove all NoneTypes
    verified_links = [x for x in new_links if x != None]

    # remove all external links
    verified_links = [x for x in verified_links if domain_name in x]

    # remove parameters and fragments
    parsed_links = [urlparse(x) for x in verified_links]
    verified_links = [urljoin(x.scheme + "://" + x.netloc, x.path) for x in parsed_links]

    # remove www and http or https from the start of the url and rebuild for standardization
    verified_links = [x.replace("https://", "").strip() for x in verified_links]
    verified_links = [x.replace("http://", "").strip() for x in verified_links]
    verified_links = [x.replace("www.", "").strip() for x in verified_links]
    verified_links = [domain_scheme + "://www." + x for x in verified_links]

    # remove all links that have already been crawled
    verified_links = [x for x in verified_links if x not in crawled_links]

    # remove duplicates
    verified_links = list(set(verified_links))

    return verified_links

def make_request_and_parse(url):
    """
    Makes a get request and parses the page's html
    """
    # debug statement
    print(f"Making Request to {url}")

    # make request, if it fails return crawl failed
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"}
    try:
        response = requests.get(url=url, headers=headers)
    except:
        return "Request Failed"

    # if page is not text/html return "Invalid Type"
    if "text/html" not in response.headers["Content-Type"]:
        return "Invalid Type"
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

def get_unique_tags(soup):
    """
    Gets a list of the unique html tags in the document.
    To be used only for debugging
    """
    tags = [tag.name for tag in soup.find_all()]
    return list(set(tags))

def crawler(start_url, page_limit=None, file_store="website_text.txt"):
    """
    Crawl a website starting from a url, collecting more links to crawl and extract
    text content from. Number of pages crawled will be restricted by the page_limit parameter
    """
    # variables to store list of crawled pages, pages to crawl, and number of pages crawled
    crawled_pages = []
    pages_to_crawl = [start_url]
    crawl_counter = 0
    
    # variable to store crawl status of pages
    page_crawl_status = []

    while True:
        # get url to crawl
        url = pages_to_crawl[0]

        # crawl url and store in list of crawled pages
        soup = make_request_and_parse(url)
        crawled_pages.append(pages_to_crawl.pop(0))

        # if invalid type or crawl failed was returned as the above continue to next link
        if soup == "Invalid Type" or soup == "Request Failed":
            print(f"{url} is not of text/html content type or the request failed")
            page_crawl_status.append({
                "Page": url,
                "Crawl Status": soup
            })
            time.sleep(2)
            continue

        # get links, verify and store in pages to crawl and remove duplicates
        links_on_page = get_links_from_page(soup)
        pages_to_crawl.extend(verify_links(start_url, crawled_pages, links_on_page))
        pages_to_crawl = list(set(pages_to_crawl))

        # get and save text content
        get_content_from_page(soup, file_store)

        # update number of pages crawled
        crawl_counter += 1

        # update crawl status
        page_crawl_status.append({
            "Page": url,
            "Crawl Status": "Crawled"
        })

        # if we've reached our limit or there are no more pages break the loop
        if crawl_counter == page_limit or len(pages_to_crawl) == 0:
            break

        # print progress update
        print(f"Number of pages crawled: {len(crawled_pages)}")
        print(f"Number of pages that can be crawled: {len(pages_to_crawl)}")

        # pause before sending next request
        print("Pausing before next request")
        time.sleep(2)

    # returning primarily for debugging
    return page_crawl_status

def create_wordcloud(file_store):
    """
    Turns the extracted text from a website into a wordcloud
    """
    # import text to be turned into a wordcloud
    with open(file_store, "r") as file:
        wc_text = file.read()

    # configure wordcloud object
    wc = WordCloud(
        width=1200,
        height=800,
        prefer_horizontal=0.9,
        min_font_size=8,
        max_words=100,
        background_color="white",
        collocations=False,
        colormap="viridis",
        normalize_plurals=True
    )

    # generate and save wordcloud
    wc.generate_from_text(wc_text)
    wc.to_file("website_wordcloud.png")

if __name__ == "__main__":
    # specify start url and file path to store extracted text
    start_url = "http://www.stax.com/"
    file_store="stax.txt"

    # run crawler
    page_crawl_status = crawler(start_url=start_url, page_limit=50, file_store=file_store)

    # export crawl log and pages to crawl log
    pd.DataFrame(page_crawl_status).to_csv("crawl_log.csv", index=False, encoding="utf-8")

    # create wordcloud
    create_wordcloud(file_store)

    # print completion message
    print(f"Your word cloud has been created for {start_url}")