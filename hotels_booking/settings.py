# import os
# from pathlib import Path
# import dj_database_url
# from decouple import config
# import cloudinary
# import cloudinary.api
# from cloudinary_storage.storage import RawMediaCloudinaryStorage
 # # Your existing CLOUDINARY_STORAGE configuration
# CLOUDINARY_STORAGE = {
#     'CLOUD_NAME': 'dwx1bznpt',
#     'API_KEY': '338398261551869',
#     'API_SECRET': 'pOkhHikI8cdt4NDAlWeSOt5qVVI',
#     'SECURE_URLS': True,
# }
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
 # # Initialize Cloudinary with your configuration
# cloudinary.config(
#     cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
#     api_key=CLOUDINARY_STORAGE['API_KEY'],
#     api_secret=CLOUDINARY_STORAGE['API_SECRET'],
# )
 # # Static and media file configurations
# MEDIA_URL = 'https://res.cloudinary.com/dwx1bznpt/'
 # BASE_DIR = Path(__file__).resolve().parent.parent
 # SECRET_KEY = '9q=3tig&^s7zoq@16ir2hz-q$+af^9tqy7=v^_b&i!uf0q8$%i'
 # # Use ON_HEROKU variable to determine the environment
# ON_HEROKU = config('ON_HEROKU', default=False, cast=bool)
 # # Set DEBUG based on the environment
# DEBUG = not ON_HEROKU  # True if local, False if on Heroku
 # ALLOWED_HOSTS = [
#     'mysterious-tundra-89304-deptes-8a08ec3a2b87.herokuapp.com',
#     'localhost',
#     '127.0.0.1',
# ]
 # INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'django.contrib.auth',
#     'multiupload',
#     'cloudinary_storage',
#     'cloudinary',
#     'hotel_your_choice',
# ]
 # MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
# ]
 # ROOT_URLCONF = 'hotels_booking.urls'
 # TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]
 # # Database configuration
# if ON_HEROKU:
#     DATABASE_URL = 'postgresql://hlrhzayn:uoZO905t2N8tM93SJQw8Jrcl2INj1lmk@horton.db.elephantsql.com/hlrhzayn'
# else:
#     DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
 # DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
 # # Other settings (Email, Static files, etc.) remain unchanged
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'hotel_your_choice/static')]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
 # LOGIN_URL = 'login'
# AUTH_USER_MODEL = 'hotel_your_choice.CustomUser'
 # AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     # other backends if needed
# ]
 # MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
import os
from pathlib import Path import dj_database_url
from decouple import config
from django.db import DatabaseError BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) ON_HEROKU = config('ON_HEROKU', default=False, cast=bool) SECRET_KEY = '9q=3tig&^s7zoq@16ir2hz-q$+af^9tqy7=v^_b&i!uf0q8$%i' # Set DEBUG based on the environment
DEBUG = not ON_HEROKU # True if local, False if on Heroku
 ALLOWED_HOSTS = [
    'mysterious-tundra-89304-deptes-8a08ec3a2b87.herokuapp.com',
    '.localhost',
    '127.0.0.1'
] INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'multiupload',
    'storages',
    'hotel_your_choice.apps.YourAppConfig',

] MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
] ROOT_URLCONF = 'hotels_booking.urls' TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
                                       'APP_DIRS': True,
                                                   'OPTIONS': { 'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ], }, }, ] # Update the existing DATABASES configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',  # Change this based on your database
#         'NAME': BASE_DIR / "db.sqlite3",
#     }
# }
 # DATABASES = {
#    'default': dj_database_url.config(
#        default=os.environ.get('postgres://hlrhzayn:uoZO905t2N8tM93SJQw8Jrcl2INj1lmk@horton.db.elephantsql.com/hlrhzayn')
#    )
# }
 # DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'hlrhzayn',
#         'PASSWORD': 'uoZO905t2N8tM93SJQw8Jrcl2INj1lmk',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
 -- ON_HEROKU = os.environ.get('ON_HEROKU')
-- HEROKU_SERVER = os.environ.get('HEROKU_SERVER')
 -- if ON_HEROKU:
--     DATABASE_URL = 'postgresql://hlrhzayn:uoZO905t2N8tM93SJQw8Jrcl2INj1lmk@horton.db.elephantsql.com/hlrhzayn'
-- else:
--     DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
 -- DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
 ON_HEROKU = os.environ.get('ON_HEROKU') HEROKU_SERVER = os.environ.get('HEROKU_SERVER') if ON_HEROKU:
    DATABASE_URL = 'postgres://hlrhzayn:ONeyuDV91QpQjURHFU2uVG-h8NeXJbAQ@horton.db.elephantsql.com/hlrhzayn'
else:
    DATABASE_URL = 'postgres://hlrhzayn:ONeyuDV91QpQjURHFU2uVG-h8NeXJbAQ@horton.db.elephantsql.com/hlrhzayn'

DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Other settings (Email, Static files, etc.) remain unchanged
 STATIC_URL = '/static/' STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'hotel_your_choice/static'),
] STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Change the login URL to use the default Django login URL
LOGIN_URL = 'login' # Use the default Django login URL
 AUTH_USER_MODEL = 'hotel_your_choice.CustomUser' MEDIA_URL = '/media/' MEDIA_ROOT = os.path.join(BASE_DIR, 'media') AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # other backends if needed
] MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'