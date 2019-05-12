'''
    bot.py
    ~~~~~~

    Twitter bot that tweets a random image from Wikiart's Hi-Res archive.

'''

import logging
import os
import time
import tweepy
import sys

from db import TweetsDatabase
from utils.data import get_random, scrape_images
from utils.io import dl_image, create_thumbnail, cleanup


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


def tweet_image(data):
    ''' Tweet image preview along with url. '''

    api = get_api()

    msg = f"{data['title']} ({data['year']}) by {data['artist']}\n{data['url']}"

    logger.info('Download image...')
    original = dl_image(data['url'])
    logger.info('Create thumbnail...')
    thumbnail = create_thumbnail(original)

    logger.info('Tweet it...')
    api.update_with_media(thumbnail, status=msg)

    logger.info('Clean up files...')
    cleanup(original, thumbnail)


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
                logger.warning('Duplicate found.')
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
