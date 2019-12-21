from .base import *

SECRET_KEY = '<SECRET_KEY>'

# shows verbose error messages
DEBUG = True

# TODO when developing on your local machine and you want to use the API in the network, insert your local IP here
ALLOWED_HOSTS += []

SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
