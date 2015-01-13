"""
Summarizer initialization.
"""
import config

import database
db = database.db

# TODO: Make this generic
database.config.sqlalchemy_url = config.sqlalchemy_url
database.config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI


from redis import Redis
r = Redis(config.REDIS_HOST, config.REDIS_PORT)


import summary
# from summary import Summary

# TODO: Make this generic
# summary.config.USER_AGENT = config.SUMMARY_USER_AGENT
# summary.config.ADBLOCK_EASYLIST_URL = config.SUMMARY_ADBLOCK_EASYLIST_URL
# summary.config.ADBLOCK_EXTRALIST_URL = config.SUMMARY_ADBLOCK_EXTRALIST_URL
