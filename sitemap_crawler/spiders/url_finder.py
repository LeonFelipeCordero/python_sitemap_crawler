from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from sitemap_crawler.ph.spiders.sitemap.ph_url_finder import PhUrlFinder


class UrlFinder(PhUrlFinder):
    name = "spider_finder"
    allowed_domains = []
    sitemap_urls = []
    handle_httpstatus_list = [400, 404, 500, 503, 302, 301, 303]

    def __init__(self, **kwargs):
        self.path = kwargs['path_file']
        self.domain = kwargs['domain']
        self.sitemap_index_url = kwargs['sitemap_url']
        self.allowed_domains.append(self.domain)
        self.sitemap_urls.append(self.sitemap_index_url)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        super(UrlFinder, self).__init__(**kwargs)

    def spider_closed(self):
        result = set(self.urls) - set(self.current_sitemap_urls)
        self.logger.debug('urls not found in sitemap: ' + str(result))
        self.logger.debug('total urls: ' + str(len(result)))
