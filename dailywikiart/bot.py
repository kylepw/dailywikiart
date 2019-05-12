'''
    bot.py
    ~~~~~~

    Twitter bot that tweets a random image from Wikiart's Hi-Res archive.

'''

import json
import logging
import os
import os.path
from PIL import Image
import random
import requests
import time
import tweepy
import sys

from db import TweetsDatabase


CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')


# Source of Hi-Res images
SRC_URL = 'https://www.wikiart.org/?json=2&layout=new&param=high_resolution&layout=new&page={}'


# If duplicates, wait before trying next page of json data
DUPLICATE_TIMEOUT = 3


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_api():
    ''' Get tweepy API object. '''
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
        logger.warning('Size of iterator (%s) is less than k (%s)', len(results), k)

    return results


def scrape_images(src_url):
    '''Scrape image urls, titles, and authors.

    Args:
        src_url: URL to scrape.

    Raises:
        Any typical Requests exceptions.

    Yields:
        Parsed url results in dictionary format.

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
        logger.error('No data to scrape at %s', src_url)


def dl_file(url):
    ''' Download file. '''
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.jpg')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open (filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return filename


def _cleanup_files(*files):
    ''' Remove files. '''
    for file in files:
        try:
            os.remove(file)
        except IOError:
            logger.exception('Failed to remove %s', file)


def create_thumbnail(original):
    ''' Create thumbnail version of an image. '''

    # Based on Twitter recommendation.
    size = 1280, 1280

    thumbnail = os.path.join(os.path.dirname(original), 'temp_small.jpg')

    try:
        im = Image.open(original)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(thumbnail, 'JPEG')

        return thumbnail
    except IOError:
        logger.exception('Failed to create thumbnail for %s', original)


def tweet_image(data):
    ''' Tweet image preview along with url. '''

    api = get_api()

    msg = f"{data['title']} ({data['year']}) by {data['artist']}\n{data['url']}"

    logger.info('Download image...')
    original = dl_file(data['url'])
    logger.info('Create thumbnail...')
    thumbnail = create_thumbnail(original)

    logger.info('Tweet it...')
    #api.update_with_media(thumbnail, status=msg)

    logger.info('Clean up files...')
    _cleanup_files(original, thumbnail)


def main():
    json_page = 1

    try:
        with TweetsDatabase() as db:

            # Retrieve random hi-res image.
            logger.info('Searching for image...')

            # Skip duplicates
            img_data = get_random(scrape_images(SRC_URL.format(json_page)))[0]
            start = time.time()
            while db.is_duplicate(img_data['url']):
                logger.info('Duplicate found.')
                img_data = get_random(scrape_images(SRC_URL.format(json_page)))[0]

                # Try next page of data after certain time
                if time.time() - start > DUPLICATE_TIMEOUT:
                    json_page += 1
                    logger.info('trying next page %s', json_page)
                    start = time.time()

            # Tweet it
            logger.info('Start tweeting image...')
            tweet_image(img_data)
            logger.info('Tweeted %s', img_data)

            # Add record of tweet
            db.add(img_data)

    except Exception:
        logger.exception('Something went wrong.')
        sys.exit(1)


if __name__ == '__main__':
    main()
