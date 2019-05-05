# Website Wordcloud (functional but still a work in progress)
Crawl a website and create a word cloud from all of its text content

### Further Work Required
* Test on more websites
* Remove the text common to every page
* Currently very basic app, no validation, no other options, only scans one page (since I'm still testing)
* Add validation so invalid urls aren't entered
* Check for robots.txt no crawling and prevent crawling if that's there
* Need to allow users to specify number of pages to be crawled
* Need to show users live output of the crawling so they don't think the site is stuck
* Create the leave feedback page as well
* When a session starts run a function to clean up extracted text and wordclouds older than 5 minutes so I don't run out of storage space (or can I just save it all in a DB?)