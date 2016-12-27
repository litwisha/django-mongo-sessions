from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from pymongo import MongoClient
from pymongo.database import Database

try:
    from django.utils.module_loading import import_string
except ImportError:
    # Django  1.5 <= version <= 1.6
    from django.utils.module_loading import import_by_path as import_string

MONGO_CLIENT = getattr(settings, 'MONGO_CLIENT', False)

MONGO_DB_NAME = getattr(settings, 'MONGO_DB_NAME', 'test')

MONGO_SESSIONS_COLLECTION = getattr(
    settings, 'MONGO_SESSIONS_COLLECTION', 'mongo_sessions'
)

# think twice before change it
# sessionid cookie will get different expiration time
MONGO_SESSIONS_TTL = getattr(
    settings, 'MONGO_SESSIONS_TTL', settings.SESSION_COOKIE_AGE
)

if MONGO_CLIENT:
    if isinstance(MONGO_CLIENT, six.string_types):
        MONGO_CLIENT = import_string(MONGO_CLIENT)

    if isinstance(MONGO_CLIENT, MongoClient):
        MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]

    elif isinstance(MONGO_CLIENT, Database):
        MONGO_DB = MONGO_CLIENT

    else:
        raise ImproperlyConfigured(
            '''
            Incorrect MONGO_CLIENT settings.
            Must be MongoClient or Database instance
            '''
        )
else:
    MONGO_PORT = int(getattr(settings, 'MONGO_PORT', 27017))
    MONGO_HOST = getattr(settings, 'MONGO_HOST', 'localhost')
    MONGO_DB_USER = getattr(settings, 'MONGO_DB_USER', False)
    MONGO_DB_PASSWORD = getattr(settings, 'MONGO_DB_PASSWORD', False)

    MONGO_CLIENT = MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
    )

    MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]

    if MONGO_DB_USER and MONGO_DB_PASSWORD:
        MONGO_DB.authenticate(MONGO_DB_USER, MONGO_DB_PASSWORD)

try:
    MONGO_DB_VERSION = MONGO_DB.connection.server_info()['version']
except TypeError:
    # for pymongo >= 3
    MONGO_DB_VERSION = MONGO_DB.client.server_info()['version']

if not float('.'.join(MONGO_DB_VERSION.split('.')[:-1])) >= 2.2:
    raise ImproperlyConfigured(
        '''
        Your mongodb service doesn't support TTL
        http://docs.mongodb.org/manual/tutorial/expire-data/
        '''
    )

DB_COLLECTION = MONGO_DB[MONGO_SESSIONS_COLLECTION]

MONGO_SESSIONS_INDEXES = DB_COLLECTION.index_information()

# check existing indexes
if len(MONGO_SESSIONS_INDEXES) <= 1:
    DB_COLLECTION.ensure_index(
        'session_key',
        unique=True,
    )

    DB_COLLECTION.ensure_index(
        'creation_date',
        expireAfterSeconds=MONGO_SESSIONS_TTL
    )

    MONGO_SESSIONS_INDEXES = DB_COLLECTION.index_information()

# change creation_date index if, MONGO_SESSIONS_TTL was changed
if int(MONGO_SESSIONS_INDEXES['creation_date_1']['expireAfterSeconds']) \
        != int(MONGO_SESSIONS_TTL):
    DB_COLLECTION.drop_index('creation_date_1')

    DB_COLLECTION.ensure_index(
        'creation_date',
        expireAfterSeconds=MONGO_SESSIONS_TTL,
    )

    MONGO_SESSIONS_INDEXES = DB_COLLECTION.index_information()
