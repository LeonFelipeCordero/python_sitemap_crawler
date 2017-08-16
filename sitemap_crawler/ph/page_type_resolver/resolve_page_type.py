import random


def resolve_page_type(url, domain):
    # TODO make the logic necessary to resolver your own page type
    return url.replace('https://www.', '').replace('http://www.', '').replace(domain + '/', '')
