from datetime import datetime

import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from sitemap_crawler.ph.elastic_parsers.elastic_parsers import parse_file_test, parse_redirect_error
from sitemap_crawler.ph.elastic_search_connection.elastic_search_connection import connection
from sitemap_crawler.ph.file_utils.read_urls_csv import read_urls


class UrlLoadTest(scrapy.Spider):
    name = 'url_load_test'
    allowed_domains = []
    start_urls = []
    handle_httpstatus_list = [400, 404, 500, 503, 302, 301, 303]

    def __init__(self, **kwargs):
        kwargs['path_file'] = '/home/leon/workspace/projects/sitemap_crawler/test.csv'
        kwargs['domain'] = 'walmart.com.mx'
        kwargs['total_requests'] = '5'
        self.urls = read_urls(kwargs['path_file'])
        self.total_request = int(kwargs.get('total_requests'))
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

    def validate_response(self, response):
        self.validate_redirects(response)
        self.validate_error(response)

    def validate_redirects(self, response):
        if self.is_redirect(response.status):
            doc = parse_redirect_error(response)
            self.elastic_connection.index(index='load_test', doc_type='redirects', body=doc)

    def validate_error(self, response):
        if self.is_error(response.status):
            doc = parse_redirect_error(response)
            self.elastic_connection.index(index='load_test', doc_type='error', body=doc)

    def setUrls(self):
        for url in self.urls:
            for number in range(1, self.total_request):
                self.start_urls.append(url)

    @staticmethod
    def is_redirect(status):
        return status == 301 or status == 302 or status == 303

    @staticmethod
    def is_error(status):
        return status == 404 or status == 500 or status == 503
