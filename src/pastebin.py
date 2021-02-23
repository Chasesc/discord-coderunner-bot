import random
import requests

from bs4 import BeautifulSoup
from collections import namedtuple

URI = 'https://pastebin.com'

Archive = namedtuple('Archive', ['url', 'raw_url', 'name', 'posted', 'syntax'])

def archives():
    archive_uri = f'{URI}/archive'
    r = requests.get(archive_uri)

    if not r.ok:
        print('oh no')
        return []

    soup = BeautifulSoup(r.content, 'html.parser')
    rows = soup.find_all('tr')[1:]
    recent_archives = []    

    for row in rows:
        row_data = row.find_all('td')
        if len(row_data) != 3:
            continue

        name, posted, syntax = row_data
        href = name.find('a').get('href')
        url = f'{URI}{href}'
        raw_url = f'{URI}/raw{href}' 

        recent_archives.append(Archive(url, raw_url, name.text, posted.text, syntax.text.lower()))

    return recent_archives

def random_archive(filter_func=None):
    if filter_func is None:
        filter_func = lambda x: x

    recent_archives = list(filter(filter_func, archives()))
    return random.choice(recent_archives)

def download_paste(paste):
    r = requests.get(paste.raw_url)
    if r.ok:
        return r.text
    else:
        return None

if __name__ == '__main__':
    a = random_archive(lambda a: a.syntax in {'c++', 'java', 'python', 'swift', 'scala'})
    print(download_paste(a))