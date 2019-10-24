"""

    twitter.py
    ~~~~~~~~~~

    Twitter API-related classes and functions.

"""

import logging
import os
import tweepy
from utils.io import dl_image, create_thumbnail, cleanup


logger = logging.getLogger(__name__)


class TwitterAPI:
    """Connect and talk to Twitter API."""

    def __init__(self):
        self.api = self._get_api()

    def _get_api(
        self,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_secret=None,
    ):
        """Connect to Twitter API.

        Args:
            consumer_key (str, optional): key to authorize application
            consumer_secret (str, optional): secret to authorize application
            access_token (str, optional): token to access Twitter resources
            access_secret (str, optional): secret to access Twitter resources

        Returns:
            api(:obj:): Twitter API wrapper

        """
        consumer_key = consumer_key or os.getenv('CONSUMER_KEY')
        consumer_secret = consumer_secret or os.getenv('CONSUMER_SECRET')
        access_token = access_token or os.getenv('ACCESS_TOKEN')
        access_secret = access_secret or os.getenv('ACCESS_SECRET')

        if not all([consumer_key, consumer_secret, access_token, access_secret]):
            raise ValueError('Some or all tweepy OAuth values missing!')

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
        return api

    def _clean_str(self, s):
        """Make string Twitter hashtag-friendly"""
        if not isinstance(s, str):
            return
        if not s:
            return s

        NUM = {
            '0': 'zero',
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
        }
        if not s[0].isalpha():
            # Replace starting number character
            s_edit = list(s)
            s_edit[0] = NUM.get(s_edit[0], 'x')
            s = ''.join(s_edit)
        return ''.join(c for c in s if c.isalnum()).lower()

    def tweet_image(self, data):
        """Tweet description of image along with thumbnail.

        Args:
            data (:obj:`dict` [`title`, `year`, `artist`, `url`]): Image data.

        Returns: None

        """

        tags = f"#wikiart #{self._clean_str(data['artist'])}"
        msg = f"{data['title']} ({data['year']}) by {data['artist']}\n{data['url']} {tags}"

        original = dl_image(data['url'])
        thumbnail = create_thumbnail(original)

        img = self.api.media_upload(filename=thumbnail.name, file=thumbnail)
        self.api.update_status(status=msg, media_ids=[img.media_id])

        cleanup(original, thumbnail)

    def follow_new(self):
        """Follow new followers"""
        followers = self.api.followers_ids()
        following = self.api.friends_ids()

        new_followers = [f for f in followers if f not in following]

        for f in new_followers:
            try:
                self.api.create_friendship(f)
            except tweepy.error.TweepError as e:
                err = str(e)
                # Ignore follow request errors
                if "'code': 160" in err or "'code': 161" in err:
                    continue
