from datetime import datetime

from sitemap_crawler.ph.page_type_resolver.resolve_page_type import resolve_page_type


def parse_canonical(canonical, request_url, response):
    return {
        'canonical': canonical,
        'request_url': request_url,
        'status_code': response.status,
        'page_type': resolve_page_type(request_url, response.url),
        'date': datetime.now()
    }


def parse_redirect_error(response):
    return {
        'request_url': response.request.url,
        'status_code': response.status,
        'date': datetime.now()
    }


def parse_crawl(urls_counter, sub_sitemaps_counts, sitemap_date_updated, sitemap_generated):
    return {
        'urls_counter': urls_counter,
        'sub_sitemaps_counts': sub_sitemaps_counts,
        'sitemap_date_updated': sitemap_date_updated,
        'sitemap_generated': sitemap_generated,
        'date': datetime.now()
    }


def parse_file_test(start_date):
    return {
        'start_at': start_date,
        'end_at': datetime.now()
    }
