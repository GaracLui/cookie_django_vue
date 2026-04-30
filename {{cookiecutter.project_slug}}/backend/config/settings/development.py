from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'backend', '0.0.0.0']

# Override static files for development
STATICFILES_DIRS = [BASE_DIR / 'static']