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


DB_FILENAME = 'tweeted.db'


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')


''' Establish connection to database. '''
def connect_to_db(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def create_paintings_table(conn):
    paintings_sql = '''
        CREATE TABLE IF NOT EXISTS paintings (
            id integer PRIMARY KEY,
            url text NOT NULL UNIQUE,
            artist text,
            title text,
            year text)
        '''
    c = conn.cursor()
    c.execute(paintings_sql)


''' Record image data to database. '''
def record_img(conn, data):
    record_sql = '''
        INSERT INTO paintings (url, artist, title, year)
        VALUES (?, ?, ?, ?)
    '''
    c = conn.cursor()
    try:
        c.execute(record_sql, (
            data['url'],
            data['artist'],
            data['title'],
            data['year']
            )
        )
    except sqlite3.IntegrityError:
        logging.exception('URL already tweeted!')
    conn.commit()


''' Check if `url` already exists in database. '''
def is_duplicate(conn, url):
    dupl_check_sql = '''
        SELECT url FROM paintings WHERE url=?
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


def scrape_images(src_url):
    '''Scrape image urls, titles, and authors.

    Args:
        src_url: URL to scrape.

    Raises:
        Any typical Requests exceptions.

    Yields:
        Parsed url results in dicationary format.

    '''
    # Exceptions raised here if connection issue arises
    r = requests.get(src_url)
    r.raise_for_status()

    data = r.json().get('Paintings')

    if data is not None:
        for obj in data:
            img = {}
            img['url'] = obj.get('image', '')
            img['artist'] = obj.get('artistName', '')
            img['title'] = obj.get('title', '')
            img['year'] = obj.get('year', '')
            yield img
    else:
        yield ''


''' Download file. '''
def dl_file(url):
    filename = 'temp.jpg'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open (filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
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
def tweet_image(data):
    api = get_api()

    msg = f"{data['title']} ({data['year']}) by {data['artist']}\n{data['url']}"

    logging.info('Download image...')
    original = dl_file(data['url'])
    logging.info('Create thumbnail...')
    thumbnail = create_thumbnail(original)

    logging.info('Tweet it...')
    api.update_with_media(thumbnail, status=msg)

    logging.info('Clean up files...')
    _cleanup_files(original, thumbnail)


def main():
    conn = connect_to_db(DB_FILENAME)

    with conn:
        try:
            # Initialize database
            create_paintings_table(conn)

            # Retrieve random hi-res image.
            logging.info('Searching for image...')

            # Skip duplicates
            img_data = get_random(scrape_images(SRC_URL))[0]
            while is_duplicate(conn, img_data['url']):
                logging.info('Duplicate found.')
                img_data = get_random(scrape_images(SRC_URL))[0]

            # Tweet it
            logging.info('Start tweeting image...')
            tweet_image(img_data)
            logging.info('Tweeted %s', img_data)

            # Record url
            record_img(conn, img_data)

        except Exception:
            logging.exception('Something went wrong.')
            sys.exit(1)

if __name__ == '__main__':
    main()
