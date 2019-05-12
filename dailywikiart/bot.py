'''
    bot.py
    ~~~~~~

    Twitter bot that tweets a random image from Wikiart's Hi-Res archive.

'''

import logging
import os
import time
import tweepy

from db import TweetDatabase
from twitter import TwitterAPI
from utils.data import get_random, scrape_images


# Source of hi-res images. Confirmed that pages 0~11 unique pages exist.
SRC_URL = 'https://www.wikiart.org/?json=2&layout=new&param=high_resolution&layout=new&page={}'


# If only duplicate images returned, wait before trying next page of json data.
DUPLICATE_TIMEOUT = 3


logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    '''Run Twitter bot.

    Note:
        Checks pulled data against Sqlite3 database to prevent duplicate
        tweets. After some time, the next page of json data will be used
        to pull new data.

    Exceptions:
        All exceptions are logged with stack trace.

    '''
    # Start at first page of json data.
    json_page = 1

    try:
        with TweetDatabase() as db:

            # Connect to Twitter API.
            api = TwitterAPI()

            # Retrieve random hi-res image.
            logger.info('Searching for image...')

            # Skip duplicates
            img_data = get_random(scrape_images(SRC_URL.format(json_page)))[0]
            start = time.time()
            while db.is_duplicate(img_data['url']):

                logger.warning('Duplicate!')
                img_data = get_random(scrape_images(SRC_URL.format(json_page)))[0]

                if time.time() - start > DUPLICATE_TIMEOUT:
                    # Try next page of data.
                    json_page += 1
                    logger.info('Trying next page %s', json_page)
                    start = time.time()

            logger.info('Start tweeting image...')

            # Tweet image data
            api.tweet_image(img_data)

            logger.info('Tweeted %s', img_data)

            # Add record of tweet to database
            db.add(img_data)

    except Exception:
        logger.exception('Something went wrong.')


if __name__ == '__main__':
    main()
