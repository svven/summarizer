"""
Summarizer initialization.
"""
import config, database, redis, summary, aggregator

## Database
database.init(config)
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)

## Summary
summary.config.USER_AGENT = config.SUMMARY_USER_AGENT
summary.config.ADBLOCK_EASYLIST_URL = config.SUMMARY_ADBLOCK_EASYLIST_URL
summary.config.ADBLOCK_EXTRALIST_URL = config.SUMMARY_ADBLOCK_EXTRALIST_URL

## Aggregator
aggregator.init(config) # delayed init
