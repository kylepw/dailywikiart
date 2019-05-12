'''

db.py
~~~~~

Sqlite3 database wrapper for tweeted data.

The database stores the following information (in str format) on wikiart images
that the bot tweets: `url`, `artist`, `title`, `year`. The database is used to
make sure the bot does not tweet the same image more than once.


'''

import logging
import sqlite3


logger = logging.getLogger(__name__)


class TweetDatabase():
    '''Configure and establish connection to tweet database.

    Note:
        This class acts as a context manager.

    Args:
        db_filename (`str`, optional): filename of database

    '''

    def __init__(self, db_filename='tweets.db'):
        self.db_filename = db_filename


    def __enter__(self):
        self._connect()
        self._create_table()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        if self.conn:
            self.conn.commit()
            self.conn.close()


    def _connect(self):
        '''Connect to database. '''
        try:
            self.conn = sqlite3.connect(self.db_filename)
        except sqlite3.Error:
            logger.exception('Failed to connect to database!')


    def _create_table(self, name='paintings'):
        '''Create a table for image data if it does not exist.

        Args:
            name (`str`, optional): name of table

        '''
        paintings_sql = '''
            CREATE TABLE IF NOT EXISTS {} (
                id integer PRIMARY KEY,
                url text NOT NULL UNIQUE,
                artist text,
                title text,
                year text)
            '''.format(name)

        self.conn.execute(paintings_sql)


    def add(self, data):
        '''Add image data to database.

        Args:
            data (:obj:`dict` [`url`, `artist`, `title`, `year`]): image data

        Raises:
            sqlite3.IntegrityError: If data already exists in database.

        '''
        record_sql = '''
            INSERT INTO paintings (url, artist, title, year)
            VALUES (?, ?, ?, ?)
        '''
        try:
            with self.conn:
                self.conn.execute(record_sql, (
                    data['url'],
                    data['artist'],
                    data['title'],
                    data['year']
                    )
                )
        except sqlite3.IntegrityError:
            logger.exception('Already tweeted %s!', data['url'])


    def is_duplicate(self, url):
        '''Check if `url` already exists in database.

        Args:
            url(`str`): url of image

        '''
        dupl_check_sql = '''
            SELECT url FROM paintings WHERE url=?
        '''
        with self.conn:
            return self.conn.execute(dupl_check_sql, (url,)).fetchone()