import logging
from scrapy import Request
from scrapy.spiders import SitemapSpider
from scrapy.utils.log import configure_logging
from scrapy.utils.sitemap import sitemap_urls_from_robots, Sitemap

from sitemap_crawler.ph.file_utils.read_urls_csv import read_urls

logger = logging.getLogger(__name__)


class PhUrlFinder(SitemapSpider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def __init__(self, *a, **kw):
        self.path = ''
        self.urls = read_urls(self.path)
        self.current_sitemap_urls = []
        self.urls_no_found = {}
        super(PhUrlFinder, self).__init__(*a, **kw)

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
            if s.type == 'sitemapindex':
                for loc in iterloc(s, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc in iterloc(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            if self.is_sitemap(loc):
                                yield Request(loc, callback=c)
                            else:
                                self.current_sitemap_urls.append(loc)
                            break

    @staticmethod
    def is_sitemap(url):
        return url.contains('xml')


def iterloc(it, alt=False):
    for d in it:
        yield d['loc']

        # Also consider alternate URLs (xhtml:link rel="alternate")
        if alt and 'alternate' in d:
            for l in d['alternate']:
                yield l
