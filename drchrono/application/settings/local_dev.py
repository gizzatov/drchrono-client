from .base import *

DEBUG = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
