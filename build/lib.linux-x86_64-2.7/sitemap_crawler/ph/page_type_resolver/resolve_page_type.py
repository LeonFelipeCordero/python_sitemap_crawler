import random


def resolve_page_type(url):
    #TODO make the logic necessary to resolver your own page type
    pages = ['page1', 'page2', 'page3', 'page4', 'page5', 'page6', 'page7', 'page8', 'page9']
    return random.sample(pages, 1)
