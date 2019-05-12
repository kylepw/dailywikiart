'''

io.py
~~~~~~~~~

Process image files.

'''
import logging
import os
import os.path
from PIL import Image
import requests


logger = logging.getLogger(__name__)


def dl_image(url):
    ''' Download file. '''
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'original.jpg')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open (filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return filename


def create_thumbnail(original):
    ''' Create thumbnail version of an image. '''

    # Based on Twitter recommendation.
    size = 1280, 1280

    thumbnail = os.path.join(os.path.dirname(original), 'temp_small.jpg')

    try:
        im = Image.open(original)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(thumbnail, 'JPEG')

        return thumbnail
    except OSError:
        logger.exception('Failed to create thumbnail for %s', original)


def cleanup(*files):
    ''' Remove files. '''
    for file in files:
        try:
            os.remove(file)
        except OSError:
            logger.exception('Failed to remove %s', file)