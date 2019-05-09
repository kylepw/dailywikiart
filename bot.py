'''
    bot.py
    ~~~~~~~~~~~

    Twitter bot that tweets a random image from Wikiart's Hi-Res archive.

'''

import json
import logging
import os
from PIL import Image
import random
import requests
import tweepy
import sqlite3
import sys


CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')


# Source of Hi-Res images
SRC_URL = 'https://www.wikiart.org/?json=2&layout=new&param=high_resolution'


DB_FILENAME = 'urls.db'


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')


''' Establish connection to database. '''
def connect_to_db(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def create_urls_table(conn):
    urls_sql = '''
        CREATE TABLE IF NOT EXISTS urls (
            id integer PRIMARY KEY,
            url text NOT NULL UNIQUE)
        '''
    c = conn.cursor()
    c.execute(urls_sql)


''' Record `url` to database. '''
def record_url(conn, url):
    record_sql = '''
        INSERT INTO urls (url)
        VALUES (?)
    '''
    c = conn.cursor()
    try:
        c.execute(record_sql, (url,))
    except sqlite3.IntegrityError as e:
        logging.exception('URL already tweeted!', e)
    conn.commit()


''' Check if `url` already exists in database. '''
def is_duplicate(conn, url):
    dupl_check_sql = '''
        SELECT url FROM urls WHERE url=?
    '''
    c = conn.cursor()
    c.execute(dupl_check_sql, (url,))
    return c.fetchone()


''' Get tweepy API object. '''
def get_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)


def get_random(iterator, k=1):
    '''Get random sample of items in iterator.

    Args:
        iterator: any iterator you want random samples from.
        k: number of samples to return.

    Note:
        Warning log if `k` is less than size of the iterator. Not
        an issue inside this function because max num of iterations
        will be number of items in `iterator`, not `k`, but could be
        one if you expect size of `results` to always equal to `k`.

    Returns:
        results: List of random items from iterator. Number of items
        is `k` or number of items in `iterator` if `k` is larger than
        the total number of items.

    '''
    results = []

    for i, item in enumerate(iterator):
        if i < k:
            results.append(item)
        else:
            s = int(random.random() * i)
            if s < k:
                results[s] = item

    if len(results) < k:
        logging.warning('Size of iterator (%s) is less than k (%s)', len(results), k)

    return results


def scrape_urls(src_url):
    '''Scrape jpg urls.

    Args:
        src_url: URL to scrape.

    Raises:
        Any typical Requests exceptions.

    Yields:
        Parsed url results in string format.

    '''
    # Exceptions raised here if connection issue arises
    r = requests.get(src_url)
    r.raise_for_status()

    data = r.json().get('Paintings')

    if data is not None:
        for obj in data:
            yield obj.get('image', '')
    else:
        yield ''


''' Download file. '''
def dl_file(url):
    filename = 'temp.jpg'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open (filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return filename


''' Remove files. '''
def _cleanup_files(*files):
    for file in files:
        try:
            os.remove(file)
        except IOError:
            logging.exception('Failed to remove %s', file)


''' Create thumbnail version of an image. '''
def create_thumbnail(original):
    # Based on Twitter recommendation.
    size = 1280, 1280

    thumbnail = original + '.thumbnail.jpg'

    try:
        im = Image.open(original)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(thumbnail, 'JPEG')

        return thumbnail
    except IOError:
        logging.exception('Failed to create thumbnail for %s', original)


''' Tweet image preview along with url. '''
def tweet_image(url):
    api = get_api()

    original = dl_file(url)
    thumbnail = create_thumbnail(original)

    api.update_with_media(thumbnail, status=url)

    _cleanup_files(original, thumbnail)

'''
Todo:
1. Prevent retweets
2. Include description of image?

'''

def main():
    conn = connect_to_db(DB_FILENAME)

    with conn:
        try:
            # Initialize database
            create_urls_table(conn)

            # Retrieve random hi-res image.
            logging.info('Searching for image...')

            # Skip duplicates
            url = get_random(scrape_urls(SRC_URL))[0]
            while is_duplicate(conn, url):
                url = get_random(scrape_urls(SRC_URL))[0]

            # Tweet it
            tweet_image(url)
            logging.info('Tweeted %s', url)

            # Record url
            record_url(conn, url)

        except Exception as e:
            logging.exception('Something went wrong.', e)
            sys.exit(1)

if __name__ == '__main__':
    main()
