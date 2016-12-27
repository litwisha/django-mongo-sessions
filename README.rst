django-mongo-sessions
=====================

:info: mongodb as Django sessions backend

.. image:: https://api.travis-ci.org/hellysmile/django-mongo-sessions.png
    :target: https://travis-ci.org/hellysmile/django-mongo-sessions

features
********

* fast NoSQL Django sessions backend
* invalidation via `TTL <http://docs.mongodb.org/manual/tutorial/expire-data/>`_

installation
------------

run ``pip install django-mongo-sessions``

set ``mongo_sessions.session`` as session engine::

    SESSION_ENGINE = 'mongo_sessions.session'

settings
--------

there are two ways to setup mongodb connection at ``settings.py``


first, if already have mongo connection as ``pymongo.database.Database`` instance::

    import pymongo
    from pymongo import MongoClient
    connection = MongoClient()
    MONGO_CLIENT = connection.your_database
    MONGO_SESSIONS_COLLECTION = 'mongo_sessions' # default option

or as ``pymongo.MongoClient`` instance::

    import pymongo
    from pymongo import MongoClient
    connection = MongoClient()
    MONGO_CLIENT = connection
    MONGO_DB_NAME = 'test'  # default option
    MONGO_SESSIONS_COLLECTION = 'mongo_sessions' # default option



Also, ``MONGO_CLIENT`` setting can be a dotted path string to ``pymongo.MongoClient`` or ``pymongo.database.Database`` instances::

    MONGO_CLIENT = 'project.main.client'  # MongoClient instance
    MONGO_DB_NAME = 'test'  # default option

or::

    MONGO_CLIENT = 'project.main.db'  # pymongo.database.Database instance

second, if you need to connect to mongodb, like::

    MONGO_PORT = 27017
    MONGO_HOST = 'localhost'
    MONGO_DB_NAME = 'test'
    MONGO_DB_USER = False
    MONGO_DB_PASSWORD = False
    MONGO_SESSIONS_COLLECTION = 'mongo_sessions'

    # all this settings are defaults, you can skip any

``expireAfterSeconds`` index value by default is ``SESSION_COOKIE_AGE``
you can change::

    MONGO_SESSIONS_TTL = 60 * 60 # one hour

be sure, that you know what are you doing with it, ``SESSION_COOKIE_AGE``
will get different expiration time

every time you change one of this values, ``expireAfterSeconds`` index
will be dropped and then will be indexed with ``ensureIndex`` again,
be careful here

*it is good way to change expireAfterSeconds only by 1 running instance*

tests
-----

::

    pip install tox
    tox
