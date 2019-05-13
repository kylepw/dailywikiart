========================
dailywikiart Twitter Bot
========================

*dailywikiart* is a simple Twitter bot that tweets random high-resolution
works of art from wikiart's API. Each tweet includes a thumbnail, description
of the work, and a link to the original image.

See it in the wild: `@dailywikiart`__

__ https://twitter.com/dailywikiart

Features
--------
- Randomized selection of high resolution art images.
- Sqlite3 database ensures that an image is never tweeted more than once.

Requirements
------------
- Python 3.6+

Installation
------------
::

    $ git clone git@github.com:kylepw/dailywikiart.git && cd dailywikiart
    $ python -m venv venv && source venv/bin/activate
    (venv) $ pip install -r requirements.txt

Setup
-----

- `Create a Twitter application`__ with the Twitter account you wish to use with the bot. Make sure you set `Read and Write access` and jot down these values: `consumer key`, `consumer secret`, `access token`, and `access token secret`.

__ https://iag.me/socialmedia/how-to-create-a-twitter-app-in-8-easy-steps/

- Set the required environment variables as follows:

    `API_KEY`
        Your application's consumer key.
    `API_SECRET`
        Your application's secret key.
    `ACCESS_TOKEN`
        Your access token.
    `ACCESS_SECRET`
        Your access token secret.

    You can use `python-dotenv`__, `pipenv`__, `virtualenv or bash`__ to set the environment variables.

    One way to do it (replacing ``XXX``'s with your values): ::

    $ echo -e "API_KEY=XXX\nAPI_SECRET=XXX\nACCESS_TOKEN=XXX\nACCESS_SECRET=XXX" >> .env
    $ set -a; source .env; set +a

__ https://preslav.me/2019/01/09/dotenv-files-python/
__ https://pipenv.readthedocs.io/en/latest/advanced/#automatic-loading-of-env
__ https://medium.com/@gitudaniel/the-environment-variables-pattern-be73e6e0e5b7


Usage
-----
::

    (venv) $ # Make sure your virtual environment is active first.
    (venv) $ python bot.py

or to view logs: ::

    (venv) $ LOGLEVEL=info python bot.py

Scheduling
----------

You could run this bot at a set time using any scheduler such as `crontab`__, `systemd`__, or `launchd`__. But a dedicated server is highly recommended.

Note: the server must offer a persistent file system so that the database file is not erased (i.e. not `heroku`). `PythonAnywhere`__ or `AWS`__ are solid choices.

__ https://www.adminschoice.com/crontab-quick-reference
__ https://www.freedesktop.org/wiki/Software/systemd/
__ https://www.google.com/search?q=launchd&ie=utf-8&oe=utf-8&aq=t
__ https://www.pythonanywhere.com/
__ https://aws.amazon.com/

License
-------
`MIT License <https://github.com/kylepw/twitterpeel/blob/master/LICENSE>`_
