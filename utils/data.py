"""

data.py
~~~~~

Data processing methods.

"""

import logging
import random
import requests


logger = logging.getLogger(__name__)


def get_random(iterator, k=1):
    """Get random sample of items in iterator.

    Args:
        iterator: any iterator you want random samples from.
        k: number of samples to return.

    Note:
        Warning log if `k` is less than size of the iterator. Not
        an issue inside this function because max num of iterations
        will be number of items in `iterator`, not `k`, but could be
        one if you expect size of `results` to always equal to `k`.

    Returns:
        results: List of random items from iterator. Number of items
        is `k` or number of items in `iterator` if `k` is larger than
        the total number of items.

    """
    results = []

    for i, item in enumerate(iterator):
        if i < k:
            results.append(item)
        else:
            s = int(random.random() * i)
            if s < k:
                results[s] = item

    if len(results) < k:
        logger.warning('Iterator size (%s) less than k (%s)', len(results), k)

    return results


def scrape_images(src_url):
    """Scrape image urls, titles, and authors.

    Args:
        src_url (`str`): URL to scrape.

    Raises:
        Any typical Requests exceptions.

    Yields:
        Parsed url results in dictionary format.

    """

    r = requests.get(src_url)
    r.raise_for_status()

    data = r.json().get('Paintings')

    if data is not None:
        for obj in data:
            img = {}
            img['url'] = obj.get('image', '')
            img['artist'] = obj.get('artistName', '')
            img['title'] = obj.get('title', '')
            img['year'] = obj.get('year', '')
            yield img
    else:
        logger.error('No data to scrape at %s', src_url)
