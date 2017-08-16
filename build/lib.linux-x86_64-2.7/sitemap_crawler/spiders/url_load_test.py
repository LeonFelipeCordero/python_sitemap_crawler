

from asyncore import dispatcher
from datetime import datetime
import scrapy
from scrapy import signals
from sitemap_crawler.ph.elastic_parsers.elastic_parsers import parse_file_test
from sitemap_crawler.ph.elastic_search_connection.elastic_search_connection import connection
from sitemap_crawler.ph.file_utils.read_urls_csv import read_urls


class UrlLoadTest(scrapy.Spider):
    name = 'url_load_test'
    allowed_domains = []
    start_urls = []
    handle_httpstatus_list = [404, 500, 503, 302, 301, 303]

    def __init__(self, **kwargs):
        self.urls = read_urls(kwargs['path_file'])
        self.coverage = int(kwargs.get('total_requests'))
        self.domain = kwargs['domain']
        self.allowed_domains.append(self.domain)
        self.setUrls()
        self.start_test_at = datetime.now()

        self.elastic_connection = connection()

        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super(UrlLoadTest, self).__init__(**kwargs)

    def spider_closed(self):
        doc = parse_file_test(self.start_test_at)
        self.elastic_connection.index(index='load_test', doc_type='file_test', body=doc)

    def parse(self, response):
        pass

    def setUrls(self):
        for url in self.urls:
            for number in range(1, self.coverage):
                self.start_urls.append(url)
