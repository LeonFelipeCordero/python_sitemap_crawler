import logging
from datetime import datetime
from dateutil import parser
from scrapy import Request
from scrapy.spiders import SitemapSpider
from scrapy.utils.log import configure_logging
from scrapy.utils.sitemap import sitemap_urls_from_robots, Sitemap

from sitemap_crawler.ph.page_type_resolver.resolve_page_type import resolve_page_type

logger = logging.getLogger(__name__)


class PhSitemapSpider(SitemapSpider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def __init__(self, *a, **kw):
        self.arguments = kw
        self.urls_counter = 0
        # self.errors = []
        # self.redirects = []
        # self.wrong_canonicals = []
        self.sub_sitemaps_counts = {}
        self.sitemap_date_updated = ''
        self.sitemap_generated = True
        super(PhSitemapSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass

    def _parse_sitemap(self, response):
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning("Ignoring invalid sitemap: %(response)s",
                               {'response': response}, extra={'spider': self})
                return

            s = Sitemap(body)
            self.save_date_generated(response, s)
            if s.type == 'sitemapindex':
                for loc in iterloc(s, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc in iterloc(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            self.urls_counter += 1
                            self.set_count(response)
                            if self.urls_requested_quantity(response):
                                yield Request(loc, callback=c)
                            break

    def set_count(self, response):
        type = resolve_page_type(response.url, self.arguments['domain'])
        if type in self.sub_sitemaps_counts.keys():
            self.sub_sitemaps_counts[type] = self.sub_sitemaps_counts[type] + 1
        else:
            self.sub_sitemaps_counts[type] = 1

    def save_date_generated(self, response, body):
        if response.url == str(self.arguments.get('sitemap_link')):
            for loc in body:
                timedelta = datetime.now().replace(tzinfo=None) - parser.parse(loc['lastmod']).replace(tzinfo=None)
                if timedelta.days > 5:  # TODO change 5 for your own option
                    self.sitemap_date_updated = parser.parse(loc['lastmod']).replace(tzinfo=None)
                    self.sitemap_generated = False

    def urls_requested_quantity(self, response):
        type = resolve_page_type(response.url, self.arguments['domain'])
        if self.sub_sitemaps_counts[type] > self.arguments['total_urls']:
            return False
        return True


def iterloc(it, alt=False):
    for d in it:
        yield d['loc']

        # Also consider alternate URLs (xhtml:link rel="alternate")
        if alt and 'alternate' in d:
            for l in d['alternate']:
                yield l
