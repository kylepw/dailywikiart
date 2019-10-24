"""
    db.py
    ~~~~~

    MongoDB database wrapper for tweeted data.

    The database stores the following information (in str format) on wikiart images
    that the bot tweets: `url`, `artist`, `title`, `year`. The database is used to
    make sure the bot does not tweet the same image more than once.

"""
import logging
import os
import os.path
import pymongo


logger = logging.getLogger(__name__)


class TweetDatabase:
    """Configure and establish connection to tweet database.

    Note:
        This class acts as a context manager.

    Args:
        uri (`str`, optional): mongodb uri string

    """

    def __init__(self, uri=None):
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017')
        self.client = self.db = self.coll = None

    def __enter__(self):
        self._connect()
        self._create_collection()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.client:
            self.client.close()

    def _connect(self, db_name=None):
        """Connect to database. """
        db_name = db_name or os.getenv('MONGODB_DBNAME', 'tweets')
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[db_name]
        except Exception:
            logger.error(f'Failed to connect to {self.uri}!')
            raise

    def _create_collection(self, coll_name=None):
        """Create a collection for image data if it does not exist.

        Args:
            name (`str`, optional): name of collection

        """
        coll_name = coll_name or 'wikiart'
        if self.db:
            self.coll = self.db[coll_name]

    def add(self, data):
        """Add image data to database.

        Args:
            data (:obj:`dict` [`url`, `artist`, `title`, `year`]): image data

        Raises:
           pymongo.errors.OperationFailure: If index exists with different options.

        """
        if self.coll:
            # Make sure unique index exists
            try:
                self.coll.create_index(
                    [
                        ('artist', pymongo.ASCENDING),
                        ('year', pymongo.ASCENDING),
                        ('title', pymongo.ASCENDING),
                        ('url', pymongo.ASCENDING),
                    ],
                    unique=True,
                )
            except pymongo.errors.OperationFailure:
                logger.error(
                    "Failed to create unique index on collection '%s'", self.coll.name
                )
                raise

            # Add tweet
            try:
                self.coll.insert_one(
                    {
                        'artist': data['artist'],
                        'year': data['year'],
                        'title': data['title'],
                        'url': data['url'],
                    }
                )
            except pymongo.errors.DuplicateKeyError:
                logger.error('Already tweeted %s! Skipping insert.', data['url'])

    def is_duplicate(self, url):
        """Check if `url` already exists in database.

        Args:
            url(`str`): url of image

        Returns:
            A duplicate match (`str`) or None.

        """
        if self.coll:
            return self.coll.find_one({'url': url})
        return False
