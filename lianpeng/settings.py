#coding: #utf-8
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True 
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    # ("Your Name", "your_email@example.com"),
]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev.db",
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Asia/Shanghai"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "zh-cn"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(PACKAGE_ROOT, "static"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = ""

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "pinax_utils.context_processors.settings",
    "pinax_theme_bootstrap_account.context_processors.theme",
    "account.context_processors.account",
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
]


MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "bookmark.django-crossdomainxhr-middleware.XsSharing",
    'django.middleware.gzip.GZipMiddleware',
    #'pipeline.middleware.MinifyHTMLMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleOAuth2Backend',    
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.contrib.weibo.WeiboBackend',    
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend',
)
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'misc.auth_pipeline.redirect_to_bind_form',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
GITHUB_EXTRA_DATA = [('email', 'email'), ('login', 'login')]

ROOT_URLCONF = "lianpeng.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "lianpeng.wsgi.application"

TEMPLATE_DIRS = [
    os.path.join(PACKAGE_ROOT, "templates"),
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    'fluent_comments',
    "django.contrib.comments",
    
    # theme
    "pinax_theme_bootstrap_account",
    "pinax_theme_bootstrap",
    "django_forms_bootstrap",
    
    # external
    "idios",
    'social_auth',    
    'guardian',
    'agon',
    "account",
    "metron",
    "eventlog",
    'djcelery',
    'djcelery_email',
    'raven.contrib.django.raven_compat',
    'endless_pagination',
    'gravatar',
    'pipeline',
    "tastypie",
    "tagging",
    "notifications",
    "pagination",
    "kaleo",
    "south",
    
    # project
    "misc",
    "lianpeng",
    "bookmark",
    "harvest",
    "profiles",
    "avatar",
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_LOGIN_REDIRECT_URL = "home"
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED_DAYS = 2
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
AUTH_PROFILE_MODULE = 'profiles.Profile'

TASTYPIE_ALLOW_MISSING_SLASH = True

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
import djcelery
from celery.schedules import crontab
djcelery.setup_loader()
BROKER_URL = 'amqp://USERNAME:PASSWORD@localhost:5672/lianpeng'
CELERYBEAT_SCHEDULE = {
    "runs-every-day": {
        "task": "bookmark.tasks.sync",
        "schedule": crontab(minute=0, hour=0),
    },
}

EMAIL_HOST = ''#'localhost'
EMAIL_HOST_PASSWORD = ""
EMAIL_HOST_USER = ""
EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = False

CONTACT_EMAIL = ''
FROM_EMAIL = ''
DEFAULT_FROM_EMAIL = "%s <%s>" % ("lianpeng", FROM_EMAIL)
THEME_ACCOUNT_CONTACT_EMAIL = FROM_EMAIL

#: cross domain request
XS_SHARING_ALLOWED_ORIGINS = "http://bookmarklet.sinaapp.com"
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ["content-type"]

#: third-party locale files
LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'i18n', app, 'locale') for app in os.listdir(os.path.join(PROJECT_ROOT,'i18n'))]

#: compress static files
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'

PIPELINE_CSS = {
    'main': {
        'source_filenames': (
          'css/bootstrap.css',
        ),
        'output_filename': 'css/main.css',
    },
}
PIPELINE_JS = {
    'main': {
        'source_filenames': (
            'js/app_base.js',
            'js/bookmark.js',
            'js/comment.js',
            'js/app.js',
        ),
        'output_filename': 'js/main.js',
    },
    'bookmark_embed': {
        'source_filenames': (
            'js/bookmark_embed.js',
        ),
        'output_filename': 'js/bookmark-embed-min.js',
    },
    'bookmark_detail': {
        'source_filenames': (
            'js/app_base.js',
            'js/comment.js',
            'js/bookmark_detail_init.js',
            'js/bookmark_embed.js',
        ),
        'output_filename': 'js/bookmark-detail-min.js',
    }
}

FLUENT_COMMENTS_EXCLUDE_FIELDS = ('name', 'email', 'url')
COMMENTS_APP = 'fluent_comments'


METRON_SETTINGS = {
    "google": {
        1: "UA-40421394-1", # production
    },
}

ANONYMOUS_USER_ID = -1
WEIBO_CLIENT_KEY = ''
WEIBO_CLIENT_SECRET = ''
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = ''
#NOTIFY_USE_JSONFIELD = True

CACHES = { 
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

KALEO_DEFAULT_INVITE_ALLOCATION = 5
GRAVATAR_DEFAULT_IMAGE = 'mm'

try:
    from local_settings import *
except ImportError:
    pass
