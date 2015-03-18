"""
Config settings for summarizer app.
"""
import os

## SQLAlchemy
## http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# SQLALCHEMY_ECHO = sqlalchemy_echo = True
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
SQLALCHEMY_DATABASE_URI = sqlalchemy_url = 'postgresql://svven@%s/svven' % DATABASE_HOST

## RQ (Redis Queue)
RQ_REDIS_HOST = os.environ.get('RQ_REDIS_HOST', 'localhost')
RQ_REDIS_PORT = 6379
RQ_REDIS_DB = 0
QUEUES = (SUMMARIZER_QUEUE, ) = ("summarizer", )

## Summary
SUMMARY_USER_AGENT = 'Svven-Summarizer'
SUMMARY_ADBLOCK_EASYLIST_URL = 'easylist.txt' # offline
  # 'https://easylist-downloads.adblockplus.org/easylist.txt' #
SUMMARY_ADBLOCK_EXTRALIST_URL = 'extralist.txt' # offline
  # 'https://dl.dropboxusercontent.com/u/134594/svven/extralist.txt' #
SUMMARY_PHANTOMJS_BIN = '/usr/local/bin/phantomjs'

## Aggregator
AGGREGATOR_REDIS_HOST = os.environ.get('AGGREGATOR_REDIS_HOST', 'localhost')
AGGREGATOR_REDIS_PORT = 6379
AGGREGATOR_REDIS_DB = 1

AGGREGATOR_BASE_UXTIME = 1420070400 # datetime(2015, 1, 1, 0, 0) # 1

## Sentry
SENTRY_DSN = ''

## Logging
LOGGING = '''
version: 1
disable_existing_loggers: true
root:
    level: INFO
    propagate: true
loggers:
    rq:
        handlers: [console]
        level: INFO
    summary:
        handlers: [console]
        level: INFO
    summarizer:
        handlers: [console, sentry]
        level: DEBUG
handlers:
    console:
        level: DEBUG
        class: logging.StreamHandler
        formatter: console
    sentry:
        level: INFO
        class: raven.handlers.logging.SentryHandler
        dsn: {dsn}
formatters:
    console:
        format: '%(asctime)s %(message)s'
        # format: '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s'
        datefmt: '%H:%M:%S'
'''
LOGGING = LOGGING.format(dsn=SENTRY_DSN)
