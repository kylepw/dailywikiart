'''

Sqlite3 database wrapper for tweeted data.

'''

import logging
import sqlite3


logging.getLogger(__name__).addHandler(logging.NullHandler())


class Tweeted():

    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename)
        self.create_table()


    def create_table(self):
        paintings_sql = '''
            CREATE TABLE IF NOT EXISTS paintings (
                id integer PRIMARY KEY,
                url text NOT NULL UNIQUE,
                artist text,
                title text,
                year text)
            '''
        with self.conn:
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
            logging.exception('Already tweeted %s!', data['url'])


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

    t = Tweeted(':memory:')

    t.add(data1)
    t.add(data2)

    assert t.is_duplicate(data1['url'])
    assert t.is_duplicate(data2['url'])
    assert not t.is_duplicate(data3['url'])
