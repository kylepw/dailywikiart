'''

db.py
~~~~~

Sqlite3 database wrapper for tweet data.

'''

import logging
import sqlite3


logger = logging.getLogger(__name__)


class TweetDatabase():

    def __init__(self, db_filename='tweets.db'):
        self.db_filename = db_filename


    def __enter__(self):
        ''' Run when called as context manager. '''
        self._connect()
        self._create_table()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        if self.conn:
            self.conn.commit()
            self.conn.close()


    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_filename)
        except sqlite3.Error:
            logger.exception('Failed to connect to database!')


    def _create_table(self, name='paintings'):
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
        ''' Add image data to database. '''

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
        ''' Check if `url` already exists in database. '''
        dupl_check_sql = '''
            SELECT url FROM paintings WHERE url=?
        '''
        with self.conn:
            return self.conn.execute(dupl_check_sql, (url,)).fetchone()