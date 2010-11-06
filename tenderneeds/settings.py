import os

# 'project' refers to the name of the module created with django-admin.py
ROOT_URLCONF = 'tenderneeds.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

INSTALLED_APPS = (
#    'django.contrib.auth',
    'django.contrib.contenttypes',
#    'django.contrib.sessions',
    'django.contrib.sites',
)

ROOT_PATH = os.path.dirname(__file__)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".  Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT_PATH + '/templates',
)
