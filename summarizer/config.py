"""
Config settings for summarizer app.
"""

## SQLAlchemy
## http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# SQLALCHEMY_ECHO = sqlalchemy_echo = True
SQLALCHEMY_DATABASE_URI = sqlalchemy_url = 'postgresql://svven@localhost/svven'

## RQ (Redis Queue)
RQ_REDIS_HOST = 'localhost'
RQ_REDIS_PORT = 6379
RQ_REDIS_DB = 0
QUEUES = (SUMMARIZER_QUEUE, ) = ("summarizer", )

## Summary
SUMMARY_USER_AGENT = 'Svven-Summarizer'
SUMMARY_ADBLOCK_EASYLIST_URL = 'easylist.txt' # offline
	# 'https://easylist-downloads.adblockplus.org/easylist.txt' #
SUMMARY_ADBLOCK_EXTRALIST_URL = 'extralist.txt' # offline
	# 'https://dl.dropboxusercontent.com/u/134594/svven/extralist.txt' #

## Aggregator
AGGREGATOR_REDIS_HOST = 'localhost'
AGGREGATOR_REDIS_PORT = 6379
AGGREGATOR_REDIS_DB = 1

AGGREGATOR_BASE_UXTIME = 1388534400 # datetime(2014, 1, 1, 0, 0)
