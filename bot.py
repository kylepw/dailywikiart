"""
    bot.py
    ~~~~~~

    Twitter bot that tweets a random image from Wikiart's Hi-Res archive.

"""

import logging
import os

from db import TweetDatabase
from twitter import TwitterAPI
from utils.data import get_data


logging.basicConfig(
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    level=os.environ.get('LOGLEVEL', 'WARNING').upper(),
)
logger = logging.getLogger(__name__)


def main():
    """Execute Twitter bot.

    Note:
        Checks pulled data against Sqlite3 database to prevent duplicate
        tweets. After some time, the next page of json data will be used
        to pull new data.
    Exceptions:
        All exceptions are logged with stack trace.

    """
    try:
        with TweetDatabase() as db:

            # Connect to Twitter API.
            api = TwitterAPI()

            # Get data.
            img_data = get_data(db)

            # Tweet it.
            api.tweet_image(img_data)
            logger.info('Tweeted %s', img_data)

            # Add record of tweet to database
            db.add(img_data)

    except Exception:
        logger.exception('Something went wrong.')


if __name__ == '__main__':
    main()
