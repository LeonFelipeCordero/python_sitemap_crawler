import csv


def read_urls(path):
    urls = []
    with open(path, 'rb') as csv_file:
        reader = csv.reader(csv_file, delimiter='\n')
        for row in reader:
            urls.append(row)
    return urls
