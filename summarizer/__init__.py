"""
Summarizer initialization.
"""
import config, database, redis, summary, aggregator

## Database
database.config.sqlalchemy_url = config.sqlalchemy_url
database.config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)

## Summary
summary.config.USER_AGENT = config.SUMMARY_USER_AGENT
summary.config.ADBLOCK_EASYLIST_URL = config.SUMMARY_ADBLOCK_EASYLIST_URL
summary.config.ADBLOCK_EXTRALIST_URL = config.SUMMARY_ADBLOCK_EXTRALIST_URL

## Aggregator
# aggregator.config.sqlalchemy_url = config.sqlalchemy_url
# aggregator.config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
# aggregator.config.REDIS_HOST = config.AGGREGATOR_REDIS_HOST
# aggregator.config.REDIS_PORT = config.AGGREGATOR_REDIS_PORT
# aggregator.config.REDIS_DB = config.AGGREGATOR_REDIS_DB
# aggregator.config.BASE_UXTIME = config.AGGREGATOR_BASE_UXTIME
aggregator.load_config(config) # delayed init
