import logging
from asyncore import dispatcher

from scrapy import signals

from sitemap_crawler.ph.elastic_parsers.elastic_parsers import parse_canonical, parse_redirect_error, parse_crawl
from sitemap_crawler.ph.elastic_search_connection.elastic_search_connection import connection
from sitemap_crawler.ph.spiders.sitemap.ph_sitemap_analyzer import PhSitemapSpider

logger = logging.getLogger(__name__)


class SitemapAnalyzer(PhSitemapSpider):
    name = 'sitemap_analyzer'
    sitemap_urls = []
    allowed_domains = []
    handle_httpstatus_list = [404, 500, 503, 302, 301, 303]

    def __init__(self, *a, **kw):
        self.total_urls_for_file = kw['total_urls']
        self.domain = kw['domain']
        self.sitemap_index_url = kw['sitemap_url']
        self.allowed_domains.append(self.domain)
        self.sitemap_urls.append(self.sitemap_index_url)

        self.elastic_connection = connection()

        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super(SitemapAnalyzer, self).__init__(*a, **kw)

    def parse(self, response):
        self.validate_response(response)

    def spider_closed(self):
        doc = parse_crawl(self.urls_counter, self.sub_sitemaps_counts, self.sitemap_date_updated,
                          self.sitemap_generated)
        self.elastic_connection.index(index='sitemap', doc_type='crawl', body=doc)

    def validate_response(self, response):
        self.validate_canonical(response)
        self.validate_redirects(response)
        self.validate_error(response)

    def validate_canonical(self, response):
        canonical, request_url = self.get_urls(response)
        if canonical != request_url:
            doc = parse_canonical(canonical, request_url, response.statu)
            self.elastic_connection.index(index='sitemap', doc_type='canonicals', body=doc)

    def validate_redirects(self, response):
        if self.is_redirect(response.status):
            doc = parse_redirect_error(response)
            self.elastic_connection.index(index='sitemap', doc_type='redirects', body=doc)

    def validate_error(self, response):
        if self.is_error(response.status):
            doc = parse_redirect_error(response)
            self.elastic_connection.index(index='sitemap', doc_type='error', body=doc)

    @staticmethod
    def get_urls(response):
        return response.css('head link[rel=canonical]::attr(href)').extract_first(), response.request.url

    @staticmethod
    def is_redirect(status):
        return status == 301 or status == 302 or status == 303

    @staticmethod
    def is_error(status):
        return status == 404 or status == 500 or status == 503
