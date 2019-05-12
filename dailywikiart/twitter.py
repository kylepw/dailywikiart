'''

twitter.py
~~~~~~~~~~

Twitter API-related classes and functions.

'''

import logging
import os
import tweepy
import requests
from utils.io import dl_image, create_thumbnail, cleanup


logger = logging.getLogger(__name__)


# Values required to connect to Twitter API.
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')


class TwitterAPI():
    '''Connect and talk to Twitter API.'''

    def __init__(self):
        self.api = self._get_api()


    def _get_api(self,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_secret=ACCESS_SECRET
    ):
        ''' Connect to Twitter API.

        Args:
            consumer_key (str, optional): key to authorize application
            consumer_secret (str, optional): secret to authorize application
            access_token (str, optional): token to access Twitter resources
            access_secret (str, optional): secret to access Twitter resources

        Returns:
            api(:obj:): Twitter API wrapper

        '''
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
        return api


    def tweet_image(self, data):
        ''' Tweet description of image along with thumbnail.

        Args:
            data (:obj:`dict` [`title`, `year`, `artist`, `url`]): Image data.

        Returns: None

        '''

        msg = f"{data['title']} ({data['year']}) by {data['artist']}\n{data['url']}"

        logger.info('Download image...')
        original = dl_image(data['url'])
        logger.info('Create thumbnail...')
        thumbnail = create_thumbnail(original)

        logger.info('Tweet it...')
        #self.api.update_with_media(thumbnail, status=msg)

        logger.info('Clean up files...')
        cleanup(original, thumbnail)