"""
    io.py
    ~~~~~~~~~

    Image file-related processing.

"""
import logging
from PIL import Image
import requests
from io import BytesIO


logger = logging.getLogger(__name__)


def dl_image(url):
    """Download file from `url` as a jpeg.

    Args:
        url (`str`): URL path to image file

    Raises:
        Any exceptions from requests library.

    Returns:
        `BytesIO` file object of downloaded image

    """
    r = requests.get(url)

    r.raise_for_status()
    return BytesIO(r.content)


def create_thumbnail(original):
    """Create thumbnail version of an image.

    Args:
        original (:obj:`BytesIO`): original jpeg image buffer

    Returns:
        (:obj:`BytesIO`): resized jpeg

    """

    # Based on Twitter recommendation.
    size = 1280, 1280

    try:
        thumbnail = BytesIO()
        thumbnail.name = 'thumbnail.jpg'

        im = Image.open(original)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(thumbnail, 'JPEG')
        thumbnail.seek(0)

        return thumbnail

    except Exception:
        logger.error('Failed to create thumbnail for %s', original)
        raise


def cleanup(*files):
    """Clear file buffers.

    Args:
        *files (:obj: of :obj:`BytesIO`): buffers to close

    """
    try:
        for file in files:
            file.close()
    except AttributeError:
        logger.error('Failed to clear file buffers.')
        raise
