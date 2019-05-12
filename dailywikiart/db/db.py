'''

db.py
~~~~~

Sqlite3 database wrapper for tweet data.

'''

import logging
import sqlite3


logger = logging.getLogger(__name__)


class TweetsDatabase():

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


if __name__ == '__main__':
    data1 = {}
    data1['url'] = 'http://hey'
    data1['artist'] = 'goh'
    data1['title'] = 'title'
    data1['year'] = '1999'

    data2 = {}
    data2['url'] = 'http://jeezus'
    data2['artist'] = 'da vinci'
    data2['title'] = 'another title'
    data2['year'] = '1897'

    data3 = {}
    data3['url'] = 'http://jeezus.rocks'
    data3['artist'] = 'da ho'
    data3['title'] = 'hello'
    data3['year'] = '1037'

    with TweetedDB(':memory:') as t:

        t.add(data1)
        t.add(data2)

        assert t.is_duplicate(data1['url'])
        assert t.is_duplicate(data2['url'])
        assert not t.is_duplicate(data3['url'])
