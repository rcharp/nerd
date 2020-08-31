from datetime import timedelta
import os
from celery.schedules import crontab

PRODUCTION = os.environ.get('PRODUCTION', None)

SERVER_NAME = os.environ.get('SERVER_NAME', None)
SITE_NAME = os.environ.get('SITE_NAME', None)
REMEMBER_COOKIE_DOMAIN = os.environ.get('REMEMBER_COOKIE_DOMAIN', None)
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)

DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = os.environ.get('SECRET_KEY', None)
CRYPTO_KEY = os.environ.get('CRYPTO_KEY', None)
PASSWORD = os.environ.get('PASSWORD', None)

# Cache
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', None)
CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
CACHE_DEFAULT_TIMEOUT = os.environ.get('DEFAULT_TIMEOUT', None)
CACHE_REDIS_PORT = os.environ.get('REDIS_PORT', None)
CACHE_REDIS_URL = os.environ.get('REDIS_URL', None)

# Celery Heartbeat.
BROKER_HEARTBEAT = 10
BROKER_HEARTBEAT_CHECKRATE = 2

# Celery.
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL', None)
REDIS_URL = os.environ.get('REDIS_URL', None)
REDBEAT_REDIS_URL = os.environ.get('REDIS_URL', None)

CELERY_BROKER_URL = os.environ.get('REDIS_URL', None)
CELERY_BROKER_HEARTBEAT = 10
CELERY_BROKER_HEARTBEAT_CHECKRATE = 2
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', None)
CELERY_REDIS_URL = os.environ.get('REDIS_URL', None)
CELERY_REDIS_HOST = os.environ.get('REDIS_HOST', None)
CELERY_REDIS_PORT = os.environ.get('REDIS_PORT', None)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_EXPIRES = 300
CELERY_REDIS_MAX_CONNECTIONS = 20
CELERY_TASK_FREQUENCY = 2  # How often (in minutes) to run this task
CELERYBEAT_SCHEDULE = {
}

# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = os.environ.get('NERDWALLET_DATABASE_URL', None)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_ADMIN_EMAIL = os.environ.get('SEED_ADMIN_EMAIL', None)
SEED_ADMIN_PASSWORD = os.environ.get('SEED_ADMIN_PASSWORD', None)
SEED_MEMBER_EMAIL = ''
REMEMBER_COOKIE_DURATION = timedelta(days=90)