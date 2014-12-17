"""
Config settings for summarizer app.
"""

## SQLAlchemy
## http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# SQLALCHEMY_ECHO = sqlalchemy_echo = True
SQLALCHEMY_DATABASE_URI = sqlalchemy_url = 'postgresql://svven@localhost/svven'

## Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
# REDIS_DB = 0

## Queues
QUEUES = (SUMMARIZER_QUEUE, ) = ("summarizer", )

## Summary
# SUMMARY_USER_AGENT = 'summary-extraction 0.2'
SUMMARY_ADBLOCK_EASYLIST_URL = 'easylist.txt' #\
	# 'https://easylist-downloads.adblockplus.org/easylist.txt'
SUMMARY_ADBLOCK_EXTRALIST_URL = 'extralist.txt' #\
	# 'https://dl.dropboxusercontent.com/u/134594/svven/extralist.txt'