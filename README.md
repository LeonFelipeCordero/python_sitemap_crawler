##### Requirements
All the packages are available on all major linux distros

* pyton 2.7.x1

#### Setup

Install scrapy, pip install scrapy  
NOTE: to run the crawler with scrapy set the variables 'total_urls', 'domain', 'sitemap_url' or any other depending of
the spider and use the command 'scrapy crawl /path/crawlerName'

##scrapyd deploy
I like to use scrapyd with scrapyd-client to control deployments into a staging or production environments

Install scrapyd:
pip install scrapyd

Install scrapyd-client:
pip install scrapyd-client

run it scrapyd : scrapyd

to deploy use: 
scrapyd-deploy local-target -p sitemap_crawler

I also use curl to trigger spiders:

curl http://localhost:6800/schedule.json -d project=sitemap_crawler -d spider=spider -d var=$var_value