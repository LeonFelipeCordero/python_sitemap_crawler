from elasticsearch import Elasticsearch


def connection():
    #TODO set your connection here
    return Elasticsearch()